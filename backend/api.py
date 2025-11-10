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
        "https://doc-rag-conversive-front.onrender.com",  # Production frontend
    ],
    allow_origin_regex=r"https://.*\.onrender\.com",  # Regex pattern for all Render domains
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

def combined_deep_search(query, context_docs):
    """Combine documentation search with web search for comprehensive answer"""
    import time
    start_time = time.time()
    
    # Extract documentation context
    doc_context = ""
    urls = []
    if context_docs:
        context_parts = []
        for doc in context_docs:
            text = doc.metadata.get('text', '')
            title = doc.metadata.get('title', 'Unknown')
            context_parts.append(f"From {title}:\n{text[:500]}...")
            
            # Extract URLs
            found_urls = re.findall(r'https://docs\.beconversive\.com/[^\s\)]+', text)
            urls.extend(found_urls[:2])
        
        doc_context = "\n\n".join(context_parts[:3])  # Top 3 docs
        urls = list(set(urls))[:5]
    
    # Retry logic for API overload
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            # Use Google Search grounding to get web information
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            config = types.GenerateContentConfig(tools=[grounding_tool])
            
            # Build comprehensive prompt
            doc_section = ""
            if doc_context:
                doc_section = f"\n\nRelevant Documentation I Found:\n{doc_context}\n"
            
            url_section = ""
            if urls:
                url_list = "\n".join([f"- {url}" for url in urls])
                url_section = f"\n\nDocumentation Links:\n{url_list}\n"
            
            prompt = f"""You are Convie, an expert SMS Magic assistant providing comprehensive, in-depth guidance.

User Question: "{query}"
{doc_section}{url_section}

Your Task:
I've gathered information from our documentation above. Now, search the web for additional current information, best practices, and any updates. Then synthesize EVERYTHING into one comprehensive, detailed response.

Response Guidelines:

1. Synthesis & Integration:
   - Combine documentation insights with web findings
   - Highlight what's from official docs vs general best practices
   - Fill in any gaps from the documentation with web research
   - Provide a complete, thorough answer

2. Structure & Organization:
   - Start with a warm, confident introduction
   - Break into clear, numbered main steps
   - Use sub-points (a., b., c.) for detailed instructions
   - Use arrows (->) to show flow and relationships
   - Group related information logically

3. Content Depth:
   - Be thorough and detailed - this is a "deep dive"
   - Include specific instructions (where to click, what to enter)
   - Mention prerequisites, requirements, and dependencies
   - Add pro tips, warnings, and best practices
   - Explain the "why" behind steps when helpful
   - Include troubleshooting tips if relevant

4. Formatting:
   - NO asterisks, NO hashtags
   - Clean, readable structure
   - Use line breaks for clarity
   - Keep paragraphs focused and scannable

5. Tone & Quality:
   - Professional, knowledgeable, and authoritative
   - Warm and supportive
   - Confident in the guidance provided
   - Thorough but not overwhelming

Remember: This is a comprehensive "Dive Deeper" response. Be detailed, practical, and complete. The user wants the full picture!"""
            
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config
            )
            
            generation_time = time.time() - start_time
            cleaned_response = clean_markdown(response.text)
            
            return cleaned_response, generation_time, True
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a 503 overload error
            if "503" in error_msg or "overloaded" in error_msg.lower():
                if attempt < max_retries - 1:
                    print(f"Gemini API overloaded, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    return "I apologize, but the AI service is currently experiencing high load. Please try again in a moment.", 0, False
            else:
                # Other errors, don't retry
                return f"I apologize, but I encountered an error during the deep search: {error_msg}", 0, False
    
    return "I apologize, but I couldn't complete the search after multiple attempts. Please try again.", 0, False

def generate_response(query, context_docs, use_web_search=False, dive_deeper=False):
    """Generate AI response"""
    import time
    start_time = time.time()
    
    # Extract URLs and context first
    urls = []
    context_text = []
    if context_docs:
        for doc in context_docs:
            text = doc.metadata.get('text', '')
            context_text.append(f"{doc.metadata.get('title', 'Unknown')}\n{text}")
            found_urls = re.findall(r'https://docs\.beconversive\.com/[^\s\)]+', text)
            urls.extend(found_urls[:2])
    
    urls = list(set(urls))[:10]
    context = "\n\n".join(context_text) if context_text else ""
    
    # Check relevance of documents
    has_good_docs = False
    if context_docs:
        has_good_docs = any(doc.score > 0.75 for doc in context_docs)
    
    # If dive deeper and no good docs, use web search with context
    if dive_deeper and not has_good_docs:
        doc_snippet = context[:500] if context else None
        return web_search_response(query, doc_snippet)
    
    # If web search is explicitly requested or no docs at all
    if use_web_search or not context_docs:
        return web_search_response(query)
    
    # Add memory
    memory_context = ""
    if conversation_memory:
        memory_context = "\nPrevious conversation:\n"
        for mem in conversation_memory[-3:]:
            memory_context += f"User: {mem['query']}\nAssistant: {mem['response'][:150]}...\n\n"
    
    # Build enhanced prompt
    url_section = ""
    if urls:
        url_list = "\n".join([f"- {url}" for url in urls])
        url_section = f"\n\nReference Documentation Links:\n{url_list}\n"
    
    prompt = f"""You are Convie, an expert SMS Magic assistant with comprehensive knowledge of the platform.

{memory_context}
Documentation Context:
{context}{url_section}

User Question: "{query}"

Response Guidelines:

1. Structure & Organization:
   - Start with a brief, friendly acknowledgment
   - Break down complex processes into clear, numbered steps
   - Format: "1. Step Name -> Brief description of what to do"
   - Use sub-points with letters (a., b., c.) for detailed instructions
   - Use arrows (->) to show relationships or progression

2. Content Quality:
   - Be specific and actionable - tell them exactly what to do
   - Include WHERE to find features (e.g., "Navigate to Settings > Campaigns")
   - Mention any prerequisites or requirements upfront
   - Add helpful tips or warnings when relevant
   - Reference the documentation links when appropriate

3. Formatting Rules:
   - NO asterisks for emphasis
   - NO hashtags for headers
   - NO excessive formatting
   - Use simple line breaks for readability
   - Keep it clean and professional

4. Tone & Style:
   - Professional yet warm and approachable
   - Confident and knowledgeable
   - Patient and supportive
   - Focus on helping them succeed

5. Completeness:
   - Answer the full question
   - Anticipate follow-up questions
   - Provide context when needed
   - Be thorough but concise

Remember: You're guiding someone through a real task. Make it easy to follow and implement."""
    
    try:
        # Try to use URL context if available (requires certain API tiers)
        config = None
        if urls:
            try:
                # Attempt to create URL context tool
                from google.genai.types import Tool, UrlContext
                url_context_tool = Tool(url_context=UrlContext())
                config = types.GenerateContentConfig(tools=[url_context_tool])
            except (ImportError, AttributeError):
                # URL context not available, will use URLs in prompt instead
                pass
        
        if config:
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config
            )
        else:
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
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
        
        # Handle dive deeper request - ALWAYS search both docs AND web
        if request.dive_deeper:
            print("Dive Deeper: Searching documentation AND web for comprehensive answer")
            
            # Search docs first
            docs, search_time = search_docs(request.message)
            print(f"Dive Deeper: Found {len(docs)} documents in {search_time:.2f}s")
            
            # Perform combined deep search (docs + web)
            response, gen_time, used_web_search = combined_deep_search(request.message, docs)
            
            # Format sources from docs
            sources = [
                {
                    "title": doc.metadata.get('title', 'Unknown'),
                    "url": doc.metadata.get('filename', ''),
                    "relevance": float(doc.score)
                }
                for doc in docs[:3]
            ] if docs else []
            
            # Generate suggestions
            query_lower = request.message.lower()
            if "campaign" in query_lower:
                related_queries = ["How do I schedule a campaign?", "What are campaign analytics?"]
                suggestions = ["What is the audience manager?", "How do I track performance?"]
            elif "message" in query_lower or "send" in query_lower:
                related_queries = ["How do I personalize messages?", "How do I track delivery?"]
                suggestions = ["How do I create a campaign?", "What is the audience manager?"]
            elif "audience" in query_lower or "contact" in query_lower:
                related_queries = ["How do I import contacts?", "What are audience segments?"]
                suggestions = ["How do I create a campaign?", "How do I track performance?"]
            else:
                related_queries = ["Tell me more about this", "What are best practices?"]
                suggestions = ["How do I create a campaign?", "What is the audience manager?"]
            
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
