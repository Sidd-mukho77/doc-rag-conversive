from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pinecone import Pinecone
from google import genai
from google.genai import types
import numpy as np
import re
from config import PINECONE_API_KEY, GEMINI_API_KEY

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:5174",
        "https://*.onrender.com",  # Allow all Render domains
    ],
    allow_origin_regex=r"https://.*\.onrender\.com",  # Regex pattern for Render domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Validate API keys
if not PINECONE_API_KEY or not GEMINI_API_KEY:
    print("ERROR: API keys not found!")
    print("Please check backend/config.py")
    
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("sms-magic-gemini")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Conversation memory
conversation_memory = []

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"
    dive_deeper: bool = False

class ChatResponse(BaseModel):
    response: str
    sources: list
    suggestions: list
    search_time: float
    generation_time: float
    used_web_search: bool = False
    related_queries: list = []

def get_query_embedding(query):
    """Get embedding for search query"""
    result = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=768
        )
    )
    values = np.array(result.embeddings[0].values)
    normalized = values / np.linalg.norm(values)
    return normalized.tolist()

def search_docs(query, top_k=10):
    """Search for relevant documents"""
    import time
    start_time = time.time()
    
    query_embedding = get_query_embedding(query)
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    search_time = time.time() - start_time
    return results.matches[:5], search_time

def clean_markdown(text):
    """Clean up excessive markdown formatting"""
    # Remove excessive asterisks (bold/italic)
    text = re.sub(r'\*\*\*+', '', text)  # Remove triple or more asterisks
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)  # Remove italic
    
    # Remove excessive hashes (headers)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Clean up extra newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def web_search_response(query):
    """Use Gemini's Google Search grounding for web search"""
    import time
    start_time = time.time()
    
    try:
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])
        
        prompt = f"""You are Convie, a helpful SMS Magic assistant. The user asked: "{query}"

I couldn't find this information in my stored documentation, so I'm searching the web for you.

Please provide a clear, helpful answer based on current web information. Format your response with:
- Clear numbered steps or bullet points
- Simple, professional language
- Practical, actionable information"""
        
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
        
        generation_time = time.time() - start_time
        cleaned_response = clean_markdown(response.text)
        
        return cleaned_response, generation_time, True
    except Exception as e:
        return f"I apologize, but I encountered an error while searching: {str(e)}", 0, False

