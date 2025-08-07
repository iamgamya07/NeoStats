import os
import json
import faiss
import numpy as np
import sys
from openai import AzureOpenAI
from config.config import AZURE_EMBEDDING_API_KEY, AZURE_EMBEDDING_ENDPOINT, AZURE_EMBEDDING_VERSION, AZURE_EMBEDDING, validate_config

# Add current directory to find utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.common_utils import data_processor, text_processor

# Settings
INPUT_JSONL = "data/banking_documents.jsonl"
INDEX_PATH = "faiss_index"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

# Get Azure client
def get_azure_client():
    # Get Azure OpenAI client
    try:
        # Validate configuration
        validate_config()
        
        return AzureOpenAI(
            api_key=AZURE_EMBEDDING_API_KEY,
            api_version=AZURE_EMBEDDING_VERSION,
            azure_endpoint=AZURE_EMBEDDING_ENDPOINT,
        )
    except Exception as e:
        print(f"Failed to initialize Azure OpenAI client: {e}")
        return None

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    # Split text into chunks
    return text_processor.chunk_text(text, chunk_size, overlap)

def load_documents(jsonl_path):
    # Load documents and split into chunks
    documents = data_processor.load_jsonl(jsonl_path)
    
    all_chunks = []
    for doc in documents:
        title = doc.get("title", "")
        content = doc.get("content", "")
        full_text = f"{title}\n{content}"
        chunks = text_processor.chunk_text(full_text, CHUNK_SIZE, CHUNK_OVERLAP)
        all_chunks.extend(chunks)
        
    return all_chunks

def embed_chunks(chunks):
    # Generate embeddings for text chunks
    if not chunks:
        raise ValueError("No chunks provided for embedding")
    
    client = get_azure_client()
    if client is None:
        raise ValueError("Azure OpenAI client not available. Please check your configuration.")
        
    embeddings = []
    batch_size = 10
    
    print(f"Generating embeddings for {len(chunks)} chunks...")
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        try:
            response = client.embeddings.create(model=AZURE_EMBEDDING, input=batch)
            batch_embeddings = [np.array(d.embedding, dtype="float32") for d in response.data]
            embeddings.extend(batch_embeddings)
            print(f"   Processed batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
        except Exception as e:
            print(f"Error embedding batch {i//batch_size + 1}: {e}")
            raise
    
    return embeddings

def build_index(chunks, embeddings):
    # Build FAISS index from chunks and embeddings
    if not chunks or not embeddings:
        raise ValueError("No chunks or embeddings provided for indexing")
    
    if len(chunks) != len(embeddings):
        raise ValueError(f"Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings")
        
    print(f"Building FAISS index...")
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.vstack(embeddings))

    # Create directory if it doesn't exist
    os.makedirs(INDEX_PATH, exist_ok=True)
    
    # Save index
    index_path = os.path.join(INDEX_PATH, "faiss.index")
    faiss.write_index(index, index_path)
    print(f"Index saved to: {index_path}")

    # Save chunks
    chunks_path = os.path.join(INDEX_PATH, "chunks.jsonl")
    with open(chunks_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps({"text": chunk}) + "\n")
    print(f"Chunks saved to: {chunks_path}")

    print(f"Successfully indexed {len(chunks)} chunks. Saved to {INDEX_PATH}")

if __name__ == "__main__":
    try:
        print("Starting FAISS index build with Azure OpenAI...")
        chunks = load_documents(INPUT_JSONL)
        if chunks:
            embeddings = embed_chunks(chunks)
            build_index(chunks, embeddings)
        else:
            print("No valid chunks found in the input file.")
    except Exception as e:
        print(f"Error building index: {e}")
        exit(1)
