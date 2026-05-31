import os

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader
)

def load_documents(data_path):

    documents = []

    for file in os.listdir(data_path):

        file_path = os.path.join(data_path, file)

        try:

            if file.endswith(".pdf"):

                loader = PyPDFLoader(file_path)

                documents.extend(loader.load())

            elif file.endswith(".docx"):

                loader = Docx2txtLoader(file_path)

                documents.extend(loader.load())

            elif file.endswith(".txt"):

                loader = TextLoader(
                    file_path,
                    encoding="utf-8"
                )

                documents.extend(loader.load())

        except Exception as e:

            print(f"Error loading {file}: {e}")

    return documents