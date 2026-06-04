import os
import sys
from dotenv import load_dotenv
from src.ingestion import load_directory, chunk_documents
from src.embedding import DocumentEmbedder
from src.vector_store import QdrantVectorStore

def main():
    # Load environment variables from .env
    load_dotenv(override=True)
    
    # 1. Load documents
    data_dir = "data"
    print(f"=== STEP 1: Ingesting documents from '{data_dir}' ===")
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        print(f"Error: The '{data_dir}' folder is empty or does not exist. Please place PDFs, DOCX, or TXT files inside it.")
        sys.exit(1)
        
    docs = load_directory(data_dir)
    if not docs:
        print("Error: No documents could be successfully parsed.")
        sys.exit(1)
    print(f"Loaded {len(docs)} document pages/sections.")
    
    # 2. Chunk documents
    chunk_size = int(os.environ.get("CHUNK_SIZE", 1000))
    chunk_overlap = int(os.environ.get("CHUNK_OVERLAP", 150))
    print(f"\n=== STEP 2: Chunking documents (size={chunk_size}, overlap={chunk_overlap}) ===")
    chunks = chunk_documents(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    print(f"Created {len(chunks)} text chunks.")
    
    # 3. Create embedding client
    emb_provider = os.environ.get("EMBEDDING_MODEL_PROVIDER", "local")
    emb_model = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    print(f"\n=== STEP 3: Creating embeddings (provider={emb_provider}, model={emb_model}) ===")
    
    # Check for keys if using APIs
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    # Auto-fallback to local if keys are missing but selected
    if emb_provider == "gemini" and not gemini_key:
        print("Warning: GEMINI_API_KEY not found in environment. Falling back to local SentenceTransformers.")
        emb_provider = "local"
        emb_model = "all-MiniLM-L6-v2"
    elif emb_provider == "openai" and not openai_key:
        print("Warning: OPENAI_API_KEY not found in environment. Falling back to local SentenceTransformers.")
        emb_provider = "local"
        emb_model = "all-MiniLM-L6-v2"
        
    embedder = DocumentEmbedder(provider=emb_provider, model_name=emb_model, api_key=gemini_key or openai_key)
    
    # Extract raw text from chunks
    texts = [chunk["text"] for chunk in chunks]
    print(f"Generating embeddings in batch for {len(texts)} chunks...")
    try:
        embeddings = embedder.embed_documents(texts)
    except Exception as e:
        print(f"Error during embedding generation: {e}")
        sys.exit(1)
        
    vector_size = len(embeddings[0])
    print(f"Embeddings generated. Vector dimension: {vector_size}")
    
    # 4. Save to Vector DB
    print("\n=== STEP 4: Storing in Qdrant Vector Store ===")
    vector_store = QdrantVectorStore(collection_name="documents", path="./qdrant_db")
    vector_store.create_collection(vector_size=vector_size, force_recreate=True)
    vector_store.add_documents(chunks, embeddings)
    
    print("\n" + "="*50)
    print("SUCCESS: Indexing completed successfully!")
    print("The vector store is persisted on disk in the 'qdrant_db/' folder.")
    print("="*50)

if __name__ == "__main__":
    main()
