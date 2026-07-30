"use client";

import { useEffect, useRef, useState } from "react";
import { createSession, sendMessage, uploadCsv } from "@/lib/api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  code?: string | null;
  stdout?: string | null;
  traceback?: string | null;
}

const EXAMPLE_PROMPTS = [
  "Buat data transaksi contoh, lalu deteksi transaksi yang nilainya tidak wajar (outlier)",
  "Buat data pelanggan contoh yang ada duplikat dan nilai kosong, lalu bersihkan dan ringkas hasilnya",
  "Buat dua kolom data contoh, lalu hitung korelasinya dan jelaskan artinya",
];

function Avatar({ role }: { role: "user" | "assistant" }) {
  return (
    <div
      className={
        "flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-medium shadow-sm " +
        (role === "user"
          ? "bg-blue-600 text-white"
          : "bg-gradient-to-br from-violet-500 to-blue-500 text-white")
      }
    >
      {role === "user" ? "U" : "C"}
    </div>
  );
}

function OutputBlock({ label, tone, children }: { label: string; tone: "code" | "ok" | "error"; children: string }) {
  const toneClasses = {
    code: "text-zinc-200",
    ok: "text-emerald-400",
    error: "text-red-400",
  }[tone];

  return (
    <div className="mt-2 overflow-hidden rounded-lg border border-black/10 shadow-sm dark:border-white/10">
      <div className="bg-zinc-800 px-3 py-1 text-[10px] font-medium uppercase tracking-wide text-zinc-400">
        {label}
      </div>
      <pre className={`overflow-x-auto bg-zinc-900 p-3 text-xs leading-relaxed ${toneClasses}`}>
        <code>{children}</code>
      </pre>
    </div>
  );
}

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionError, setSessionError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    createSession()
      .then(setSessionId)
      .catch(() => setSessionError("Could not reach the backend. Is it running?"));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function submitMessage(userMessage: string) {
    if (!sessionId || !userMessage.trim() || loading) return;

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

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    submitMessage(input.trim());
  }

  async function handleFileSelected(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file || !sessionId || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: `Uploaded file: ${file.name}` }]);
    setLoading(true);

    try {
      const result = await uploadCsv(sessionId, file);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Loaded \`${file.name}\` into a DataFrame called \`${result.variable}\`.`,
          stdout: result.stdout,
          traceback: result.traceback,
        },
      ]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "Failed to upload the file." }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-screen flex-col bg-zinc-50 dark:bg-zinc-950">
      <header className="border-b border-black/5 bg-white/80 backdrop-blur dark:border-white/5 dark:bg-zinc-950/80">
        <div className="mx-auto max-w-2xl px-4 py-4 sm:px-6">
          <h1 className="text-lg font-semibold tracking-tight">charissa</h1>
          <p className="text-sm text-zinc-500">a conversational data engineering assistant</p>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-2xl px-4 py-6 sm:px-6">
          {sessionError && (
            <p className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600 dark:bg-red-950 dark:text-red-400">
              {sessionError}
            </p>
          )}

          {messages.length === 0 && !sessionError && (
            <div className="flex flex-col items-center gap-4 py-16 text-center">
              <p className="text-sm text-zinc-500">Coba tanyakan sesuatu tentang data-mu, misalnya:</p>
              <div className="flex flex-col gap-2">
                {EXAMPLE_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => submitMessage(prompt)}
                    disabled={!sessionId}
                    className="rounded-full border border-black/10 bg-white px-4 py-2 text-sm text-zinc-700 shadow-sm transition hover:border-blue-400 hover:text-blue-600 disabled:opacity-50 dark:border-white/10 dark:bg-zinc-900 dark:text-zinc-300"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
              <p className="text-xs text-zinc-400">
                atau upload CSV kamu sendiri lewat tombol <span className="font-medium">+ CSV</span> di bawah
              </p>
            </div>
          )}

          <div className="space-y-6">
            {messages.map((message, i) => (
              <div
                key={i}
                className={"flex items-start gap-3 " + (message.role === "user" ? "flex-row-reverse" : "")}
              >
                <Avatar role={message.role} />
                <div
                  className={
                    "max-w-[85%] rounded-2xl px-4 py-2.5 text-sm shadow-sm sm:max-w-[80%] " +
                    (message.role === "user"
                      ? "rounded-tr-sm bg-blue-600 text-white"
                      : "rounded-tl-sm bg-white dark:bg-zinc-900")
                  }
                >
                  <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                  {message.code && (
                    <OutputBlock label="Code" tone="code">
                      {message.code}
                    </OutputBlock>
                  )}
                  {message.stdout && (
                    <OutputBlock label="Output" tone="ok">
                      {message.stdout}
                    </OutputBlock>
                  )}
                  {message.traceback && (
                    <OutputBlock label="Error" tone="error">
                      {message.traceback}
                    </OutputBlock>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex items-start gap-3">
                <Avatar role="assistant" />
                <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm bg-white px-4 py-3 shadow-sm dark:bg-zinc-900">
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.3s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.15s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-400" />
                </div>
              </div>
            )}
          </div>
          <div ref={bottomRef} />
        </div>
      </div>

      <div className="border-t border-black/5 bg-white/80 backdrop-blur dark:border-white/5 dark:bg-zinc-950/80">
        <form
          onSubmit={handleSubmit}
          className="mx-auto flex max-w-2xl flex-wrap items-center gap-2 px-4 py-3 sm:flex-nowrap sm:px-6"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={handleFileSelected}
          />
          <button
            type="button"
            title="Upload a CSV file"
            onClick={() => fileInputRef.current?.click()}
            disabled={!sessionId || loading}
            className="shrink-0 rounded-full border border-black/10 bg-white px-3 py-2.5 text-sm text-zinc-600 shadow-sm transition hover:border-blue-400 hover:text-blue-600 disabled:opacity-50 dark:border-white/10 dark:bg-zinc-900 dark:text-zinc-300"
          >
            + CSV
          </button>
          <input
            className="min-w-0 flex-1 rounded-full border border-black/10 bg-white px-4 py-2.5 text-sm shadow-sm outline-none transition focus:border-blue-400 disabled:opacity-50 dark:border-white/10 dark:bg-zinc-900"
            placeholder="Ask something about your data..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!sessionId || loading}
          />
          <button
            type="submit"
            className="shrink-0 rounded-full bg-blue-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 disabled:opacity-50"
            disabled={!sessionId || loading || !input.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
