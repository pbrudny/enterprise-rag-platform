# rag-platform frontend

React + TypeScript + Vite + Tailwind CSS web UI for the [rag-platform](../README.md) practice project — a browser front-end for the same flows as `rag demo`: pick a mock user, ask questions, and see the access context, injection scan, retrieved chunks, output validation, citations, and audit log.

See the root [README.md](../README.md#web-ui) for how to run this alongside the backend API.

```bash
npm install
cp .env.example .env.local   # first time only — points at the backend API
npm run dev                  # http://localhost:5173
npm run build
npm run test                 # Vitest + Testing Library
```
