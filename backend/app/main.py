from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.api.api_router import api_router
from app.core.auth import auth_client, auth_router
from app.core.db import engine, init_db
from app.core.fga import authorization_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("1. Starting database...")
    try:
        init_db()
        print("2. Database initialized")
    except Exception as exc:
        print(f"2. Database initialization skipped: {exc}")

    print("3. Connecting to FGA...")
    try:
        authorization_manager.connect()
        print("4. FGA connected")
    except Exception as exc:
        print(f"4. FGA connection skipped: {exc}")

    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALL_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the session middleware
app.add_middleware(SessionMiddleware, secret_key=settings.AUTH0_SECRET)

# Save auth state
app.state.auth_client = auth_client

# Include auth routes at root level
app.include_router(auth_router, tags=["auth"])

# Include API routes
app.include_router(api_router, prefix=settings.API_PREFIX)
