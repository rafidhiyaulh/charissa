# charissa

A conversational data engineering assistant. Chat with your data, run generated code against real data sources (files, SQL), and get results back without writing code by hand — live at [charissa-eta.vercel.app](https://charissa-eta.vercel.app).

Built as a learning project to practice designing and shipping a multi-service LLM-backed data platform, with a focus on the problem most companies actually face when adopting AI for data work: how do you let an LLM run generated code against your data without handing that data to a third party.

## Who this is for

Charissa isn't built for the general public — it's built for organizations that
want AI-assisted data analysis but can't send their data to a third-party
service. Financial, healthcare, and government teams need that help but are
bound by compliance requirements that rule out tools like ChatGPT for anything
touching sensitive data. Charissa's architecture — self-hosted, a network-isolated
sandbox, and connectors straight into a private database — exists specifically
to answer that constraint: the LLM writes and runs code against your data, but
the data itself never leaves infrastructure you control.

## Status

Deployed end-to-end: Next.js frontend on Vercel, FastAPI backend on a self-managed VPS, sandboxed code execution, multi-source data connectors, and an audit trail.

## Architecture

```
Browser
  │  HTTPS
  ▼
Next.js frontend (Vercel)
  │  HTTPS
  ▼
Caddy (auto TLS) → FastAPI backend (VPS)
  │                       │
  ▼                       ▼
Gemini API          Docker sandbox (network-isolated, one per session)
                          │
                          ▼
                    Postgres / CSV data sources
```

- **LLM layer**: provider-agnostic interface (`charissa/llm`), currently backed by Gemini.
- **Execution**: each chat session gets its own Docker container with networking fully disabled — generated code can read the data it's given but can't reach the internet.
- **Data connectors**: CSV and Postgres. Credentials and queries stay on the trusted host; only the resulting rows are ever handed to the sandbox.
- **Session lifecycle**: idle sessions are swept and their containers torn down automatically, so the service doesn't accumulate resources under real usage.
- **Access control**: optional API key gate (`API_KEYS`) — a no-op in local dev, enforceable in a real deployment.
- **Audit log**: every chat turn (message, generated code, output) is persisted to Postgres, independent of the ephemeral sandbox, so there's a durable trail of what ran against what data.

## Setup

1. Copy `backend/.env.example` to `backend/.env` and fill in `GEMINI_API_KEY`.
2. `cd backend && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"`
3. Run tests: `.venv/bin/pytest -v`
4. Run the API: `.venv/bin/uvicorn charissa.api.app:app --reload`
5. In another terminal: `cd frontend && cp .env.example .env.local && npm install && npm run dev`, then open http://localhost:3000

## API

- `POST /sessions` - start a new chat session (spins up an isolated sandbox)
- `POST /sessions/{id}/chat` - send a message, get back the agent's reply, code, and execution result
- `DELETE /sessions/{id}` - close a session and tear down its sandbox

All three require `X-API-Key` header if `API_KEYS` is set in the environment.

## Known gotchas

- Some office/campus wifi blocks outbound ports 5432 (Postgres) and 22 (SSH), so
  `DATABASE_URL` connections or SSH access can hang or time out on those networks
  even though the code/server is fine. If something hangs, try a mobile hotspot
  to confirm it's a network policy issue, not a bug. This doesn't affect the
  deployed environment itself, only debugging from a restrictive network.
