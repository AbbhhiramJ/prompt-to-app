from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_build_rejects_empty_prompt():
    response = client.post("/api/build", json={"prompt": "   "})
    assert response.status_code == 400
