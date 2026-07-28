from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException

from charissa.api.schemas import ChatRequest, ChatResponse, SessionCreated
from charissa.api.session import SessionManager

load_dotenv()

app = FastAPI(title="charissa")

_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    return _session_manager


@app.post("/sessions", response_model=SessionCreated)
def create_session(sessions: SessionManager = Depends(get_session_manager)):
    return SessionCreated(session_id=sessions.create())


@app.post("/sessions/{session_id}/chat", response_model=ChatResponse)
def chat(session_id: str, request: ChatRequest, sessions: SessionManager = Depends(get_session_manager)):
    agent = sessions.get(session_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="session not found")

    result = agent.ask(request.message)
    return ChatResponse(
        reply=result.reply,
        code=result.code,
        stdout=result.execution["stdout"] if result.execution else None,
        traceback=result.execution["traceback"] if result.execution else None,
    )


@app.delete("/sessions/{session_id}")
def close_session(session_id: str, sessions: SessionManager = Depends(get_session_manager)):
    if not sessions.close(session_id):
        raise HTTPException(status_code=404, detail="session not found")
    return {"status": "closed"}
