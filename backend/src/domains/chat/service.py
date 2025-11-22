from functools import lru_cache
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from src.core.config import get_settings


class ChatService:
    """"""

    def __init__(self):
        """
        Initialize the heavy resources only once.

        This ensures that the embedding model and the connection to Groq
        are reused, functioning as a natural connection pool.
        """

        settings = get_settings()
        
        embedding_model = HuggingFaceEmbeddings(
            model_name = settings.SENTENSE_TRANSFORMER_MODEL
        )

        vectorstore = Chroma(
            persist_directory = "data/output/chroma_db",
            embedding_function = embedding_model,
            collection_name = "portfolio_collection"
        )

        self.retriever = vectorstore.as_retriever(
            search_type = "similarity",
            search_kwargs = {"k": 4}
        )

        self.llm = ChatGroq(
            api_key = settings.GROQ_API_KEY,
            model = settings.GROK_MODEL,
            temperature = 0,
            max_tokens = 512
        )

        self.prompt = ChatPromptTemplate.from_template(
            """
            Você é um assistente virtual profissional encarregado de responder perguntas sobre o currículo e portfólio de Héctor.
            
            Use APENAS o contexto fornecido abaixo para responder à pergunta do usuário.
            Se a resposta não estiver no contexto, diga educadamente que não possui essa informação sobre o candidato.
            Não invente informações. Seja conciso e direto. Responda sempre em Português do Brasil.
            
            <context>
            {context}
            </context>

            Pergunta do Usuário: {question}
            """
        )

        self.chain = (
            {"context": self.retriever | self.format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )


    def format_docs(self, docs: List[Document]) -> str:
        """"""
        
        return "\n\n".join(doc.page_content for doc in docs)

    async def get_response(self, query: str) -> str:
        """"""

        return await self.chain.ainvoke(query)


@lru_cache
def get_chat_service() -> ChatService:
    """"""

    return ChatService()