const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface ChatResponse {
  reply: string;
  code: string | null;
  stdout: string | null;
  traceback: string | null;
}

export interface UploadResponse {
  variable: string;
  stdout: string | null;
  traceback: string | null;
}

export async function createSession(): Promise<string> {
  const res = await fetch(`${API_URL}/sessions`, { method: "POST" });
  if (!res.ok) throw new Error("failed to create session");
  const data = await res.json();
  return data.session_id;
}

export async function sendMessage(sessionId: string, message: string): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/sessions/${sessionId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error("failed to send message");
  return res.json();
}

export async function uploadCsv(sessionId: string, file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/sessions/${sessionId}/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("failed to upload file");
  return res.json();
}
