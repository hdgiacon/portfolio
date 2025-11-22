from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
import traceback

from src.domains.chat.service import ChatService, get_chat_service
from src.domains.chat.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model = ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service) 
):
    try:
        ai_response = await service.get_response(request.message)
        
        return ChatResponse(response = ai_response)
    
    except Exception as e:
        logger.exception(f"Error generating chat response: {e} \n\nStacktrace: \n\n{traceback.format_exc}")

        raise HTTPException(status_code = 500, detail = "Internal process error answer")