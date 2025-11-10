# SMS Magic Documentation RAG System

A Retrieval-Augmented Generation (RAG) system for querying SMS Magic documentation with vector visualization.

## Features

- 💬 **Chat Interface**: Ask questions about SMS Magic docs
- 📊 **3D Vector Visualization**: See semantic relationships between documents
- 📈 **Statistics Dashboard**: Track usage and index stats
- 🔍 **Source Attribution**: See which docs answered your question
- 🎯 **Semantic Search**: Find relevant info using AI embeddings

## Setup

### 1. Install Dependencies

```bash
pip install -r rag_requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file:

```bash
PINECONE_API_KEY=your_pinecone_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Setup Vector Database

Run the setup script to process markdown files and create embeddings:

```bash
python setup_vectordb.py
```

This will:
- Create a Pinecone index named "sms-magic-docs"
- Process all markdown files in `scraped_data/`
- Generate embeddings using OpenAI
- Upload vectors to Pinecone

### 4. Run the App

```bash
python rag_app.py
```

The app will be available at `http://localhost:7860`

## Usage

### Chat Tab
- Ask questions about SMS Magic features
- Get AI-generated answers with source citations
- View similarity scores for each source

### Vector Visualization Tab
- Click "Generate Visualization" to see 3D plot
- Hover over points to see document titles
- Color indicates similarity to query

### Statistics Tab
- View index statistics (total vectors, queries)
- See recent search history

## Deployment to Render.com

### 1. Create `render.yaml`

```yaml
services:
  - type: web
    name: sms-magic-rag
    env: python
    buildCommand: pip install -r rag_requirements.txt
    startCommand: python rag_app.py
    envVars:
      - key: PINECONE_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
```

### 2. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### 3. Deploy on Render
- Connect your GitHub repo
- Add environment variables
- Deploy!

## Architecture

```
User Query
    ↓
OpenAI Embeddings (text-embedding-3-small)
    ↓
Pinecone Vector Search (top 3 results)
    ↓
GPT-4o-mini (generate response with context)
    ↓
Response + Sources
```

## Cost Estimates

- **Pinecone**: Free tier (100K vectors)
- **OpenAI Embeddings**: ~$0.02 per 1M tokens
- **OpenAI GPT-4o-mini**: ~$0.15 per 1M input tokens
- **Render**: Free tier available

## Customization

- Change `top_k` in `search_docs()` for more/fewer sources
- Adjust `chunk_size` in `setup_vectordb.py` for different chunk sizes
- Modify system prompt in `generate_response()` for different behavior
- Change model to `gpt-4` for better quality (higher cost)
