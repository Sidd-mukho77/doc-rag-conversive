import os
import time
from pathlib import Path
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

INDEX_NAME = "sms-magic-docs-v2"

def create_index():
    """Create Pinecone index with integrated embeddings"""
    existing_indexes = [index.name for index in pc.list_indexes()]
    
    if INDEX_NAME not in existing_indexes:
        print(f"Creating index: {INDEX_NAME}")
        pc.create_index_for_model(
            name=INDEX_NAME,
            cloud="aws",
            region="us-east-1",
            embed={
                "model": "multilingual-e5-large",
                "field_map": {"text": "chunk_text"}
            }
        )
        print("Waiting for index to be ready...")
        time.sleep(15)
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

def process_markdown_files(data_dir="scraped_data"):
    """Process all markdown files and create embeddings"""
    index = create_index()
    data_path = Path(data_dir)
    md_files = list(data_path.glob("*.md"))
    
    print(f"\nFound {len(md_files)} markdown files")
    
    vectors_to_upsert = []
    batch_size = 100
    
    for i, md_file in enumerate(md_files, 1):
        print(f"Processing [{i}/{len(md_files)}]: {md_file.name}")
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title (first line after #)
            lines = content.split('\n')
            title = lines[0].replace('#', '').strip() if lines else md_file.stem
            
            # Chunk the content
            chunks = chunk_text(content)
            
            for chunk_idx, chunk in enumerate(chunks):
                # Create unique ID
                vector_id = f"{md_file.stem}_chunk_{chunk_idx}"
                
                # Prepare record with text for integrated embedding
                record = {
                    "id": vector_id,
                    "chunk_text": chunk,  # This field will be embedded automatically
                    "title": title,
                    "filename": md_file.name,
                    "chunk_index": chunk_idx,
                    "text": chunk[:1000],  # Store first 1000 chars
                    "total_chunks": len(chunks)
                }
                
                vectors_to_upsert.append(record)
                
                # Upsert in batches
                if len(vectors_to_upsert) >= batch_size:
                    index.upsert(vectors=[], records=vectors_to_upsert, namespace="")
                    print(f"  Upserted batch of {len(vectors_to_upsert)} records")
                    vectors_to_upsert = []
        
        except Exception as e:
            print(f"  Error processing {md_file.name}: {e}")
    
    # Upsert remaining records
    if vectors_to_upsert:
        index.upsert(vectors=[], records=vectors_to_upsert, namespace="")
        print(f"Upserted final batch of {len(vectors_to_upsert)} records")
    
    # Get index stats
    time.sleep(2)
    stats = index.describe_index_stats()
    print(f"\n✓ Setup complete!")
    print(f"Total vectors in index: {stats.total_vector_count}")
    
    return stats

if __name__ == "__main__":
    print("=== SMS Magic Docs Vector DB Setup ===\n")
    process_markdown_files()
