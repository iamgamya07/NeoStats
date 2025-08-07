import os
import json
import faiss
import numpy as np
import logging
from openai import AzureOpenAI
from config.config import (
    AZURE_EMBEDDING_API_KEY,
    AZURE_EMBEDDING_ENDPOINT,
    AZURE_EMBEDDING_VERSION,
    AZURE_EMBEDDING,
    validate_config,
)

# Paths to FAISS index and stored chunks
INDEX_PATH = "faiss_index"
CHUNKS_FILE = os.path.join(INDEX_PATH, "chunks.jsonl")
INDEX_FILE = os.path.join(INDEX_PATH, "faiss.index")

# Initializing Azure OpenAI client with error handling
def get_azure_client():
    """
    Get Azure OpenAI client with proper error handling.
    
    Returns:
        AzureOpenAI: Configured client or None if configuration is invalid
    """
    try:
        # Validate configuration
        validate_config()
        
        return AzureOpenAI(
            api_key=AZURE_EMBEDDING_API_KEY,
            api_version=AZURE_EMBEDDING_VERSION,
            azure_endpoint=AZURE_EMBEDDING_ENDPOINT,
        )
    except Exception as e:
        logging.error(f"Failed to initialize Azure OpenAI client: {e}")
        return None

# Loading FAISS index and text chunks
def load_index_and_chunks():
    """
    Load the FAISS index and text chunks from disk.
    
    Returns:
        tuple: (index, chunks) - FAISS index and list of text chunks
        
    Raises:
        FileNotFoundError: If index or chunks file not found
    """
    if not os.path.exists(INDEX_FILE) or not os.path.exists(CHUNKS_FILE):
        raise FileNotFoundError("FAISS index or chunks.jsonl not found. Please run build_faiss_index.py first.")

    try:
        index = faiss.read_index(INDEX_FILE)
        with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
            chunks = [json.loads(line)["text"] for line in f]
        return index, chunks
    except Exception as e:
        logging.error(f"Error loading index and chunks: {e}")
        raise

# Loading index and chunks at module level
try:
    index, chunks = load_index_and_chunks()
except Exception as e:
    logging.error(f"Failed to load index and chunks: {e}")
    index, chunks = None, []

# Embedding query using Azure OpenAI
def embed_query(query: str) -> np.ndarray:
    """
    Generate embedding for a query using Azure OpenAI.
    
    Args:
        query (str): Query text to embed
        
    Returns:
        np.ndarray: Query embedding
    """
    client = get_azure_client()
    if client is None:
        raise ValueError("Azure OpenAI client not available. Please check your configuration.")
    
    try:
        response = client.embeddings.create(
            input=[query],
            model=AZURE_EMBEDDING,
        )
        return np.array(response.data[0].embedding, dtype="float32")
    except Exception as e:
        logging.error(f"Error embedding query: {e}")
        raise

# Performing semantic search in the FAISS index
def retrieve_similar_documents(query: str, top_k: int = 5):
    """
    Retrieve similar documents using FAISS index and Azure OpenAI embeddings.
    
    Args:
        query (str): Search query
        top_k (int): Number of top results to return
        
    Returns:
        list: List of similar text chunks
    """
    if index is None or chunks is None:
        return ["Error: FAISS index not loaded. Please run build_faiss_index.py first."]
    
    try:
        query_embedding = embed_query(query).reshape(1, -1)
        distances, indices = index.search(query_embedding, top_k)
        results = [chunks[idx] for idx in indices[0] if idx < len(chunks)]
        return results if results else ["No relevant documents found."]
    except Exception as e:
        logging.error(f"Error in document retrieval: {e}")
        return [f"Error retrieving documents: {str(e)}"]
