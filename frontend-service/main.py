# main.py - For the Frontend Service
from dotenv import load_dotenv
load_dotenv()
import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

# --- Configuration ---
# Get the directory where this main.py file is located.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the RAG service URL from the .env file
RAG_SERVICE_URL = os.environ.get("RAG_SERVICE_URL")

if not RAG_SERVICE_URL:
    raise RuntimeError("RAG_SERVICE_URL environment variable is not set. Please check your .env file.")

# --- FastAPI App ---
app = FastAPI()

# --- Path Configuration ---
# Define the paths to your frontend files.
# This assumes your 'frontend' folder is in the same directory as this 'main.py' file.
static_path = os.path.join(BASE_DIR, "frontend", "static")
index_path = os.path.join(BASE_DIR, "frontend", "index.html")

# --- Create Static Directory if it doesn't exist ---
# This prevents errors if the 'static' folder is missing.
os.makedirs(static_path, exist_ok=True)

# --- Mount Static Files ---
# This makes files in your 'static' folder (like CSS or JS) available.
app.mount("/static", StaticFiles(directory=static_path), name="static")

# --- Serve the Frontend ---
# This is the main route that serves your index.html file.
@app.get("/")
async def read_index():
    if not os.path.exists(index_path):
        # If the file is not found, return a clear error.
        raise HTTPException(status_code=404, detail=f"index.html not found at path: {index_path}")
    return FileResponse(index_path)

# API endpoint for the chat that acts as a proxy
@app.post("/api/chat")
async def chat_endpoint(request: dict):
    user_message = request.get("message", "")
    if not user_message:
        return {"error": "No message provided"}

    # Forward the request to the RAG service
    try:
        async with httpx.AsyncClient() as client:
            full_url = f"{RAG_SERVICE_URL}/api/query"
            print(f"Forwarding request to: {full_url}")
            
            response = await client.post(
                full_url,
                json={"message": user_message},
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Error communicating with the RAG service: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {exc}")