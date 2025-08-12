import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# --- Configuration ---
# Define paths for your data and the persistent database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "db")
PDF_PATH = os.path.join(DATA_PATH, "handbook.pdf")

def main():
    """
    Main function to ingest the PDF document and store it in ChromaDB.
    """
    print("--- Starting Document Ingestion ---")

    # 1. Load the document
    if not os.path.exists(PDF_PATH):
        print(f"Error: The file '{PDF_PATH}' was not found.")
        return
        
    print(f"Loading document from: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"Successfully loaded {len(documents)} page(s).")

    # 2. Split the document into chunks
    print("Splitting document into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} text chunks.")

    # 3. Create embeddings
    # This uses a local model to create numerical representations of the text.
    print("Initializing embedding model...")
    # Using a popular, lightweight model for embeddings
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    print("Embedding model initialized.")

    # 4. Create and persist the vector database
    print(f"Creating and persisting vector store at: {DB_PATH}")
    # This will create a 'db' folder and store the indexed data there.
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=DB_PATH
    )
    print("--- Ingestion Complete ---")
    print(f"Vector store created successfully with {vectorstore._collection.count()} documents.")

if __name__ == "__main__":
    main()
