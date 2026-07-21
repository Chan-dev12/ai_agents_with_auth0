# Assistant0

**An enterprise-grade AI agent reference implementation demonstrating secure LLM application architecture with Auth0.**

Assistant0 combines a LangGraph-based conversational agent with role-based access control, retrieval-augmented generation, and a layered defense strategy against common LLM security vulnerabilities, built entirely on a self-hosted, open-source stack.

---

## Overview

This project serves as a practical reference for building production-minded AI agents where **authorization and data protection are enforced in application code, not delegated to the language model's judgment.** Every sensitive operation — salary lookups, document retrieval, role-gated actions — is routed deterministically, with the LLM used strictly for language understanding and generation rather than access control decisions.

## Core Capabilities

### Identity & Access Management
- Session-based authentication via Auth0, with secure login, callback, and logout flows
- Role-Based Access Control (RBAC) enforced at both the API layer and within individual agent tool calls
- Fine-Grained Authorization (Auth0 FGA) governing document ownership and sharing relationships
- Resilient, case-insensitive role matching to accommodate inconsistent identity provider data

### Conversational Agent
- Self-hosted LLM inference via Ollama (Llama 3.1), eliminating dependency on third-party inference APIs
- Deterministic tool invocation — sensitive actions are triggered by application logic rather than model discretion, closing a significant class of prompt-injection and hallucination risk
- Fully asynchronous execution path, including Windows-compatible event loop configuration for the async Postgres driver

### Document Intelligence (RAG)
- Document ingestion pipeline: chunking, embedding (Ollama `nomic-embed-text`), and vector storage (Postgres with pgvector)
- Retrieval scoped exclusively to documents the requesting user owns or has been granted access to, enforced prior to any LLM invocation
- Retrieved content is explicitly demarcated as untrusted, non-instructional data to the model

### LLM Security Controls

This implementation directly addresses several categories from the **OWASP Top 10 for LLM Applications**:

| Category | Control |
|---|---|
| Prompt Injection | Pattern-based detection intercepts adversarial instructions before they reach the model |
| Sensitive Information Disclosure | Role-scoped tool access, self-record isolation, reversible PII masking, and output-level redaction as a final safeguard |
| Excessive Agency | The model is never bound to tools directly; all sensitive operations are routed by deterministic application logic |
| System Prompt Leakage | Dedicated detection prevents disclosure of internal instructions under both direct and indirect probing |

### Reversible PII Masking

A distinguishing feature of this implementation: personally identifiable information retrieved from documents is tokenized before being passed to the language model, and restored to its original value only in the final response — after the requesting user's authorization has already been verified.

```
Source document   ->  "email id is chandruv@dotsolved.com"
Model receives     ->  "email id is [EMAIL_a1b2c3]"
Model responds      ->  "The email is [EMAIL_a1b2c3]"
User receives        ->  "The email is chandruv@dotsolved.com"
```

This ensures the model's reasoning process never has access to real personal data, while authorized end users still receive complete, accurate answers.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| Backend | FastAPI, LangGraph, LangChain, SQLModel |
| AI / ML | Ollama (Llama 3.1, nomic-embed-text) |
| Data | PostgreSQL with pgvector, Docker |
| Identity | Auth0, Auth0 FGA |
| Frontend | React, Vite, TypeScript, Tailwind CSS, shadcn/ui |
| Observability | LangSmith (optional) |

---

## Architecture

```
                 React              FastAPI              LangGraph
                Frontend    ---->    Backend    ---->    Agent Server
                 :3000      <----     :8000     <----      :2024
                                        |                     |
                                 Auth0 Sessions          Ollama
                                 Auth0 FGA               (local inference)
                                        |
                                  PostgreSQL
                                  + pgvector
```

---

## Getting Started

### Prerequisites

- Python 3.13
- Node.js
- Docker Desktop
- [Ollama](https://ollama.com)
- An Auth0 tenant with RBAC enabled

### 1. Install required models

```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

### 2. Start the database

```bash
cd backend
docker compose up -d
```

### 3. Configure environment variables

**`backend/.env`**

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

# LangSmith (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=assistant0-dev
```

**`frontend/.env`**

```env
VITE_API_HOST=http://localhost:8000
```

### 4. Configure Auth0

1. Create a Regular Web Application in your Auth0 dashboard
2. Set **Allowed Callback URLs** to `http://localhost:8000/auth/callback`
3. Set **Allowed Logout URLs** and **Allowed Web Origins** to `http://localhost:3000`
4. Under **Actions -> Triggers -> post-login**, add a custom action to embed role claims:

   ```javascript
   exports.onExecutePostLogin = async (event, api) => {
     const namespace = 'https://yourapp.com';
     if (event.authorization) {
       api.idToken.setCustomClaim(`${namespace}/roles`, event.authorization.roles);
       api.accessToken.setCustomClaim(`${namespace}/roles`, event.authorization.roles);
     }
   };
   ```

5. Enable RBAC and "Add Permissions in the Access Token" in your Auth0 API settings
6. Define roles (`Admin`, `Manager`, `Employee`) and assign them to test accounts

### 5. Initialize the database schema

```bash
cd backend
python create_db.py
```

### 6. Run the application

Three processes run concurrently, each in its own terminal:

```bash
# Backend API
cd backend
uvicorn app.main:app --reload

# Agent server
cd backend
langgraph dev

# Frontend
cd frontend
npm install
npm run dev
```

Navigate to `http://localhost:3000`.

---

## Project Structure

```
backend/
  app/
    agents/
      assistant0.py       # Agent definition, routing logic, security layers
    api/
      routes/
        chat.py            # Chat proxy; injects authenticated user context
        documents.py        # Document management (RBAC + FGA)
        salary.py            # Example RBAC-protected endpoints
      api_router.py
    core/
      auth.py               # Auth0 session handling and role dependencies
      config.py              # Application settings
      db.py                    # Database engine configuration
      fga.py                    # Auth0 FGA client
      pii_masking.py             # PII tokenization utilities
      rag.py                      # Embedding generation and retrieval
    models/                        # Data models
  create_db.py
  docker-compose.yml
  langgraph.json

frontend/
  src/
    components/
    pages/
    lib/
```

---

## Production Considerations

This project is intended as a security-focused reference implementation. Before deploying in a production context, consider addressing the following:

- Replace mock data structures with database-backed records subject to row-level authorization
- Remove diagnostic logging retained from development
- Implement rate limiting to mitigate unbounded resource consumption
- Conduct a dependency audit for known vulnerabilities
- Introduce content validation for document ingestion to reduce data-poisoning exposure

## License

MIT
