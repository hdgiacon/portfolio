import json
import shutil
import os
from typing import List
from pydantic import ValidationError
from loguru import logger

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from src.domains.ingest.schemas import PortfolioItem


class LoadData:
    """"""

    def __init__(self):
        self.chroma_path = "data/output/chroma_db"
        self.processed_json_paths = [os.path.join("data/processed", f) for f in os.listdir("data/processed/")]


    def load_and_validate(self) -> List[Document]:
        """"""

        lc_documents = []

        os.makedirs("data/output/", exist_ok = True)
        
        for file_path in self.processed_json_paths:
            with open(file_path, "r", encoding = "utf-8") as f:
                raw_data = json.load(f)
                
            logger.info(f"Processing {file_path} ({len(raw_data)} items)...")
            
            for item in raw_data:
                try:
                    validated_item = PortfolioItem(**item)
                    
                    doc = Document(
                        page_content = validated_item.content,
                        metadata = validated_item.metadata,
                        id = validated_item.id
                    )

                    lc_documents.append(doc)
                    
                except ValidationError as e:
                    logger.exception(f"validation error in {item.get('id', 'unknown')}: {e}")

        return lc_documents


    def create_vector_db(self):
        """"""

        if os.path.exists(self.chroma_path):
            shutil.rmtree(self.chroma_path)

        docs = self.load_and_validate()

        logger.start("Loading embedding model (HuggingFace)...")

        embedding_model = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")

        logger.info(f"Creating vectorstore in {self.chroma_path}...")
        
        Chroma.from_documents(
            documents = docs,
            embedding = embedding_model,
            persist_directory = self.chroma_path,
            collection_name = "portfolio_collection"
        )
        
        logger.success(f"{len(docs)} vectorized documents.")

