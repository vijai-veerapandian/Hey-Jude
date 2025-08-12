# HeyJude - AI Assistant (Two-Service Architecture)

HeyJude is a smart, friendly AI assistant designed to help employees navigate internal company documents. This project is built using a modern, scalable two-service architecture.

## Architecture Overview

The application is split into two distinct services for better performance, security, and separation of concerns:

1.  **RAG/Inference Service:** A dedicated backend that lives on the same server as the Ollama model. It handles all data ingestion, vector storage, and AI processing.
2.  **Frontend Service:** A lightweight, containerized service that serves the user interface and acts as a proxy, forwarding user requests to the RAG service.

```
[User's Browser] <--> [Frontend Service (Docker)] <--> [RAG/Inference Service (Ollama Server)]
```

---

## Features

* **Interactive Chat Interface:** A modern, user-friendly frontend for seamless interaction.
* **Document-Aware Responses:** Answers are generated based on the content of provided internal documents.
* **Source Highlighting:** Users can see the exact text from the source document that was used to generate an answer.
* **Dark/Light Mode:** A theme toggle for user comfort.
* **Scalable Two-Service Design:** Decouples the UI from the AI, allowing them to be scaled and managed independently.

---

## Screenshots

**Main Chat Interface:**
`[YET TO INSERT SCREENSHOT OF THE MAIN CHAT WINDOW HERE]`

**"Show Sources" Feature:**
`[YET TO INSERT SCREENSHOT OF AN AI RESPONSE WITH THE SOURCES EXPANDED HERE]`

---

## Tech Stack

### RAG/Inference Service (Backend)
* **Python 3.10+**
* **FastAPI & Uvicorn**
* **LangChain, ChromaDB, SentenceTransformers, PyPDF**
* **Ollama (phi3:mini)**

### Frontend Service (UI & Proxy)
* **Python 3.10+**
* **FastAPI & Uvicorn**
* **HTTPX:** For making API calls to the RAG service.
* **Docker:** For containerization.
* **HTML, Tailwind CSS, Vanilla JavaScript**

---

## Setup and Execution

Follow these steps to set up and run both services.

### Part 1: RAG/Inference Service (On the Ollama Server)

This service must be running before you start the frontend.

#### **Folder Structure (`rag-service/`)**
```
rag-service/
├── app/
│   ├── data/
│   │   └── handbook-v1.pdf
│   ├── db/
│   │   └── ...
│   ├── ingest.py
│   └── rag_main.py
├── .env
└── requirements.txt
```

#### **Setup & Run**
1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure Environment:** Create a `.env` file with the local Ollama URL:
    ```
    OLLAMA_BASE_URL=http://localhost:11434
    ```
3.  **Ingest Data:** Run the ingestion script to build the vector database.
    ```bash
    python app/ingest.py
    ```
4.  **Start the Service:** Run the Uvicorn server. It must listen on `0.0.0.0` to be accessible on the network.
    ```bash
    uvicorn app.rag_main:app --host 0.0.0.0 --port 8001 --reload
    ```

### Part 2: Frontend Service:

This service serves the UI to the user.

#### **Folder Structure (`frontend-service/`)**
```
frontend-service/
├── app/
│   ├── frontend/
│   │   └── index.html
│   └── main.py
├── .env
├── Dockerfile
└── requirements.txt
```

#### **Setup & Run**
1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure Environment:** Create a `.env` file with the IP address and port of your RAG service:
    ```
    RAG_SERVICE_URL=[http://192.168.2.210:8001](http://192.168.2.210:8001)
    ```
3.  **Build the Docker Image:**
    ```bash
    docker build -t heyjude-frontend:1.0 .
    ```
4.  **Run the Docker Container:** Use the `--env-file` flag to pass the configuration.
    ```bash
    docker run --env-file ./.env -p 8000:8000 --name heyjude-frontend heyjude-frontend:1.0
    ```
5.  **Access the Application:** Open your browser and navigate to `http://localhost:8000`.
