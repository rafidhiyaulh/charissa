import asyncio
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from charissa.api.auth import require_api_key
from charissa.api.schemas import ChatRequest, ChatResponse, SessionCreated
from charissa.api.session import SessionManager

load_dotenv()

_session_manager = SessionManager()
_SESSION_TTL_SECONDS = int(os.environ.get("SESSION_TTL_SECONDS", 1800))
_CLEANUP_INTERVAL_SECONDS = 60


async def _cleanup_idle_sessions_loop():
    while True:
        await asyncio.sleep(_CLEANUP_INTERVAL_SECONDS)
        _session_manager.close_idle(_SESSION_TTL_SECONDS)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    task = asyncio.create_task(_cleanup_idle_sessions_loop())
    yield
    task.cancel()


app = FastAPI(title="charissa", lifespan=lifespan)

_allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_session_manager() -> SessionManager:
    return _session_manager


@app.post("/sessions", response_model=SessionCreated, dependencies=[Depends(require_api_key)])
def create_session(sessions: SessionManager = Depends(get_session_manager)):
    return SessionCreated(session_id=sessions.create())


@app.post("/sessions/{session_id}/chat", response_model=ChatResponse, dependencies=[Depends(require_api_key)])
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


@app.delete("/sessions/{session_id}", dependencies=[Depends(require_api_key)])
def close_session(session_id: str, sessions: SessionManager = Depends(get_session_manager)):
    if not sessions.close(session_id):
        raise HTTPException(status_code=404, detail="session not found")
    return {"status": "closed"}
