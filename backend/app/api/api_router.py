# # from fastapi import APIRouter
# # from app.api.routes.chat import agent_router
# # from app.api.routes.documents import documents_router

# # api_router = APIRouter()

# # api_router.include_router(agent_router)
# # api_router.include_router(documents_router)

# from fastapi import APIRouter, Depends

# from app.api.routes.chat import agent_router
# from app.api.routes.documents import documents_router
# from app.core.auth import auth_router, require_role, get_current_user

# api_router = APIRouter()

# # Public auth routes (login, callback, logout, profile) — no role restriction
# api_router.include_router(auth_router)

# # Protected routes — require any authenticated user (adjust roles per router as needed)
# api_router.include_router(
#     agent_router,
#     dependencies=[Depends(get_current_user)],
# )

# api_router.include_router(
#     documents_router,
#     dependencies=[Depends(require_role("admin", "manager", "employee"))],
# )
# from fastapi import APIRouter

# from app.api.routes.salary import salary_router
# from app.core.auth import auth_router

# api_router = APIRouter()

# api_router.include_router(auth_router)
# api_router.include_router(agent_router)
# api_router.include_router(documents_router)
# api_router.include_router(salary_router)
from fastapi import APIRouter, Depends

from app.api.routes.chat import agent_router
from app.api.routes.documents import documents_router
from app.api.routes.salary import salary_router
from app.core.auth import auth_router, require_role

api_router = APIRouter()

# Public auth routes (login, callback, logout, profile) — no role restriction
api_router.include_router(auth_router)

# Protected routes — require any authenticated user
api_router.include_router(agent_router)

api_router.include_router(
    documents_router,
    dependencies=[Depends(require_role("admin", "manager", "employee"))],
)

api_router.include_router(salary_router)