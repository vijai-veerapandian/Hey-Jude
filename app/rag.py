import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

# This is a constant for the path where the vector store will be saved.
DB_PATH = "./chroma_db"
# This is the name of the embedding model that converts text to vectors.
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def ingest_documents(documents_path):
    """
    Loads PDF documents from a specified directory, splits them into chunks, 
    and creates a persistent ChromaDB vector store.
    """
    docs = []
    for filename in os.listdir(documents_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(documents_path, filename)
            loader = PyPDFLoader(file_path)
            docs.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)

    embedding_model = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=DB_PATH
    )
    vector_store.persist()
    print("Ingestion complete. Vector store created.")

    return vector_store

def retrieve_context(vector_store, query, k=4):
    """
    Retrieves the most relevant document chunks from the vector store 
    based on a given query.
    """
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])
