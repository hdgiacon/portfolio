import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.domains.ingest.extract import ExtractData
from src.domains.ingest.transform import TransformData
from src.domains.ingest.load import LoadData

from src.domains.chat.router import router as chat_router

CHROMA_DB_PATH = "data/output/chroma_db"


def run_full_ingest_pipeline():
    """"""

    logger.info("Database not found. Starting full ingestion pipeline...")

    extractor = ExtractData()
    pdf_text = extractor.get_pdf_text()
    github_user = extractor.get_github_info()

    transformer = TransformData()
    transformer.parse_structured_curriculum(pdf_text)
    
    gh_docs = transformer.parse_header_github_data(github_user)
    transformer.parse_repository_github_data(github_user, gh_docs)

    loader = LoadData()
    loader.create_vector_db()

    logger.success("Pipeline finished. Vector Database created.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """"""

    if os.path.exists(CHROMA_DB_PATH):
        logger.info("Vector Database found. API ready to serve.")

    else:
        try:
            run_full_ingest_pipeline()
        
        except Exception as e:
            logger.critical(f"Failed to initialize database: {e}")
    
    yield
    
    logger.info("Shutting down API...")


app = FastAPI(
    title = "RAG API Portfolio",
    description = "API for portfolio chatbot with RAG",
    version = "0.1.0",
    lifespan = lifespan 
)


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    # URL API deploy
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

app.include_router(chat_router, prefix = "/api", tags = ["Chat"])

@app.get("/db_check")
def health_check():
    """"""

    return {
        "status": "ok", 
        "chroma_exists": os.path.exists(CHROMA_DB_PATH)
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host = "0.0.0.0", port = 8000, reload = True)

