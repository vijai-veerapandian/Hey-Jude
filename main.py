# main.py - For the Frontend Service
from dotenv import load_dotenv
load_dotenv()
import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the RAG service URL from the .env file
RAG_SERVICE_URL = os.environ.get("RAG_SERVICE_URL")

if not RAG_SERVICE_URL:
    raise RuntimeError("RAG_SERVICE_URL environment variable is not set. Please check your .env file.")

# --- FastAPI App ---
app = FastAPI()

# Mount static files and serve the frontend
static_path = os.path.join(BASE_DIR, "frontend", "static")
os.makedirs(static_path, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def read_index():
    index_path = os.path.join(BASE_DIR, "frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found"}

# API endpoint for the chat that acts as a proxy
@app.post("/api/chat")
async def chat_endpoint(request: dict):
    user_message = request.get("message", "")
    if not user_message:
        return {"error": "No message provided"}

    # Forward the request to the RAG service
    try:
        async with httpx.AsyncClient() as client:
            # The full URL to the RAG service's query endpoint
            full_url = f"{RAG_SERVICE_URL}/api/query"
            print(f"Forwarding request to: {full_url}")
            
            response = await client.post(
                full_url,
                json={"message": user_message},
                timeout=60.0 # Set a generous timeout
            )
            response.raise_for_status() # Raise an exception for bad status codes (like 404 or 500)
            return response.json()
            
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Error communicating with the RAG service: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {exc}")