def generate_response(query, context_docs, use_web_search=False):
    """Generate AI response"""
    import time
    start_time = time.time()
    
    # If web search is requested or no docs found
    if use_web_search or not context_docs:
        return web_search_response(query)
    
    # Extract URLs and context
    urls = []
    context_text = []
    for doc in context_docs:
        text = doc.metadata.get('text', '')
        context_text.append(f"{doc.metadata.get('title', 'Unknown')}\n{text}")
        found_urls = re.findall(r'https://docs\.beconversive\.com/[^\s\)]+', text)
        urls.extend(found_urls[:2])
    
    urls = list(set(urls))[:10]
    context = "\n\n".join(context_text)
    
    # Add memory
    memory_context = ""
    if conversation_memory:
        memory_context = "\nPrevious conversation:\n"
        for mem in conversation_memory[-3:]:
            memory_context += f"User: {mem['query']}\nAssistant: {mem['response'][:150]}...\n\n"
    
    # Build prompt
    if urls:
        url_list = "\n".join([f"- {url}" for url in urls])
        prompt = f"""You are Convie, a helpful and professional SMS Magic assistant.

{memory_context}
Context from documentation:
{context}

Reference links: {url_list}

User asks: {query}

Instructions:
- Provide clear, numbered steps (like "1. Review Campaign Settings -> Start by...")
- Use simple arrows (->) to show progression
- Use sub-points with letters (a., b., c.) for details
- Keep formatting minimal - NO asterisks, NO hashtags
- Be warm and professional
- Keep it organized and easy to read"""
    else:
        prompt = f"""You are Convie, a helpful and professional SMS Magic assistant.

{memory_context}
Context from documentation:
{context}

User asks: {query}

Instructions:
- Provide clear, numbered steps (like "1. Review Campaign Settings -> Start by...")
- Use simple arrows (->) to show progression
- Use sub-points with letters (a., b., c.) for details
- Keep formatting minimal - NO asterisks, NO hashtags
- Be warm and professional
- Keep it organized and easy to read"""
    
    try:
        tools = [types.Tool(url_context=types.UrlContext())]
        config = types.GenerateContentConfig(tools=tools)
        
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
        
        generation_time = time.time() - start_time
        
        # Clean up the response
        cleaned_response = clean_markdown(response.text)
        
        # Generate contextual suggestions based on the query
        query_lower = query.lower()
        
        # Related queries (more specific to current topic)
        related_queries = []
        if "campaign" in query_lower:
            related_queries = [
                "How do I schedule a campaign?",
                "What are campaign analytics?",
            ]
        elif "message" in query_lower or "send" in query_lower:
            related_queries = [
                "How do I personalize messages?",
                "How do I track message delivery?",
            ]
        elif "audience" in query_lower or "contact" in query_lower:
            related_queries = [
                "How do I import contacts?",
                "What are audience segments?",
            ]
        else:
            related_queries = [
                "Tell me more about this feature",
                "What are best practices?",
            ]
        
        # General suggestions (different topics)
        general_suggestions = []
        if "campaign" not in query_lower:
            general_suggestions.append("How do I create a campaign?")
        if "audience" not in query_lower:
            general_suggestions.append("What is the audience manager?")
        if "track" not in query_lower and "analytics" not in query_lower:
            general_suggestions.append("How do I track campaign performance?")
        
        # Combine: related queries + general suggestions
        all_suggestions = related_queries + general_suggestions[:2]
        
        return cleaned_response, generation_time, all_suggestions, False
    except Exception as e:
        return f"Error: {str(e)}", 0, [], False

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        print(f"Received message: {request.message} (dive_deeper: {request.dive_deeper})")
        
        used_web_search = False
        related_queries = []
        
        # If dive deeper is requested, use web search
        if request.dive_deeper:
            response, gen_time, used_web_search = generate_response(
                request.message, 
                None, 
                use_web_search=True
            )
            search_time = 0
            sources = []
            suggestions = [
                "How do I create a campaign?",
                "What is the audience manager?",
                "How do I track campaign performance?"
            ]
        else:
            # Search docs
            docs, search_time = search_docs(request.message)
            print(f"Found {len(docs)} documents in {search_time:.2f}s")
            
            # Check if we have good results (relevance > 0.7)
            has_good_results = any(doc.score > 0.7 for doc in docs) if docs else False
            
            # Generate response
            result = generate_response(request.message, docs, use_web_search=False)
            
            if len(result) == 4:
                response, gen_time, suggestions, used_web_search = result
            else:
                response, gen_time, used_web_search = result
                suggestions = []
            
            print(f"Generated response in {gen_time:.2f}s")
            
            # Format sources
            sources = [
                {
                    "title": doc.metadata.get('title', 'Unknown'),
                    "url": doc.metadata.get('filename', ''),
                    "relevance": float(doc.score)
                }
                for doc in docs[:3]
            ] if docs else []
            
            # Split suggestions into related queries and general suggestions
            if suggestions:
                related_queries = suggestions[:2]  # First 2 are related
                suggestions = suggestions[2:]  # Rest are general
        
        # Update memory
        conversation_memory.append({
            "query": request.message,
            "response": response
        })
        if len(conversation_memory) > 5:
            conversation_memory.pop(0)
        
        return ChatResponse(
            response=response,
            sources=sources,
            suggestions=suggestions,
            search_time=search_time,
            generation_time=gen_time,
            used_web_search=used_web_search,
            related_queries=related_queries
        )
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
