# 🤖 Assistant0 - Complete Project Analysis & Setup Guide

## Project Overview

**Assistant0** is an AI-powered personal assistant application that consolidates your digital life. It features:
- ✅ Authentication with **Auth0**
- ✅ Fine-grained authorization with **Auth0 FGA**
- ✅ LLM-based agent with **LangGraph**
- ✅ Document upload & RAG (Retrieval-Augmented Generation)
- ✅ Real-time chat interface
- ✅ PostgreSQL with vector embeddings

---

## 📋 Architecture

### Backend (Python/FastAPI)
- **Port**: 8000
- **Framework**: FastAPI + LangGraph
- **Database**: PostgreSQL with pgvector
- **Auth**: Auth0 + FGA
- **LLM**: OpenAI GPT-4o-mini
- **Key Files**:
  - `app/main.py` - FastAPI app initialization
  - `app/agents/assistant0.py` - LangGraph agent config
  - `app/api/routes/chat.py` - Chat proxy to LangGraph
  - `app/core/config.py` - Configuration settings

### Frontend (React/TypeScript/Vite)
- **Port**: 5173
- **Framework**: React 19 + Vite + TailwindCSS
- **Key Features**:
  - Chat interface with streaming responses
  - Document management
  - Auth0 authentication
  - Real-time communication with backend

### LangGraph Server
- **Port**: 2024 (configured in .env as LANGGRAPH_API_URL)
- **Purpose**: Runs the AI agent in-memory
- **Graph**: Defined in `langgraph.json`

### Database
- **PostgreSQL** running in Docker container
- **Port**: 5433
- **Database**: `ai_documents_db`
- **Credentials**: `postgres:postgres`
- **Extensions**: pgvector (for embeddings)

---

## ✅ Current Status

### ✔ Already Running
1. **PostgreSQL Database** - Docker container is running
   - Check: `docker ps | grep postgres`
   - Connection: `localhost:5433`

2. **Frontend Dev Server** - Vite running on port 5173
   - Terminal: `esbuild`
   - Status: Ready

3. **Backend HTTP Server** - FastAPI running on port 8000
   - Terminal: `uvicorn`
   - Status: Running but waiting for LangGraph

### ⚠️ Services to Start
1. **LangGraph Dev Server** - NOT YET RUNNING
   - Command: `langgraph dev --port 2024 --allow-blocking`
   - Required before API calls work
   - Terminal: `langgraph`

2. **API Verification** - Need to verify health

---

## 🚀 Complete Startup Sequence

### Step 1: Verify Database is Running
```bash
docker ps
# Should see: postgres_pgvector container running on port 5433
```

### Step 2: Start LangGraph Server (NEW TERMINAL)
```bash
cd backend
source .venv/bin/activate  # Windows: .venv\Scripts\activate
langgraph dev --port 2024 --allow-blocking
```
Expected output:
```
✓ Graph "agent" compiled successfully
✓ Ready at http://localhost:2024/
```

### Step 3: Verify All Services
```bash
# Test Database
psql -h localhost -p 5433 -U postgres -d ai_documents_db

# Test Backend
curl http://localhost:8000/docs

# Test LangGraph
curl http://127.0.0.1:2024/docs

# Test Frontend
Open browser: http://localhost:5173
```

---

## 📊 Service Status Checklist

| Service | Port | Status | Command | Terminal |
|---------|------|--------|---------|----------|
| PostgreSQL | 5433 | ✅ Running | Docker | - |
| FastAPI | 8000 | ✅ Running | `fastapi dev app/main.py` | uvicorn |
| LangGraph | 2024 | ❌ PENDING | `langgraph dev --port 2024` | langgraph |
| Frontend | 5173 | ✅ Running | `npm run dev` | esbuild |

---

## 🔧 Configuration Overview

### Backend Environment Variables (.env)
```ini
# Application
APP_BASE_URL=http://localhost:8000

# Auth0
AUTH0_DOMAIN=dev-vvf7b7nqzf3wrfir.us.auth0.com
AUTH0_CLIENT_ID=6bvtoK1h6kpSGVu2z5dUhRiDDMD8vVKu
AUTH0_CLIENT_SECRET=[configured]
AUTH0_SECRET=[configured]

# OpenAI
OPENAI_API_KEY=[configured]

# Database
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/ai_documents_db

# LangGraph
LANGGRAPH_API_URL=http://127.0.0.1:2024

# Auth0 FGA
FGA_STORE_ID=[configured]
FGA_CLIENT_ID=[configured]
FGA_CLIENT_SECRET=[configured]
FGA_API_URL=https://api.us1.fga.dev
```

### Frontend Environment Variables (.env)
```ini
LANGGRAPH_API_URL=http://127.0.0.1:2024
```

