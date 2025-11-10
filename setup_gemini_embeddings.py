import os
from pathlib import Path
from pinecone import Pinecone, ServerlessSpec
from google import genai
from google.genai import types
from dotenv import load_dotenv
import time

load_dotenv()

# Initialize clients
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

INDEX_NAME = "sms-magic-gemini"
EMBEDDING_DIMENSION = 768  # Using 768 for efficiency

def create_index():
    """Create Pinecone index for Gemini embeddings"""
    existing_indexes = [index.name for index in pc.list_indexes()]
    
    if INDEX_NAME not in existing_indexes:
        print(f"Creating index: {INDEX_NAME}")
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        print("Waiting for index to be ready...")
        time.sleep(10)
    else:
        print(f"Index {INDEX_NAME} already exists")
    
    return pc.Index(INDEX_NAME)

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    
    return chunks

def get_embeddings(texts):
    """Get embeddings from Gemini with normalization"""
    import numpy as np
    
    result = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=EMBEDDING_DIMENSION
        )
    )
    
    # Normalize embeddings for better similarity
    embeddings = []
    for embedding_obj in result.embeddings:
        values = np.array(embedding_obj.values)
        normalized = values / np.linalg.norm(values)
        embeddings.append(normalized.tolist())
    
    return embeddings

def process_markdown_files(data_dir="scraped_data"):
    """Process all markdown files and create embeddings"""
    index = create_index()
    data_path = Path(data_dir)
    md_files = list(data_path.glob("*.md"))
    
    print(f"\nFound {len(md_files)} markdown files")
    print("Processing with 3-second delay between files to respect API limits...\n")
    
    vectors_to_upsert = []
    batch_size = 50
    
    for i, md_file in enumerate(md_files, 1):
        print(f"Processing [{i}/{len(md_files)}]: {md_file.name}")
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title
            lines = content.split('\n')
            title = lines[0].replace('#', '').strip() if lines else md_file.stem
            
            # Chunk the content
            chunks = chunk_text(content)
            
            # Get embeddings for all chunks at once (batch processing)
            embeddings = get_embeddings(chunks)
            
            for chunk_idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{md_file.stem}_chunk_{chunk_idx}"
                
                metadata = {
                    "title": title,
                    "filename": md_file.name,
                    "chunk_index": chunk_idx,
                    "text": chunk[:1000],
                    "total_chunks": len(chunks)
                }
                
                vectors_to_upsert.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                })
                
                # Upsert in batches
                if len(vectors_to_upsert) >= batch_size:
                    index.upsert(vectors=vectors_to_upsert)
                    print(f"  ✓ Upserted batch of {len(vectors_to_upsert)} vectors")
                    vectors_to_upsert = []
            
            # Add delay between files to respect API rate limits
            if i < len(md_files):
                time.sleep(3)
        
        except Exception as e:
            print(f"  ✗ Error processing {md_file.name}: {e}")
            # Wait longer if there's an error (might be rate limit)
            time.sleep(5)
    
    # Upsert remaining vectors
    if vectors_to_upsert:
        index.upsert(vectors=vectors_to_upsert)
        print(f"✓ Upserted final batch of {len(vectors_to_upsert)} vectors")
    
    # Get index stats
    time.sleep(2)
    stats = index.describe_index_stats()
    print(f"\n✓ Setup complete!")
    print(f"Total vectors in index: {stats.total_vector_count}")
    
    return stats

if __name__ == "__main__":
    print("=== SMS Magic Docs with Gemini Embeddings ===\n")
    process_markdown_files()
