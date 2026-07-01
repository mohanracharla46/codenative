"""
CodeNative Load Balancer — migrated from Flask to FastAPI.

Distributes traffic across backend instances using round-robin, with
background health checks every 5 seconds using asyncio.
"""
import os
import asyncio
import threading

import httpx

from fastapi import FastAPI, Request
from fastapi.responses import Response, StreamingResponse

app = FastAPI()

# Configurable backend ports (can be overridden by environment variables)
BACKENDS = [
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
    "http://127.0.0.1:8003",
]

# Thread safety lock for active_backends list
_backends_lock = threading.Lock()
_active_backends: list = list(BACKENDS)
_current_index: int = 0


# ─── Background health checker ────────────────────────────────────────────────
async def _health_check_loop():
    """Periodically check the health of each backend server."""
    global _active_backends
    print("[Health Checker] Started background check daemon.")
    while True:
        healthy = []
        async with httpx.AsyncClient(timeout=2.0) as client:
            for backend in BACKENDS:
                try:
                    resp = await client.get(backend)
                    if resp.status_code < 500:
                        healthy.append(backend)
                except Exception:
                    pass  # backend is down — skip

        with _backends_lock:
            _active_backends = healthy

        await asyncio.sleep(5)  # re-check every 5 seconds


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(_health_check_loop())


# ─── Proxy route ──────────────────────────────────────────────────────────────
@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def load_balancer_proxy(path: str, request: Request):
    global _current_index

    with _backends_lock:
        healthy_servers = list(_active_backends)

    if not healthy_servers:
        return Response(
            content="Service Temporarily Unavailable — No healthy backend server instances found.",
            status_code=503,
            media_type="text/plain",
        )

    # Round-robin backend selection
    backend = healthy_servers[_current_index % len(healthy_servers)]
    _current_index = (_current_index + 1) % len(healthy_servers)

    # Build destination URL
    url = f"{backend}/{path}"
    qs  = request.url.query
    if qs:
        url += f"?{qs}"

    # Forward all headers except hop-by-hop
    excluded_headers = {
        "host", "content-length", "connection", "keep-alive",
        "proxy-authenticate", "proxy-authorization", "te",
        "trailers", "transfer-encoding", "upgrade",
    }
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in excluded_headers
    }

    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                cookies=dict(request.cookies),
                follow_redirects=False,
            )

        # Strip hop-by-hop headers from the response before returning
        resp_headers = {
            k: v for k, v in resp.headers.items()
            if k.lower() not in excluded_headers
        }

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=resp_headers,
        )

    except httpx.RequestError as e:
        print(f"[Load Balancer] Failed to connect to backend {backend}: {e}")
        with _backends_lock:
            if backend in _active_backends:
                _active_backends.remove(backend)
        return Response(
            content=f"Bad Gateway — Connection to backend instance {backend} failed.",
            status_code=502,
            media_type="text/plain",
        )


# ─── Entrypoint ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    print("=" * 60)
    print(f"CodeNative Load Balancer initialized on http://127.0.0.1:{port}")
    print(f"Distributing requests across: {', '.join(BACKENDS)}")
    print("=" * 60)
    uvicorn.run("load_balancer:app", host="0.0.0.0", port=port, reload=False)
