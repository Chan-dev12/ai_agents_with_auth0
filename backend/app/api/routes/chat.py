import json
import httpx
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.config import settings
from app.core.auth import auth_client, ROLES_CLAIM

agent_router = APIRouter(prefix="/agent", tags=["agent"])


@agent_router.api_route(
    "/{full_path:path}", methods=["GET", "POST", "DELETE", "PATCH", "PUT", "OPTIONS"]
)
async def api_route(
    request: Request,
    full_path: str,
    auth_session=Depends(auth_client.require_session),
):
    try:
        user = auth_session.get("user") or {}
        user_roles = user.get(ROLES_CLAIM, [])

        # Build target URL
        query_string = str(request.url.query)
        target_url = f"{settings.LANGGRAPH_API_URL}/{full_path}"
        if query_string:
            target_url += f"?{query_string}"

        # Prepare headers
        headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower().startswith("x-") or k.lower() == "authorization"
        }
        headers["x-api-key"] = settings.LANGGRAPH_API_KEY

        # Prepare body
        body = await request.body()
        if request.method in ("POST", "PUT", "PATCH") and body:
            content = await request.json()
            configurable = content.setdefault("config", {}).setdefault("configurable", {})
            configurable["_credentials"] = {}
            configurable["user_roles"] = user_roles
            configurable["user_email"] = user.get("email")
            configurable["user_sub"] = user.get("sub")  # needed to check document ownership
            body = json.dumps(content).encode("utf-8")

        # Stream the response back
        async def stream_response():
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body if request.method in ("POST", "PUT", "PATCH") else None,
                ) as proxied_response:
                    if proxied_response.status_code >= 400:
                        response_text = await proxied_response.aread()
                        raise HTTPException(
                            status_code=proxied_response.status_code,
                            detail=response_text.decode(),
                        )

                    async for chunk in proxied_response.aiter_bytes():
                        yield chunk

        return StreamingResponse(
            stream_response(),
            status_code=200,
            media_type=request.headers.get("content-type", "application/json"),
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})