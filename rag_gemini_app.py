import os
import gradio as gr
from pinecone import Pinecone
from dotenv import load_dotenv
import plotly.graph_objects as go
import numpy as np
from google import genai
from google.genai import types
import re

load_dotenv()

# Initialize clients
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("sms-magic-gemini")
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Chat history with conversation memory
chat_history = []
conversation_memory = []  # Stores last 5 Q&A pairs

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
    
    # Normalize
    values = np.array(result.embeddings[0].values)
    normalized = values / np.linalg.norm(values)
    return normalized.tolist()

def search_docs(query, top_k=10):
    """Search for relevant documents with reranking"""
    import time
    start_time = time.time()
    
    # Get more results initially for reranking
    query_embedding = get_query_embedding(query)
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    search_time = time.time() - start_time
    
    # Rerank results using text similarity
    reranked = []
    for match in results.matches:
        # Simple reranking based on text length and score
        text = match.metadata.get('text', '')
        # Boost score if text is substantial
        adjusted_score = match.score * (1 + min(len(text) / 1000, 0.2))
        reranked.append((match, adjusted_score))
    
    # Sort by adjusted score
    reranked.sort(key=lambda x: x[1], reverse=True)
    
    # Return top 5 after reranking
    return [match for match, _ in reranked[:5]], search_time

def generate_response(query, context_docs):
    """Generate AI response using Gemini with URL context and conversation memory"""
    import time
    start_time = time.time()
    
    if not context_docs:
        return "I couldn't find relevant information in the documentation.", 0, []
    
    # Extract URLs from context docs
    urls = []
    context_text = []
    for doc in context_docs:
        text = doc.metadata.get('text', '')
        context_text.append(f"**{doc.metadata.get('title', 'Unknown')}**\n{text}")
        
        # Extract URLs from the text
        found_urls = re.findall(r'https://docs\.beconversive\.com/[^\s\)]+', text)
        urls.extend(found_urls[:2])  # Limit to 2 URLs per doc
    
    # Limit total URLs to 10 to avoid token limits
    urls = list(set(urls))[:10]
    
    context = "\n\n".join(context_text)
    
    # Add conversation memory (last 5 exchanges)
    memory_context = ""
    if conversation_memory:
        memory_context = "\n**Previous conversation:**\n"
        for mem in conversation_memory[-5:]:
            memory_context += f"User: {mem['query']}\nAssistant: {mem['response'][:200]}...\n\n"
    
    # Build prompt with URLs and memory
    if urls:
        url_list = "\n".join([f"- {url}" for url in urls])
        prompt = f"""You are an expert assistant for SMS Magic (Conversive) documentation.
{memory_context}
**Context from documentation:**
{context}

**Related documentation URLs (fetch these for complete information):**
{url_list}

**User Question:** {query}

**Instructions:**
1. Consider the previous conversation context if relevant
2. Read the context AND fetch content from the URLs above for complete information
3. Provide a detailed, step-by-step answer
4. Include specific instructions, buttons to click, or fields to fill
5. Use bullet points or numbered lists for clarity
6. Be specific and actionable

**Answer:**"""
    else:
        prompt = f"""You are an expert assistant for SMS Magic (Conversive) documentation.
{memory_context}
**Context from documentation:**
{context}

**User Question:** {query}

**Instructions:**
1. Consider the previous conversation context if relevant
2. Provide a detailed, step-by-step answer based on the context
3. Include specific instructions, buttons to click, or fields to fill
4. Use bullet points or numbered lists for clarity
5. Be specific and actionable

**Answer:**"""
    
    try:
        # Enable URL context tool only
        tools = [types.Tool(url_context=types.UrlContext())]
        
        config = types.GenerateContentConfig(tools=tools)
        
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
        
        generation_time = time.time() - start_time
        
        # Generate follow-up suggestions
        suggestions = generate_followup_suggestions(query, response.text)
        
        return response.text, generation_time, suggestions
    except Exception as e:
        return f"Error generating response: {str(e)}\n\nPartial context:\n{context[:500]}...", 0, []

def generate_followup_suggestions(query, response):
    """Generate follow-up question suggestions"""
    suggestions = []
    
    # Simple keyword-based suggestions
    if "campaign" in query.lower():
        suggestions = [
            "How do I edit a campaign?",
            "What are the different campaign types?",
            "How do I schedule a campaign?"
        ]
    elif "template" in query.lower():
        suggestions = [
            "How do I create a message template?",
            "Can I use variables in templates?",
            "How do I manage template folders?"
        ]
    elif "audience" in query.lower():
        suggestions = [
            "How do I create an audience segment?",
            "What data types are supported?",
            "How do I import contacts?"
        ]
    else:
        suggestions = [
            "How do I send my first message?",
            "What is the audience manager?",
            "How do I create a campaign?"
        ]
    
    return suggestions[:3]

