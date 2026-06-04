import os
import sys
from dotenv import load_dotenv
from src.embedding import DocumentEmbedder
from src.vector_store import QdrantVectorStore
from src.generator import LLMGenerator

def main():
    # Load environment variables
    load_dotenv(override=True)
    
    # 1. Setup Embedder and Vector Store
    emb_provider = os.environ.get("EMBEDDING_MODEL_PROVIDER", "local")
    emb_model = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    top_k = int(os.environ.get("TOP_K", 3))
    
    # API keys checks
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")
    
    # Fallback embedding to local if keys are missing but selected
    if emb_provider == "gemini" and not gemini_key:
        emb_provider = "local"
        emb_model = "all-MiniLM-L6-v2"
    elif emb_provider == "openai" and not openai_key:
        emb_provider = "local"
        emb_model = "all-MiniLM-L6-v2"
        
    print("Initializing components, please wait...")
    try:
        embedder = DocumentEmbedder(provider=emb_provider, model_name=emb_model, api_key=gemini_key or openai_key)
    except Exception as e:
        print(f"Error initializing embedding client: {e}")
        sys.exit(1)
        
    # Check if Qdrant database exists
    qdrant_path = "./qdrant_db"
    if not os.path.exists(qdrant_path):
        print(f"Error: Vector store directory '{qdrant_path}' not found. Please run 'python index.py' first to index your documents.")
        sys.exit(1)
        
    vector_store = QdrantVectorStore(collection_name="documents", path=qdrant_path)
    
    # Verify that the collection has elements
    try:
        collections = vector_store.client.get_collections().collections
        exists = any(c.name == "documents" for c in collections)
        if not exists:
            print("Error: The 'documents' collection does not exist in Qdrant. Please run 'python index.py' first.")
            sys.exit(1)
            
        count = vector_store.client.get_collection("documents").points_count
        if count == 0:
            print("Error: The vector store has 0 indexed chunks. Please run 'python index.py' first.")
            sys.exit(1)
        print(f"Vector store connected. Found {count} indexed document chunks.")
    except Exception as e:
        print(f"Error connecting to vector store collection: {e}")
        sys.exit(1)
        
    # 2. Setup Generator (Groq by default, Gemini as fallback)
    # Check if Groq key exists and is not empty or placeholder
    has_groq = groq_key and len(groq_key.strip()) > 0 and "your-groq-api" not in groq_key
    has_gemini = gemini_key and len(gemini_key.strip()) > 0 and "your-gemini-api" not in gemini_key
    
    generator_provider = None
    generator_key = None
    
    if has_groq:
        generator_provider = "groq"
        # We auto-clean the environment variable key if it has a prefix
        if "gsk_" in groq_key:
            generator_key = groq_key[groq_key.index("gsk_"):]
        else:
            generator_key = groq_key
    elif has_gemini:
        generator_provider = "gemini"
        generator_key = gemini_key
    else:
        # Fallback to check if a mock or default key was provided
        # Let's inspect env for ANY GROQ_API_KEY
        raw_groq = os.environ.get("GROQ_API_KEY", "")
        if "gsk_" in raw_groq:
            generator_provider = "groq"
            generator_key = raw_groq[raw_groq.index("gsk_"):]
            print("Using cleaned GROQ_API_KEY from environment.")
            
    if not generator_provider:
        print("\n" + "!"*60)
        print("WARNING: No valid API keys found in your environment or .env file.")
        print("Please configure GROQ_API_KEY or GEMINI_API_KEY in a local '.env' file.")
        print("!"*60 + "\n")
        # Ask user to supply one
        try:
            user_key = input("Please enter a valid Groq API Key to proceed (or press Enter to exit): ").strip()
            if not user_key:
                print("Exiting.")
                sys.exit(0)
            generator_provider = "groq"
            generator_key = user_key
        except KeyboardInterrupt:
            print("\nExiting.")
            sys.exit(0)
            
    try:
        generator = LLMGenerator(provider=generator_provider, api_key=generator_key)
    except Exception as e:
        print(f"Error initializing generator: {e}")
        sys.exit(1)
        
    print("\n" + "="*50)
    print(" RAG Document Q&A Bot Initialized! ")
    print(" You can ask questions based on the ingested documents. ")
    print(" Type 'exit' or 'quit' to close the program. ")
    print("="*50 + "\n")
    
    # 3. Interactive Loop
    while True:
        try:
            query = input("\nAsk a question: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
                
            print("\nStep 1: Embedding query and searching vector store...")
            query_vector = embedder.embed_query(query)
            results = vector_store.search(query_vector, top_k=top_k)
            
            if not results:
                print("No relevant context found in vector store.")
                continue
                
            print(f"\nStep 2: Retrieved Top-{len(results)} relevant chunks:")
            for i, hit in enumerate(results):
                meta = hit["metadata"]
                source = meta.get("source", "Unknown")
                location = f"Page {meta['page']}" if "page" in meta else f"Section: {meta['section']}"
                print(f"  [{i+1}] {source} ({location}) - Similarity Score: {hit['score']:.4f}")
                
            print("\nStep 3: Generating grounded answer...")
            answer = generator.generate_answer(query, results)
            
            print("\n=== ANSWER ===")
            print(answer)
            print("==============\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred during query processing: {e}")

if __name__ == "__main__":
    main()
