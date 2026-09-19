"""Minimal health endpoint.

Production Prompt -> App execution is performed by the connected host agent.
This deployed API deliberately does not accept provider credentials or execute model calls.
"""
from fastapi import FastAPI

app = FastAPI(title="Prompt -> App API")

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "agent-orchestrated"}