---

## 📝 Project Dependencies

### Backend (Python)
- `fastapi[standard]>=0.115.14` - Web framework
- `langgraph>=0.5.4` - Agent orchestration
- `langchain-openai>=0.3.28` - LLM integration
- `auth0-fastapi>=1.0.0b5` - Auth0 integration
- `openfga-sdk>=0.9.5` - Fine-grained authorization
- `sqlmodel>=0.0.24` - ORM
- `psycopg>=3.2.9` - PostgreSQL driver
- `langchain-postgres>=0.0.15` - PostgreSQL vector store

### Frontend (Node)
- `react@^19.2.1` - UI framework
- `@langchain/langgraph-sdk@^0.0.101` - LangGraph client
- `react-router@^7.7.0` - Routing
- `axios@^1.15.2` - HTTP client
- `tailwindcss@^4.1.11` - Styling

---

## 🔄 API Endpoints

### Agent Routes
- `GET/POST /api/agent/*` - Proxies to LangGraph server
- All requests forward to `http://127.0.0.1:2024/agent/*`

### Chat Routes
- `POST /api/chat` - Send chat messages
- `GET /api/chat/history` - Get chat history
- Streaming responses supported

### Document Routes
- `POST /api/documents/upload` - Upload documents
- `GET /api/documents` - List documents
- `DELETE /api/documents/{id}` - Delete document

### Auth Routes
- `POST /api/auth/login` - Login endpoint
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

---

## 🐛 Troubleshooting

### Issue: "Connection refused" on LangGraph calls
**Solution**: Start LangGraph server
```bash
cd backend && langgraph dev --port 2024 --allow-blocking
```

### Issue: "Database connection error"
**Solution**: Verify PostgreSQL is running
```bash
docker compose -f backend/docker-compose.yml up -d
```

### Issue: "Auth0 error" or "FGA error"
**Solution**: Verify .env variables are correct
```bash
cat backend/.env | grep AUTH0
cat backend/.env | grep FGA
```

### Issue: Frontend can't connect to backend
**Solution**: Check CORS and backend URL
- Frontend: http://localhost:5173 ✓
- Backend: http://localhost:8000 ✓
- LangGraph: http://127.0.0.1:2024 ✓

---

## 📦 Full Startup Command (All Services)

### Terminal 1: PostgreSQL (already running)
```bash
# Already running in Docker via: docker compose up -d
```

### Terminal 2: LangGraph Server
```bash
cd backend
source .venv/bin/activate
langgraph dev --port 2024 --allow-blocking
```

### Terminal 3: Backend FastAPI (already running)
```bash
# Already running with: fastapi dev app/main.py
```

### Terminal 4: Frontend (already running)
```bash
# Already running with: npm run dev
```

### Access Points
- 🌐 Frontend: **http://localhost:5173**
- 📡 Backend API: **http://localhost:8000/docs**
- 🔗 LangGraph Studio: **http://localhost:2024/docs**

---

## 🎯 Next Steps

1. **Start LangGraph Server** (CRITICAL)
   ```bash
   cd backend && langgraph dev --port 2024 --allow-blocking
   ```

2. **Verify All Services**
   - Open http://localhost:8000/docs
   - Check all endpoints return responses
   - Open http://localhost:5173 in browser

3. **Test Chat Functionality**
   - Go to chat page
   - Send a test message
   - Verify it proxies through to LangGraph

4. **Monitor Logs**
   - Backend: uvicorn terminal
   - Frontend: esbuild terminal
   - LangGraph: langgraph terminal

---

## 📚 Key Files Reference

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app entry point |
| `backend/app/agents/assistant0.py` | LangGraph agent definition |
| `backend/app/api/api_router.py` | API route registration |
| `backend/app/api/routes/chat.py` | Chat endpoint proxy |
| `backend/app/core/config.py` | Configuration loader |
| `backend/app/core/db.py` | Database initialization |
| `backend/app/core/auth.py` | Auth0 integration |
| `backend/app/core/fga.py` | FGA authorization |
| `frontend/src/main.tsx` | React app entry point |
| `frontend/src/pages/ChatPage.tsx` | Chat UI component |
| `langgraph.json` | LangGraph configuration |

---

## ✨ Features

✅ **Authentication**: Auth0 OAuth2  
✅ **Authorization**: Auth0 FGA  
✅ **AI Agent**: LangGraph with tool use  
✅ **Streaming**: Real-time chat responses  
✅ **Documents**: RAG with pgvector  
✅ **Database**: PostgreSQL with vector embeddings  
✅ **Type Safety**: TypeScript + Pydantic  
✅ **UI Components**: Radix UI + Tailwind  

