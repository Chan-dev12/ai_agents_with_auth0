# Assistant0 — Enterprise AI Agent with Auth0 RBAC & Security Hardening

A full-stack AI agent application demonstrating enterprise-grade security patterns for LLM applications: role-based access control, prompt injection defense, sensitive data protection, and secure document RAG — built with FastAPI, LangGraph, Ollama, Auth0, and React.

## Features

### 🔐 Authentication & Authorization
- **Auth0 session-based authentication** via `auth0-fastapi` SDK (login, callback, logout, profile)
- **Role-Based Access Control (RBAC)** enforced at both the REST API layer and inside AI agent tool calls
- **Auth0 FGA (Fine-Grained Authorization)** for document-level ownership and sharing permissions
- Case-insensitive role matching to handle inconsistent role capitalization from Auth0

### 🤖 AI Agent (LangGraph + Ollama)
- Local LLM inference via **Ollama** (`llama3.1`) — no external API costs, fully self-hosted
- **Deterministic tool routing**: sensitive operations (salary lookups, document search) are triggered by code-level pattern matching, never left to the LLM's own judgment — eliminating a whole class of hallucination and permission-bypass risks
- Async-safe implementation (Windows-compatible event loop handling for psycopg + LangGraph)

### 📄 Document RAG Pipeline
- Document upload → chunking (`RecursiveCharacterTextSplitter`) → embeddings (`nomic-embed-text` via Ollama) → storage in **Postgres + pgvector**
- Retrieval strictly filtered to documents the requesting user **owns or has been shared** — enforced before content ever reaches the LLM
- Retrieved content wrapped as `<untrusted_data>` and explicitly flagged to the model as non-instructional reference material

### 🛡️ LLM Security Hardening (OWASP Top 10 for LLM Applications)

| Vulnerability | Mitigation |
|---|---|
| **LLM01 — Prompt Injection** | Regex-based detection short-circuits before the LLM is invoked; malicious instructions embedded in messages or documents are never followed |
| **LLM02 — Sensitive Information Disclosure** | Role-gated tools, self-data isolation, reversible PII masking (see below), and a final output-scrubbing safety net for emails/SSNs/API keys |
| **LLM06 — Excessive Agency** | No tool-binding on the LLM — every sensitive tool call is triggered deterministically by application code, never by model discretion |
| **LLM07 — System Prompt Leakage** | Dedicated detection layer refuses to reveal internal instructions, security rules, or tool logic, even under direct or indirect probing |

### 🔒 Reversible PII Masking

A key design pattern in this project: sensitive values (emails, phone numbers) inside retrieved documents are **masked with placeholder tokens before the LLM ever processes them**, and only unmasked back to real values in the final response — after the user's access has already been verified. This means the LLM's own reasoning never touches real PII, while authorized users still get real data in their answers.

```
Real document:  "email id is chandruv@dotsolved.com"
LLM sees:       "email id is [EMAIL_a1b2c3]"
LLM responds:   "The email is [EMAIL_a1b2c3]"
User sees:      "The email is chandruv@dotsolved.com"
```

## Tech Stack

**Backend:** FastAPI · LangGraph · LangChain · Ollama · SQLModel · Postgres (pgvector) · Auth0 (auth0-fastapi) · Auth0 FGA · Docker

**Frontend:** React · Vite · TypeScript · Tailwind CSS v4 · shadcn/ui · LangGraph SDK

**Observability:** LangSmith tracing (optional)

## Architecture Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   React     │─────▶│   FastAPI    │─────▶│  LangGraph Dev   │
│  Frontend   │      │   Backend    │      │  Server (Agent)  │
│  (:3000)    │◀─────│   (:8000)    │◀─────│    (:2024)       │
└─────────────┘      └──────┬───────┘      └────────┬─────────┘
                             │                        │
                    ┌────────┴────────┐      ┌────────┴────────┐
                    │  Auth0 (login,  │      │  Ollama (local  │
                    │  sessions, RBAC)│      │  llama3.1 +     │
                    │  Auth0 FGA      │      │  nomic-embed)   │
                    └─────────────────┘      └─────────────────┘
                             │
                    ┌────────┴────────┐
                    │  Postgres +     │
                    │  pgvector       │
                    │  (Docker)       │
                    └─────────────────┘
