"use client";

import { useEffect, useRef, useState } from "react";
import { createSession, sendMessage } from "@/lib/api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  code?: string | null;
  stdout?: string | null;
  traceback?: string | null;
}

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionError, setSessionError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    createSession()
      .then(setSessionId)
      .catch(() => setSessionError("Could not reach the backend. Is it running?"));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!sessionId || !input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const result = await sendMessage(sessionId, userMessage);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.reply,
          code: result.code,
          stdout: result.stdout,
          traceback: result.traceback,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Something went wrong reaching the backend." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-1 flex-col max-w-3xl w-full mx-auto p-4">
      <header className="py-4">
        <h1 className="text-xl font-semibold">charissa</h1>
        <p className="text-sm text-gray-500">a conversational data engineering assistant</p>
      </header>

      {sessionError && <p className="text-sm text-red-500 mb-4">{sessionError}</p>}

      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.map((message, i) => (
          <div key={i} className={message.role === "user" ? "text-right" : "text-left"}>
            <div
              className={
                "inline-block max-w-[85%] rounded-lg px-3 py-2 text-sm text-left " +
                (message.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800")
              }
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              {message.code && (
                <pre className="mt-2 overflow-x-auto rounded bg-black/80 text-white p-2 text-xs">
                  <code>{message.code}</code>
                </pre>
              )}
              {message.stdout && (
                <pre className="mt-2 overflow-x-auto rounded bg-gray-900 text-green-400 p-2 text-xs">
                  {message.stdout}
                </pre>
              )}
              {message.traceback && (
                <pre className="mt-2 overflow-x-auto rounded bg-gray-900 text-red-400 p-2 text-xs">
                  {message.traceback}
                </pre>
              )}
            </div>
          </div>
        ))}
        {loading && <p className="text-sm text-gray-400">thinking...</p>}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 pt-2 border-t">
        <input
          className="flex-1 rounded border px-3 py-2 text-sm bg-transparent"
          placeholder="Ask something about your data..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!sessionId || loading}
        />
        <button
          type="submit"
          className="rounded bg-blue-600 text-white px-4 py-2 text-sm disabled:opacity-50"
          disabled={!sessionId || loading || !input.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
}
