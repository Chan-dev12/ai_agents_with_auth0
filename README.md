# AI Agents with Auth0 🔐🤖

An enterprise-grade AI agent application featuring a **FastAPI** backend, a **LangGraph**-powered agent, and a **React + Vite** frontend, secured end-to-end with **Auth0-based Role-Based Access Control (RBAC)**.

This project demonstrates how to build production-ready agentic AI systems where every request — from the chat UI down to individual agent tool calls — is authenticated and authorized.

---

## ✨ Features

- **Conversational AI Agent** — Built with LangGraph, supporting streaming responses and stateful multi-turn conversations.
- **Secure Authentication** — Auth0 handles login, session, and token management.
- **Role-Based Access Control (RBAC)** — Fine-grained permissions so different user roles (e.g. `admin`, `user`, `viewer`) can access different agent capabilities and data.
- **Streaming Chat UI** — React frontend with real-time streaming responses, optimistic UI updates, and auto-scroll.
- **Credentialed API Communication** — All frontend-to-backend requests are sent with credentials (cookies) included, so authenticated sessions persist securely.
- **FastAPI Backend** — Async, typed, and easily extensible with new agent endpoints or tools.

---

## 🏗️ Architecture

```
┌─────────────────┐        ┌──────────────────┐        ┌─────────────────┐
│  React + Vite    │  HTTP  │  FastAPI Backend  │        │     Auth0       │
│  Frontend         │◄─────►│  + LangGraph Agent │◄─────►│  (Auth & RBAC)  │
│  (Chat UI)         │  SSE  │                    │        │                 │
└─────────────────┘        └──────────────────┘        └─────────────────┘
```

1. The **frontend** authenticates the user via Auth0 (Universal Login / SPA SDK).
2. Auth0 issues a session/token containing the user's **roles and permissions**.
3. The **backend** validates the token on every request and enforces RBAC before invoking the **LangGraph agent**.
4. The agent streams responses back to the frontend via Server-Sent Events (SSE) / streaming.

---

## 🧰 Tech Stack

| Layer          | Technology                                  |
|----------------|----------------------------------------------|
| Frontend       | React, Vite, TypeScript, Tailwind CSS         |
| Agent Runtime  | LangGraph, LangChain                          |
| Backend        | FastAPI, Python                               |
| Auth & RBAC    | Auth0                                         |
| Streaming      | LangGraph SDK (`useStream`), SSE              |

---

## 📋 Prerequisites

- Node.js (v18+) and npm/yarn/pnpm
- Python 3.10+
- An [Auth0](https://auth0.com/) account with:
  - A configured Application (SPA) for the frontend
  - A configured API for the backend
  - Roles/permissions set up for RBAC (e.g. `admin`, `user`)

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/Chan-dev12/ai_agents_with_auth0.git
cd ai_agents_with_auth0
```

### 2. Backend setup

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```env
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=your-api-identifier
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
FRONTEND_ORIGIN=http://localhost:5173
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_HOST=http://localhost:8000
VITE_AUTH0_DOMAIN=your-tenant.auth0.com
VITE_AUTH0_CLIENT_ID=your-spa-client-id
VITE_AUTH0_AUDIENCE=your-api-identifier
```

Run the frontend:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

---

## 🔑 Auth0 RBAC Configuration

1. In the Auth0 Dashboard, enable **RBAC** and **Add Permissions in the Access Token** for your API.
2. Define roles (e.g. `admin`, `user`) under **User Management → Roles**.
3. Assign permissions to each role (e.g. `read:agent`, `manage:agent`, `admin:all`).
4. Assign roles to users under **User Management → Users → Roles**.
5. The backend reads the roles/permissions from the validated access token and enforces access per-endpoint or per-tool.

> ⚠️ Never commit your `.env` files or Auth0 client secrets to version control. Make sure they're listed in `.gitignore`.

---

## 📁 Project Structure

```
ai_agents_with_auth0/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app entrypoint
│   │   ├── agent/            # LangGraph agent definition & tools
│   │   ├── auth/             # Auth0 token validation & RBAC middleware
│   │   └── routes/           # API routes
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/       # Chat UI components
│   │   ├── lib/               # Utilities
│   │   └── App.tsx
│   ├── package.json
│   └── .env
├── .gitignore
└── README.md
```

---

## 🧪 Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

---

## 🛣️ Roadmap

- [ ] Add fine-grained tool-level authorization within the agent graph
- [ ] Add audit logging for agent actions
- [ ] Deploy with CI/CD (Docker + GitHub Actions)
- [ ] Add multi-tenant support

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 🙌 Acknowledgements

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Auth0](https://auth0.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
