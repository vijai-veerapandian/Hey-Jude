import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# --- Configuration ---
# Define paths for your data and the persistent database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "db")

def find_handbook_file():
    """
    Finds a PDF file in the data directory that starts with 'handbook-'.
    Returns the full path to the file if found, otherwise None.
    """
    search_pattern = os.path.join(DATA_PATH, "handbook-*.pdf")
    pdf_files = glob.glob(search_pattern)
    
    if not pdf_files:
        print(f"Error: No file matching the pattern '{search_pattern}' was found.")
        return None
    
    if len(pdf_files) > 1:
        print(f"Error: Multiple handbook files found. Please ensure only one file starting with 'handbook-' exists in the data directory.")
        print(f"Files found: {pdf_files}")
        return None
        
    return pdf_files[0]

def main():
    """
    Main function to ingest the PDF document and store it in ChromaDB.
    """
    print("--- Starting Document Ingestion ---")

    # 1. Find and load the document
    pdf_path = find_handbook_file()
    if not pdf_path:
        return
        
    print(f"Loading document from: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    print(f"Successfully loaded {len(documents)} page(s).")

    # 2. Split the document into chunks
    print("Splitting document into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} text chunks.")

    # 3. Create embeddings
    print("Initializing embedding model...")
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    print("Embedding model initialized.")

    # 4. Create and persist the vector database
    print(f"Creating and persisting vector store at: {DB_PATH}")
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=DB_PATH
    )
    print("--- Ingestion Complete ---")
    print(f"Vector store created successfully with {vectorstore._collection.count()} documents.")

if __name__ == "__main__":
    main()