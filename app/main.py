import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db")

# --- Initialize Embeddings and LLM ---
print("Initializing embedding model...")
model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)
print("Embedding model initialized.")

print("Initializing Ollama with phi3:mini...")
llm = Ollama(model="phi3:mini")
print("Ollama initialized.")

# --- Load the Vector Database ---
if not os.path.exists(DB_PATH):
    raise RuntimeError(f"Database not found at {DB_PATH}. Please run ingest.py first.")

print(f"Loading vector database from: {DB_PATH}")
vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
print("Vector database loaded successfully.")

# --- Create a Custom Prompt Template ---
# This template guides the LLM to use the provided context and answer concisely.
prompt_template = """
Use the following pieces of context to answer the question at the end. 
If you don't know the answer from the context provided, just say that you don't know, don't try to make up an answer.
Keep the answer concise and helpful.

Context: {context}

Question: {question}

Helpful Answer:
"""
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

# --- Create the RetrievalQA Chain with the custom prompt ---
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT} # Injecting our custom prompt
)
print("RAG chain with custom prompt created.")

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

# API endpoint for the chat
@app.post("/api/chat")
async def chat_endpoint(request: dict):
    """
    Handles chat requests by running them through the RAG chain and returning sources.
    """
    user_message = request.get("message", "")
    if not user_message:
        return {"error": "No message provided"}

    print(f"Received query: {user_message}")
    
    # Get the answer and the source documents from the RAG chain
    result = qa_chain.invoke({"query": user_message})
    
    ai_response = result.get("result", "Sorry, I couldn't find an answer.")
    
    # Extract the content from the source documents
    source_documents = result.get("source_documents", [])
    sources = [doc.page_content for doc in source_documents]

    print(f"Generated response: {ai_response}")
    print(f"Sources found: {len(sources)}")

    return {"response": ai_response, "sources": sources}