```

## Prerequisites

- Python 3.13
- Node.js (for the frontend, Vite-based)
- Docker Desktop (for Postgres + pgvector)
- [Ollama](https://ollama.com) installed locally
- An Auth0 tenant with RBAC enabled

## Setup

### 1. Pull required Ollama models

```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

### 2. Start Postgres (via Docker)

```bash
cd backend
docker compose up -d
```

### 3. Configure environment variables

Create `backend/.env`:

```env
APP_BASE_URL=http://localhost:8000
FRONTEND_HOST=http://localhost:3000

# Auth0
AUTH0_DOMAIN=your-tenant.us.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_SECRET=a-long-random-string

# Auth0 FGA
FGA_STORE_ID=your-fga-store-id
FGA_CLIENT_ID=your-fga-client-id
FGA_CLIENT_SECRET=your-fga-client-secret

# Database
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/ai_documents_db

# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# LangGraph
LANGGRAPH_API_URL=http://127.0.0.1:2024

# LangSmith (optional, for tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=assistant0-dev
```

Create `frontend/.env`:

```env
VITE_API_HOST=http://localhost:8000
```

### 4. Set up Auth0

1. Create an Auth0 Application (Regular Web App)
2. Add **Allowed Callback URLs**: `http://localhost:8000/auth/callback`
3. Add **Allowed Logout URLs** and **Allowed Web Origins**: `http://localhost:3000`
4. Under **Actions → Triggers → post-login**, add a custom action to inject roles:

```javascript
exports.onExecutePostLogin = async (event, api) => {
  const namespace = 'https://yourapp.com';
  if (event.authorization) {
    api.idToken.setCustomClaim(`${namespace}/roles`, event.authorization.roles);
    api.accessToken.setCustomClaim(`${namespace}/roles`, event.authorization.roles);
  }
};
```

5. Enable **RBAC** and **Add Permissions in the Access Token** under your Auth0 API settings
6. Create roles (`Admin`, `Manager`, `Employee`) and assign them to test users

### 5. Initialize the database

```bash
cd backend
python create_db.py
```

### 6. Run the backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 7. Run the LangGraph agent server

```bash
cd backend
langgraph dev
```

### 8. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`.

## Project Structure

```
backend/
├── app/
│   ├── agents/
│   │   └── assistant0.py       # LangGraph agent: tools, routing, security layers
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py         # Proxies chat requests to LangGraph, injects user context
│   │   │   ├── documents.py    # Document upload/share/delete (RBAC + FGA protected)
│   │   │   └── salary.py       # Example RBAC-protected REST endpoints
│   │   └── api_router.py
│   ├── core/
│   │   ├── auth.py             # Auth0 session handling, require_role() dependency
│   │   ├── config.py           # Pydantic settings
│   │   ├── db.py               # Database engine
│   │   ├── fga.py              # Auth0 FGA authorization manager
│   │   ├── pii_masking.py      # Reversible PII mask/unmask utilities
│   │   └── rag.py              # Embedding generation + document retrieval
│   └── models/                 # SQLModel table definitions
├── create_db.py
├── docker-compose.yml
└── langgraph.json

frontend/
├── src/
│   ├── components/
│   │   ├── chat-window.tsx
│   │   ├── chat-message-bubble.tsx
│   │   └── ui/                 # shadcn/ui components
│   ├── pages/
│   │   ├── ChatPage.tsx
│   │   └── DocumentsPage.tsx
│   └── lib/
│       └── use-auth.ts
```

## Security Notes

This project is a **learning/demonstration environment** for LLM application security patterns. Before any production use:

- Replace the hardcoded `SALARY_DATA` mock in `assistant0.py` with real database-backed records and per-row access checks
- Remove debug `traceback.print_exc()` calls
- Add rate limiting (LLM10 — Unbounded Consumption is not yet addressed)
- Review dependencies for known vulnerabilities (LLM03 — Supply Chain)
- Add validation/scanning on document uploads (LLM04 — Data Poisoning is only partially mitigated)

## License

MIT
