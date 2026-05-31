from src.loaders.document_loader import load_documents
from src.chunking.text_chunker import chunk_documents
from src.vectordb.chroma_store import create_vector_store

def main():

    print("=" * 50)
    print("RAG DOCUMENT INDEXING")
    print("=" * 50)

    print("\nLoading documents...")

    documents = load_documents("data")

    print(f"Loaded {len(documents)} documents")

    print("\nChunking documents...")

    chunks = chunk_documents(documents)

    print(f"Created {len(chunks)} chunks")

    print("\nCreating vector database...")

    create_vector_store(chunks)

    print("\nIndexing completed successfully!")

if __name__ == "__main__":
    main()