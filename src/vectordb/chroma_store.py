from langchain_community.vectorstores import Chroma

from src.embeddings.embedding_model import load_embedding_model

def create_vector_store(chunks):

    embedding_model = load_embedding_model()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory="chroma_db"
    )

    vector_store.persist()

    return vector_store