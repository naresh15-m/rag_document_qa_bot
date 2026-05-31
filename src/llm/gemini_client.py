import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

from src.prompts.rag_prompt import RAG_PROMPT

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

def generate_answer(query, docs):

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = RAG_PROMPT.format(
        context=context,
        question=query
    )

    response = llm.invoke(prompt)

    return response.content