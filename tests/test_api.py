from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_text_evidence_offsets():
    src = "欢迎。未来已来。"
    response = client.post("/v1/inspect", json={"modality": "text", "content": src})
    assert response.status_code == 200
    issue = response.json()["issues"][0]
    assert src[issue["start"]:issue["end"]] == issue["evidence"]

def test_ui_a11y():
    html = '<html><body><img src="x"><input id="email"></body></html>'
    response = client.post("/v1/inspect", json={"modality": "ui", "content": html})
    assert response.status_code == 200
    codes = {i["code"] for i in response.json()["issues"]}
    assert {"ui.image.alt", "ui.form.label", "ui.document.lang", "ui.landmark.main"} <= codes

def test_invalid_mode():
    assert client.post("/v1/inspect", json={"modality": "video", "content": "x"}).status_code == 422

def test_empty_input():
    assert client.post("/v1/inspect", json={"modality": "text", "content": ""}).status_code == 422
