import os
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .rag import ingest_documents, retrieve_context, DB_PATH, EMBEDDING_MODEL_NAME
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

# Initialize FastAPI app
app = FastAPI()
# Get the absolute path to the directory containing main.py
# This ensures the path is correct regardless of where the command is run.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mount the 'frontend' directory to serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend/static")), name="static")

# Pydantic model for incoming chat requests
class ChatRequest(BaseModel):
    query: str

# Environment variables are used to configure the application.
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://ollama:11434")
UPLOAD_FOLDER = "./documents"

# Initialize vector store at startup
try:
    embedding_model = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_store = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embedding_model
    )
    print("Vector store loaded successfully.")
except Exception as e:
    print(f"Error loading vector store: {e}")
    vector_store = None
# Serve the main HTML page
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serves the main HTML page for document upload."""
    with open(os.path.join(BASE_DIR, "frontend/index.html"), "r") as f:
        return f.read()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint to upload a PDF file, validate it, and trigger ingestion.
    """
    max_file_size_mb = 100
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_size_bytes = 0
    # Create the upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024)
            if not chunk:
                break
            file_size_bytes += len(chunk)
            if file_size_bytes > max_file_size_mb * 1024 * 1024:
                os.remove(file_path)
                raise HTTPException(status_code=400, detail=f"File size exceeds the {max_file_size_mb}MB limit.")
            buffer.write(chunk)

    global vector_store
    vector_store = ingest_documents(UPLOAD_FOLDER)

    return {"message": f"File '{file.filename}' processed successfully!"}

@app.post("/chat")
async def chat_with_rag(request: ChatRequest):
    """
    Endpoint to answer a query using Retrieval-Augmented Generation (RAG).
    This endpoint is still available for testing, though the primary UI is now Open WebUI.
    """
    if not vector_store:
        return {"error": "Vector store not initialized. Please upload a PDF first."}

    context = retrieve_context(vector_store, request.query)

    prompt = f"Using the following context, answer the user's question. If you don't know the answer, say so.\n\nContext:\n{context}\n\nQuestion:\n{request.query}"

    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": "phi3:mini",
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        ollama_response = response.json()["response"]
        return {"response": ollama_response}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to communicate with Ollama: {e}"}
