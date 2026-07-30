from pydantic import BaseModel


class SessionCreated(BaseModel):
    session_id: str


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    code: str | None
    stdout: str | None
    traceback: str | None


class UploadResponse(BaseModel):
    variable: str
    stdout: str | None
    traceback: str | None
