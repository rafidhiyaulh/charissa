# charissa

A conversational data engineering assistant. Chat with your data, run generated code against real data sources (files, SQL, object storage), and get results back without writing code by hand.

Built as a learning project to practice designing and shipping a multi-service LLM-backed data platform: sandboxed code execution, multi-source data connectors, and a provider-agnostic LLM layer.

## Status

Early scaffolding, work in progress.

## Stack (planned)

- LLM: Google Gemini API (provider-agnostic interface, swappable)
- Backend: FastAPI
- Frontend: Next.js (Vercel)
- Execution: sandboxed code runner (container-based)
- Database: Postgres (Supabase/Neon)
- Storage: Cloudflare R2 / S3-compatible

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

## Known gotchas

- Some office/campus wifi blocks outbound port 5432 (Postgres), so `DATABASE_URL`
  connections (e.g. to Neon) can hang or time out on those networks even though
  the code is correct. If `scripts/check_db_connection.py` hangs, try a mobile
  hotspot to confirm it's a network policy issue, not a bug. This won't affect
  deployed environments (Fly.io, cloud providers) since they don't restrict
  outbound ports the way some corporate networks do.
