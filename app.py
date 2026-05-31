import streamlit as st

from src.retrieval.retriever import retrieve_documents
from src.llm.gemini_client import generate_answer

st.set_page_config(
    page_title="RAG QA Bot",
    page_icon="📚",
    layout="wide"
)

st.title("📚 RAG Document Q&A Bot")

st.markdown("Ask questions from your documents")

query = st.text_input("Enter your question")

if query:

    docs = retrieve_documents(query)

    answer = generate_answer(query, docs)

    st.subheader("Answer")
    st.write(answer)

    st.subheader("Retrieved Sources")

    for i, doc in enumerate(docs):

        st.markdown(f"### Source {i+1}")

        st.write(doc.metadata)

        st.write(doc.page_content[:500])

        st.divider()