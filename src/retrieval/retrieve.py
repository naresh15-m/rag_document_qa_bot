from langchain_community.vectorstores import Chroma

from src.embeddings.embedding_model import load_embedding_model

embedding_model = load_embedding_model()

vector_store = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding_model
)

def retrieve_documents(query, k=3):

    docs = vector_store.similarity_search(
        query,
        k=k
    )

    return docs