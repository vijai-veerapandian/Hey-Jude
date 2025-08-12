# rag_main.py - To be run on the Ollama server (e.g., 192.168.2.210)
from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI
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

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

print(f"Initializing Ollama with phi3:mini at base URL: {OLLAMA_BASE_URL or 'default'}...")
llm = Ollama(model="phi3:mini", base_url=OLLAMA_BASE_URL)
print("Ollama initialized.")

# --- Load the Vector Database ---
if not os.path.exists(DB_PATH):
    raise RuntimeError(f"Database not found at {DB_PATH}. Please run ingest.py on this machine first.")

print(f"Loading vector database from: {DB_PATH}")
vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
print("Vector database loaded successfully.")

# --- Create a Custom Prompt Template ---
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

# --- Create the RetrievalQA Chain ---
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)
print("RAG chain with custom prompt created.")

# --- FastAPI App ---
app = FastAPI()

# API endpoint for handling queries
@app.post("/api/query")
async def query_endpoint(request: dict):
    user_message = request.get("message", "")
    if not user_message:
        return {"error": "No message provided"}

    print(f"Received query: {user_message}")
    result = qa_chain.invoke({"query": user_message})
    ai_response = result.get("result", "Sorry, I couldn't find an answer.")
    source_documents = result.get("source_documents", [])
    sources = [doc.page_content for doc in source_documents]

    print(f"Generated response: {ai_response}")
    print(f"Sources found: {len(sources)}")

    return {"response": ai_response, "sources": sources}

# To run this service:
# uvicorn rag_main:app --host 0.0.0.0 --port 8001