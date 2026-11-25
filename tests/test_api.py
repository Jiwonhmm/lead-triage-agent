from fastapi.testclient import TestClient

from app.main import app
from tests.test_graph import use_fake_llms

client = TestClient(app)


def test_submit_view_approve_flow(monkeypatch):
    use_fake_llms(monkeypatch, "hot")

    # 1) 제출: POST /leads
    response = client.post("/leads", json={"raw_text": "anything"})
    assert response.status_code == 200
    thread_id = response.json()["thread_id"]

    # 2) 조회: GET /leads/{thread_id} ->200
    response = client.get(f"/leads/{thread_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["waiting_for_approval"] is True
    assert body["reply_draft"] == "Hi, this is a draft."

    # 3) 승인: POST /leads/{thread_id}/approve
    response = client.post(f"/leads/{thread_id}/approve", json={"action": "approved"})
    assert response.status_code == 200
    assert response.json()["approval"] == "approved"


# return 404 test
def test_unknown_thread_returns_404():
    response = client.get("/leads/does-not-exist")  # 실행: 없는 번호로 조회
    assert response.status_code == 404  # 확인


def test_invalid_action_returns_422():
    response = client.post("/leads/any-id/approve", json={"action": "yes"})
    assert response.status_code == 422


def test_health_needs_no_api_key(monkeypatch):
    monkeypatch.setenv("API_ACCESS_KEY", "secret")
    assert client.get("/health").status_code == 200


def test_missing_api_key_returns_401(monkeypatch):
    monkeypatch.setenv("API_ACCESS_KEY", "secret")
    assert client.get("/leads/any-id").status_code == 401


def test_correct_api_key_is_accepted(monkeypatch):
    monkeypatch.setenv("API_ACCESS_KEY", "secret")
    response = client.get("/leads/does-not-exist", headers={"X-API-Key": "secret"})
    assert response.status_code == 404  # passed the key check, then no such lead
