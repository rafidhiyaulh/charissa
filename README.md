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

1. Copy `.env.example` to `.env` and fill in `GEMINI_API_KEY`.
2. (More setup instructions land here as pieces get built.)
