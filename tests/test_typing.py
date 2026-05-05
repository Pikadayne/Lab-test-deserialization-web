import base64
import pickle

from app import app


def make_typing_state(prompt):
    return base64.b64encode(
        pickle.dumps({"prompt": prompt, "issued_at": 123, "source": "test"})
    ).decode("ascii")


def test_home_page_serves_typing_app():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert "Typing Speed Test" in response.get_data(as_text=True)


def test_prompt_api_returns_encoded_typing_state():
    client = app.test_client()

    response = client.get("/api/prompt")
    data = response.get_json()
    state = pickle.loads(base64.b64decode(data["typing_state"]))

    assert response.status_code == 200
    assert data["prompt"]
    assert state["prompt"] == data["prompt"]
    assert state["source"] == "typing-test"


def test_typing_api_scores_submitted_state():
    client = app.test_client()
    typing_state = make_typing_state("hello world")

    response = client.post(
        "/api/typing",
        json={
            "typing_state": typing_state,
            "typed_text": "hello world",
            "duration_seconds": 30,
        },
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "submitted"
    assert data["state_type"] == "dict"
    assert data["wpm"] == 4
    assert data["accuracy"] == 100
    assert data["completed"] is True


def test_typing_api_accepts_form_data():
    client = app.test_client()
    typing_state = make_typing_state("hello world")

    response = client.post(
        "/api/typing",
        data={
            "typing_state": typing_state,
            "typed_text": "hello world",
            "duration_seconds": "30",
        },
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "submitted"
    assert data["completed"] is True


def test_typing_api_returns_400_for_invalid_state():
    client = app.test_client()

    response = client.post(
        "/api/typing",
        json={
            "typing_state": "not-a-valid-state",
            "typed_text": "hello world",
            "duration_seconds": 30,
        },
    )
    data = response.get_json()

    assert response.status_code == 400
    assert data["status"] == "error"
    assert "state decode error" in data["error"]
