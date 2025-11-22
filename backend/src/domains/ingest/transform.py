import re
import os
import html
import json
from typing import List, Dict
from loguru import logger
from datetime import datetime, timezone
from github.NamedUser import NamedUser
from github.AuthenticatedUser import AuthenticatedUser

from src.core.config import get_settings

SECTION_MAP = {
    "experiência profissional": "experience",
    "formação acadêmica": "education",
    "publicações": "publications",
    "idiomas": "languages",
    "tecnologia": "tech_stack",
    "outros conhecimentos": "courses"
}


class TransformData:
    """"""

    def __init__(self):
        self.ignore_repos = get_settings().IGNORE_REPOS
        self.output_github_json = "data/processed/github_data.json"
        self.output_curriculum_json = "data/processed/curriculum_data.json"


    def clean_markdown(self, text: str) -> str:
        """"""

        text = html.unescape(text)

        text = re.sub(r'```[\s\S]*?```', '', text)

        text = re.sub(r'`[^`]*`', '', text)

        text = re.sub(r'!\[[^\]]*\]\([^\)]*\)', '', text)
        text = re.sub(r'<[^>]+>', ' ', text)

        text = re.sub(r'\[\s*\]\([^\)]*\)', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        text = re.sub(r'\[\^?\d+\]', '', text)

        text = re.sub(r'[#\*_>~]', '', text)
        
        text = re.sub(r'^\s*[-+]\s+', '', text, flags = re.MULTILINE)
        text = re.sub(r'\s+', ' ', text).strip()

        return text
    
    def parse_header_github_data(self, user: NamedUser | AuthenticatedUser) -> List[Dict]:
        """"""

        documents = []

        logger.info(f"Processing profile: {user.name}")

        bio_content = f"Nome: {user.name}. "
        
        if user.bio:
            bio_content += f"Bio: {self.clean_markdown(user.bio)}. "
        if user.company:
            bio_content += f"Empresa atual: {user.company}. "
        if user.location:
            bio_content += f"Localização: {user.location}. "

        documents.append({
            "id": "gh_profile_main",
            "content": bio_content,
            "metadata": {
                "source": "github",
                "type": "profile",
                "url": user.html_url,
                "last_update": datetime.now(timezone.utc).isoformat()
            }
        })

        return documents
    
    def parse_repository_github_data(self, user: NamedUser | AuthenticatedUser, documents: List[Dict]) -> None:
        """"""

        logger.info("Processing repository...")

        repos = user.get_repos()

        for repo in repos:
            if repo.fork or repo.name in self.ignore_repos:
                continue

            logger.info(f" -> Extraindo: {repo.name}")

            readme_content = ""

            try:
                readme_raw = repo.get_readme().decoded_content.decode("utf-8")
                
                readme_content = self.clean_markdown(readme_raw)
            
            except Exception:
                logger.warning(f"    (Sem README para {repo.name}, usando descrição curta)")
                
                readme_content = repo.description if repo.description else f"Projeto {repo.name} sem descrição."

            topics = repo.get_topics()

            tags_str = ", ".join(topics) if topics else "geral"

            documents.append({
                "id": f"gh_repo_{repo.name}",
                "content": f"Projeto: {repo.name}. Descrição Técnica: {readme_content}",
                "metadata": {
                    "source": "github",
                    "type": "repository",
                    "project_name": repo.name,
                    "url": repo.html_url,
                    "language": repo.language if repo.language else "Desconhecida",
                    "tags": tags_str,
                    "stars": repo.stargazers_count
                }
            })

        logger.info(f"Saving {len(documents)} documents in {self.output_github_json}...")

        self.save_json_file(documents, self.output_github_json)

        logger.success("Repository process done!")


    def parse_structured_curriculum(self, full_text: str) -> None:
        """"""

        logger.info("Processing curriculum...")

        lines = full_text.split('\n')
        lines_to_process = lines[11:] if len(lines) > 11 else lines

        sections_found = []
        current_key = None
        current_lines = []

        for line in lines_to_process:
            clean_line = line.strip()
            
            if not clean_line: 
                continue

            normalized = clean_line.replace(':', '').lower()

            if normalized in SECTION_MAP:
                if current_key:
                    sections_found.append((current_key, current_lines))
                
                current_key = SECTION_MAP[normalized]
                current_lines = []
            
            elif current_key:
                current_lines.append(clean_line)

        if current_key:
            sections_found.append((current_key, current_lines))

        documents = []

        for key, lines_content in sections_found:
            text_content = "\n".join(lines_content)
            
            tags = key
            
            if key == "tech_stack":
                raw_techs = text_content.replace('\n', ' ').split('|')
                tags = ", ".join([t.strip().lower() for t in raw_techs if t.strip()])

            documents.append({
                "id": f"cv_section_{key}",
                "content": f"SEÇÃO DO CURRÍCULO: {key.upper()}\n\n{text_content}",
                "metadata": {
                    "source": "cv",
                    "type": key,
                    "tags": tags
                }
            })

        logger.info(f"Saving {len(documents)} documents in {self.output_curriculum_json}...")

        self.save_json_file(documents, self.output_curriculum_json)

        logger.success("Curriculum process done!")
    

    def save_json_file(self, documents: List[Dict], output_file_path: str) -> None:
        """"""

        os.makedirs("data/processed/", exist_ok = True)

        with open(output_file_path, 'w', encoding = 'utf-8') as f:
            json.dump(documents, f, ensure_ascii = False, indent = 2)