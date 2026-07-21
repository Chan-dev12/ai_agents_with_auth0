from urllib.parse import urlparse

from auth0_fastapi.auth import AuthClient
from auth0_fastapi.config import Auth0Config
from auth0_fastapi.server.routes import router as auth_router
from fastapi import Request, Response, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse, RedirectResponse

from app.core.config import settings

auth_config = Auth0Config(
    domain=settings.AUTH0_DOMAIN,
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    secret=settings.AUTH0_SECRET,
    app_base_url=settings.APP_BASE_URL,
    mount_routes=False,
    mount_connect_routes=True,
    authorization_params={
        "scope": "openid profile email offline_access",
    },
)

auth_client = AuthClient(auth_config)

# Namespace must match the custom claim you set in your Auth0 Action
ROLES_CLAIM = "https://yourapp.com/roles"


def _safe_frontend_redirect(return_to: str | None) -> str:
    frontend_url = settings.FRONTEND_HOST.rstrip("/")
    if not return_to:
        return frontend_url

    parsed_return_to = urlparse(return_to)
    parsed_frontend = urlparse(frontend_url)

    if parsed_return_to.scheme and parsed_return_to.netloc:
        if (
            parsed_return_to.scheme == parsed_frontend.scheme
            and parsed_return_to.netloc == parsed_frontend.netloc
        ):
            return return_to
        return frontend_url

    if return_to.startswith("/"):
        return f"{frontend_url}{return_to}"

    return frontend_url


@auth_router.get("/auth/login")
async def login(request: Request, response: Response):
    return_to = request.query_params.get("returnTo")
    authorization_params = {
        k: v for k, v in request.query_params.items() if k != "returnTo"
    }
    auth_url = await auth_client.start_login(
        app_state={"returnTo": return_to} if return_to else None,
        authorization_params=authorization_params,
        store_options={"response": response},
    )
    return RedirectResponse(url=auth_url, headers=response.headers)


@auth_router.get("/auth/callback")
async def callback(request: Request, response: Response):
    full_callback_url = str(request.url)
    try:
        session_data = await auth_client.complete_login(
            full_callback_url,
            store_options={"request": request, "response": response},
        )
        if isinstance(session_data, dict):
            app_state = session_data.get("app_state", {}) or {}
        else:
            app_state = getattr(session_data, "app_state", {}) or {}
        return_to = app_state.get("returnTo") if isinstance(app_state, dict) else None
        redirect_url = _safe_frontend_redirect(return_to)
        return RedirectResponse(url=redirect_url, headers=response.headers)
    except Exception as exc:
        return PlainTextResponse(content=f"Callback error: {exc}", status_code=500)


@auth_router.get("/auth/logout")
async def logout(request: Request, response: Response):
    return_to = request.query_params.get("returnTo")
    logout_url = await auth_client.logout(
        return_to=_safe_frontend_redirect(return_to),
        store_options={"response": response},
    )
    return RedirectResponse(url=logout_url, headers=response.headers)


@auth_router.get("/auth/profile")
async def get_profile(request: Request, response: Response):
    store_options = {"request": request, "response": response}
    session = await auth_client.client.get_session(store_options=store_options)
    if not session:
        return {"user": None}
    user = session.get("user") or {}
    return {
        "user": user,
        "roles": user.get(ROLES_CLAIM, []),
    }


def require_role(*allowed_roles: str):
    """
    Dependency to protect a route by role.
    Case-insensitive — matches regardless of how roles are capitalized in Auth0.
    Usage: Depends(require_role("admin", "manager"))
    """
    async def role_checker(auth_session=Depends(auth_client.require_session)):
        user = auth_session.get("user") or {}
        user_roles = [r.lower() for r in user.get(ROLES_CLAIM, [])]
        allowed = [r.lower() for r in allowed_roles]
        if not any(role in allowed for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this action",
            )
        return auth_session
    return role_checker