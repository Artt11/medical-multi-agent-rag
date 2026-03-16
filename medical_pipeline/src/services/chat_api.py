from fastapi import APIRouter, HTTPException
import uuid
from pydantic import BaseModel
from typing import Optional
from src.agents.graph import app as medical_graph


class ChatRequest(BaseModel):
    query: str
    patient_id: Optional[str] = None


class ChatResponse(BaseModel):
    agent_used: str
    answer: str


# Ուշադրություն դարձրու նոր tag-ին՝ "AI Agents Chat"
router = APIRouter(prefix="/v1/medical", tags=["AI Agents Chat"])


@router.post("/chat", response_model=ChatResponse)
async def ask_medical_agents(request: ChatRequest):
    try:
        initial_state = {
            "query": request.query,
            "patient_id": request.patient_id,
            "timeframe": None,
            "disease": None,
            "context_chunks": [],
            "sql_results": []
        }

        print(f"🧠 Սկսում ենք մշակել հարցումը: {request.query}")
        thread_id = request.patient_id or str(uuid.uuid4())
        result = medical_graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": thread_id}}
        )

        return ChatResponse(
            agent_used=result.get("next_node", "unknown"),
            answer=result.get("final_answer", "Պատասխանը չի գեներացվել:")
        )

    except Exception as e:
        import traceback
        print(f" AI Agent Error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Multi-Agent System error: {str(e)}")
