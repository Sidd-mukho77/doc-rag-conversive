import os
import gradio as gr
from pinecone import Pinecone
from dotenv import load_dotenv
import plotly.graph_objects as go
from sklearn.decomposition import PCA
import numpy as np
from google import genai

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("sms-magic-docs-v2")

# Initialize Gemini
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Chat history
chat_history = []

def search_docs(query, top_k=5):
    """Search for relevant documents using integrated inference"""
    results = index.search(
        namespace="docs",
        query={
            "top_k": top_k,
            "inputs": {"text": query}
        }
    )
    return results.get('result', {}).get('hits', [])

def generate_response(query, context_docs):
    """Generate AI response using Gemini with context"""
    if not context_docs:
        return "I couldn't find relevant information in the documentation."
    
    # Build context from retrieved documents
    context = "\n\n".join([
        f"Document: {doc.get('fields', {}).get('title', 'Unknown')}\n{doc.get('fields', {}).get('text', '')}"
        for doc in context_docs
    ])
    
    # Create prompt for Gemini
    prompt = f"""You are a helpful AI assistant for SMS Magic (Conversive) documentation. 
Answer the user's question based on the provided documentation context.

Context from documentation:
{context}

User Question: {query}

Instructions:
- Answer the question clearly and concisely
- Use information from the context provided
- If the context doesn't contain enough information, say so
- Be helpful and professional
- Format your response in markdown

Answer:"""
    
    try:
        # Generate response using Gemini
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}\n\nContext available:\n{context[:500]}..."

def chat(message, history):
    """Main chat function"""
    if not message.strip():
        return history, ""
    
    # Search for relevant docs
    docs = search_docs(message, top_k=3)
    
    # Generate response
    response = generate_response(message, docs)
    
    # Format sources
    sources = "\n\n**Sources:**\n" + "\n".join([
        f"- {doc.get('fields', {}).get('title', 'Unknown')} (score: {doc.get('_score', 0):.3f})"
        for doc in docs
    ])
    
    full_response = response + sources
    
    # Update history
    history.append((message, full_response))
    chat_history.append({"query": message, "response": response, "sources": docs})
    
    return history, ""

def get_index_stats():
    """Get index statistics"""
    stats = index.describe_index_stats()
    return f"""
    **Index Statistics:**
    - Total Vectors: {stats.total_vector_count:,}
    - Dimension: {stats.dimension}
    - Index Fullness: {stats.index_fullness:.2%}
    - Total Queries: {len(chat_history)}
    """

def visualize_vectors():
    """Create visualization of search results"""
    # Get sample documents
    results = index.search(
        namespace="docs",
        query={
            "top_k": 30,
            "inputs": {"text": "SMS Magic features"}
        }
    )
    
    hits = results.get('result', {}).get('hits', [])
    if not hits:
        return None
    
    # Extract metadata
    titles = [hit.get('fields', {}).get('title', 'Unknown')[:40] for hit in hits]
    scores = [hit.get('_score', 0) for hit in hits]
    filenames = [hit.get('fields', {}).get('filename', '')[:30] for hit in hits]
    
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
        title="Document Relevance Scores",
        xaxis_title="Similarity Score",
        yaxis_title="Document",
        height=800,
        yaxis=dict(autorange="reversed")
    )
    
    return fig

def get_search_history():
    """Get formatted search history"""
    if not chat_history:
        return "No search history yet"
    
    history_text = ""
    for i, item in enumerate(chat_history[-10:], 1):
        history_text += f"**{i}. Query:** {item['query']}\n"
        history_text += f"**Response:** {item['response'][:100]}...\n\n"
    
    return history_text

# Create Gradio interface
with gr.Blocks(title="SMS Magic Docs RAG", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔮 SMS Magic Documentation Assistant")
    gr.Markdown("Ask questions about SMS Magic (Conversive) documentation")
    
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
            
            submit.click(chat, inputs=[msg, chatbot], outputs=[chatbot, msg])
            msg.submit(chat, inputs=[msg, chatbot], outputs=[chatbot, msg])
            clear.click(lambda: ([], None), outputs=[chatbot, msg])
        
        with gr.Tab("📊 Document Visualization"):
            gr.Markdown("### Document Relevance Visualization")
            gr.Markdown("This shows how relevant documents are to a sample query")
            
            viz_button = gr.Button("Generate Visualization", variant="primary")
            plot = gr.Plot(label="Vector Space")
            
            viz_button.click(visualize_vectors, outputs=plot)
        
        with gr.Tab("📈 Statistics"):
            gr.Markdown("### Index & Usage Statistics")
            
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
    demo.launch(server_name="0.0.0.0", server_port=7860)
