RAG_PROMPT = """
You are a helpful AI assistant.

Answer ONLY from the provided context.

If answer is not found in the context say:
"I could not find relevant information in the documents."

Context:
{context}

Question:
{question}

Answer:
"""