def chat(message, history):
    """Main chat function with memory and enhanced features"""
    if not message.strip():
        return history, "", ""
    
    # Search for relevant docs with reranking
    docs, search_time = search_docs(message, top_k=10)
    
    # Generate response with memory
    response, gen_time, suggestions = generate_response(message, docs)
    
    # Format sources with relevance scores
    sources = f"\n\n**📚 Sources** (search: {search_time:.2f}s, generation: {gen_time:.2f}s):\n"
    sources += "\n".join([
        f"- [{doc.metadata['title']}]({doc.metadata.get('filename', '')}) (relevance: {doc.score:.3f})"
        for doc in docs[:3]
    ])
    
    # Add follow-up suggestions
    if suggestions:
        sources += "\n\n**💡 Follow-up questions:**\n" + "\n".join([f"- {s}" for s in suggestions])
    
    full_response = response + sources
    
    # Update conversation memory (keep last 5)
    conversation_memory.append({
        "query": message,
        "response": response
    })
    if len(conversation_memory) > 5:
        conversation_memory.pop(0)
    
    # Update history
    history.append((message, full_response))
    chat_history.append({
        "query": message,
        "response": response,
        "sources": docs,
        "search_time": search_time,
        "gen_time": gen_time
    })
    
    return history, "", ""

def get_index_stats():
    """Get index statistics"""
    stats = index.describe_index_stats()
    return f"""
**Index Statistics:**
- Total Vectors: {stats.total_vector_count:,}
- Dimension: {stats.dimension}
- Index Fullness: {stats.index_fullness:.2%}
- Total Queries: {len(chat_history)}
- Embedding Model: Gemini Embedding 001
- Generation Model: Gemini 2.0 Flash
"""

def visualize_vectors():
    """Create visualization of search results"""
    try:
        # Get sample query
        query_embedding = get_query_embedding("SMS Magic features and capabilities")
        results = index.query(
            vector=query_embedding,
            top_k=30,
            include_metadata=True
        )
        
        if not results.matches:
            return None
        
        # Extract data
        titles = [match.metadata.get('title', 'Unknown')[:40] for match in results.matches]
        scores = [match.score for match in results.matches]
        filenames = [match.metadata.get('filename', '')[:30] for match in results.matches]
        
        # Create bar chart
        fig = go.Figure(data=[go.Bar(
            x=scores,
            y=titles,
            orientation='h',
            marker=dict(
                color=scores,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Relevance")
            ),
            hovertemplate='<b>%{y}</b><br>Score: %{x:.3f}<br>File: %{text}<extra></extra>',
            text=filenames
        )])
        
        fig.update_layout(
            title="Document Relevance Scores (Sample Query: 'SMS Magic features')",
            xaxis_title="Similarity Score",
            yaxis_title="Document",
            height=800,
            yaxis=dict(autorange="reversed")
        )
        
        return fig
    except Exception as e:
        return None

def get_search_history():
    """Get formatted search history"""
    if not chat_history:
        return "No search history yet"
    
    history_text = ""
    for i, item in enumerate(chat_history[-10:], 1):
        history_text += f"**{i}. Query:** {item['query']}\n"
        history_text += f"**Response:** {item['response'][:150]}...\n\n"
    
    return history_text

# Create Gradio interface
with gr.Blocks(title="SMS Magic RAG Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔮 SMS Magic Documentation Assistant")
    gr.Markdown("Powered by Gemini Embeddings + Gemini 2.5 Flash | Features: Conversation Memory, Reranking, URL Context")
    
    with gr.Tabs():
        with gr.Tab("💬 Chat"):
            chatbot = gr.Chatbot(height=500, label="Chat History", type="tuples")
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Ask a question about SMS Magic...",
                    label="Your Question",
                    scale=4
                )
                submit = gr.Button("Send", variant="primary", scale=1)
            
            clear = gr.Button("Clear Chat")
            
            gr.Markdown("""
            **Example questions:**
            - How do I create a campaign?
            - What is the audience manager?
            - How do I send my first message?
            - What are message templates?
            """)
            
            # Add feedback buttons
            with gr.Row():
                feedback_output = gr.Textbox(label="Feedback", visible=False)
            
            submit.click(chat, inputs=[msg, chatbot], outputs=[chatbot, msg, feedback_output])
            msg.submit(chat, inputs=[msg, chatbot], outputs=[chatbot, msg, feedback_output])
            clear.click(lambda: ([], None, None), outputs=[chatbot, msg, feedback_output])
        
        with gr.Tab("📊 Document Visualization"):
            gr.Markdown("### Document Relevance Visualization")
            gr.Markdown("Shows semantic similarity of documents to a sample query")
            
            viz_button = gr.Button("Generate Visualization", variant="primary")
            plot = gr.Plot(label="Vector Space")
            
            viz_button.click(visualize_vectors, outputs=plot)
        
        with gr.Tab("📈 Statistics"):
            gr.Markdown("### System Statistics")
            
            stats_button = gr.Button("Refresh Stats", variant="primary")
            stats_output = gr.Markdown()
            
            gr.Markdown("### Recent Search History")
            history_button = gr.Button("Show History")
            history_output = gr.Markdown()
            
            stats_button.click(get_index_stats, outputs=stats_output)
            history_button.click(get_search_history, outputs=history_output)
    
    # Load stats on startup
    demo.load(get_index_stats, outputs=None)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)
