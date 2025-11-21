import os
import fitz
from loguru import logger

from github import Github, NamedUser, AuthenticatedUser
from github.NamedUser import NamedUser
from github.AuthenticatedUser import AuthenticatedUser

from src.core.config import get_settings


class ExtractData:
    """"""

    def __init__(self) -> None:
        self.curriculum_pdf_path = "data/raw/curriculum_vitae_hector_dorrighello_giacon.pdf"
        self.github_token = get_settings().GITHUB_TOKEN

    def get_pdf_text(self) -> str:
        """"""

        full_text = ""

        os.makedirs("data/raw/", exist_ok = True)
        
        try:
            doc = fitz.open(self.curriculum_pdf_path)
            
            for page in doc:
                text = str(page.get_text("text"))

                full_text += text + "\n"
                
            doc.close()
            
        except Exception as e:
            logger.exception(f"PDF extraction error: {e}")
            
            return ""
        
        logger.success("PDF curriculum extraction complete")

        return full_text


    def get_github_info(self) -> NamedUser | AuthenticatedUser:
        """"""

        logger.info("GitHub connection init...")
        
        g = Github(self.github_token)
        user = g.get_user()

        logger.success("GitHub extraction complete")

        return user
