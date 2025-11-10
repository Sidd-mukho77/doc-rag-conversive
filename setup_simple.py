import os
from pathlib import Path
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("sms-magic-docs-v2")

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
    """Process all markdown files"""
    data_path = Path(data_dir)
    md_files = list(data_path.glob("*.md"))
    
    print(f"\nFound {len(md_files)} markdown files")
    
    records_to_upsert = []
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
            
            for chunk_idx, chunk in enumerate(chunks):
                # Create unique ID
                record_id = f"{md_file.stem}_chunk_{chunk_idx}"
                
                # Prepare record
                record = {
                    "id": record_id,
                    "chunk_text": chunk,  # This will be embedded
                    "title": title,
                    "filename": md_file.name,
                    "chunk_index": chunk_idx,
                    "text": chunk[:500]
                }
                
                records_to_upsert.append(record)
                
                # Upsert in batches
                if len(records_to_upsert) >= batch_size:
                    try:
                        index.upsert_records("docs", records_to_upsert)
                        print(f"  ✓ Upserted batch of {len(records_to_upsert)} records")
                        records_to_upsert = []
                    except Exception as e:
                        print(f"  ✗ Error upserting batch: {e}")
                        records_to_upsert = []
        
        except Exception as e:
            print(f"  ✗ Error processing {md_file.name}: {e}")
    
    # Upsert remaining records
    if records_to_upsert:
        try:
            index.upsert_records("docs", records_to_upsert)
            print(f"✓ Upserted final batch of {len(records_to_upsert)} records")
        except Exception as e:
            print(f"✗ Error upserting final batch: {e}")
    
    print(f"\n✓ Setup complete!")

if __name__ == "__main__":
    print("=== SMS Magic Docs Vector DB Setup ===\n")
    process_markdown_files()
