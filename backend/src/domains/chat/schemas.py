from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., description = "Pergunta ou sentença a ser consultada no banco de vetores")

class ChatResponse(BaseModel):
    response: str = Field(..., description = "Resposta gerada pela LLM a ser retornada ao frontend")