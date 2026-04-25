"""
API Gateway — Unified entry point for all RAG microservices.
Routes requests to the correct backend service.
"""
import httpx
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger("gateway")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="RAG System — API Gateway",
    description="Unified API gateway routing to Graph-RAG, Vector-RAG, and Voice-RAG services.",
    version="0.1.0",
)

# Service registry — container names from docker-compose
SERVICES = {
    "graph": "http://graph-rag:8001",
    "vector": "http://vector-rag:8002",
    "voice": "http://voice-rag-server:5000/api",
}


@app.get("/health")
async def health():
    """Aggregated health check across all services."""
    results = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, base_url in SERVICES.items():
            try:
                health_path = "/health" if name != "voice" else "/models"  
                resp = await client.get(f"{base_url}{health_path}")
                results[name] = {"status": "up", "code": resp.status_code}
            except Exception as e:
                results[name] = {"status": "down", "error": str(e)}

    all_up = all(s["status"] == "up" for s in results.values())
    return {"gateway": "healthy", "services": results, "all_services_up": all_up}


@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request):
    """Reverse proxy to the target microservice."""
    if service not in SERVICES:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown service '{service}'. Available: {list(SERVICES.keys())}",
        )

    target_url = f"{SERVICES[service]}/{path}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            body = await request.body()
            headers = dict(request.headers)
            headers.pop("host", None)

            resp = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
                params=dict(request.query_params),
            )
            return JSONResponse(
                content=resp.json(),
                status_code=resp.status_code,
            )
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail=f"Service '{service}' is unreachable.")
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))
