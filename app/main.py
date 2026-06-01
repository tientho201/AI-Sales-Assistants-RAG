"""
FastAPI application entrypoint.
Initializes database tables, configures CORS, and registers API routers.
"""
import sys
import os
# Auto-resolve python path for app package when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api import chat, sessions, ingest, feedback

import uvicorn
import logging

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# 1. Automatically create PostgreSQL/SQLite database tables on startup
try:
    logger.info("Initializing database migrations...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.critical(f"Failed to initialize database tables: {e}")

# 2. Initialize FastAPI Application
app = FastAPI(
    title="Multi-Agent Conversational Sales Copilot using Hybrid GraphRAG",
    description="Enterprise Hybrid RAG (Qdrant + Neo4j) and LangGraph agent for commercial vehicle sales.",
    version="1.0.0"
)

# 3. Configure CORS Middlewares for cross-origin frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Register routers
app.include_router(chat.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "AI-Sales-Assistants-RAG-Backend",
        "engine": "LangGraph Multi-Agent",
        "retrieval": "Hybrid GraphRAG (Qdrant + Neo4j)"
    }


if __name__ == "__main__":
    port = settings.PORT or 8081
    logger.info(f"Launching Uvicorn server on port {port}...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
