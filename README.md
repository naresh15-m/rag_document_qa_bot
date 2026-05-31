# RAG Document Q&A Bot

A Retrieval-Augmented Generation (RAG) application that allows users to ask questions from documents using semantic search and LLMs.

---

# Features

- PDF, DOCX, TXT support
- Semantic search using embeddings
- ChromaDB vector database
- Gemini LLM integration
- Streamlit UI
- Source citations
- Persistent vector storage

---

# Tech Stack

- Python
- LangChain
- ChromaDB
- Sentence Transformers
- Gemini
- Streamlit

---

# Architecture

Documents
↓
Chunking
↓
Embeddings
↓
Vector DB
↓
Retriever
↓
LLM
↓
Answer Generation

---

# Setup

## Install dependencies

```bash
pip install -r requirements.txt
```

## Add Gemini API key

Create `.env`

```env
GOOGLE_API_KEY=your_key
```

## Index documents

```bash
python index.py
```

## Run app

```bash
streamlit run app.py
```

---

# Example Questions

- What is machine learning?
- Explain deep learning
- What are cloud deployment models?
- What is RAG?
- Explain AI in business

---

# Limitations

- Small context window
- Basic retrieval
- No reranking
- No conversation memory