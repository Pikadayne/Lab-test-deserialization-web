import base64
import os
import pickle
import random
import time
from typing import Any

from flask import Flask, jsonify, request, send_from_directory


app = Flask(__name__, static_folder="static", static_url_path="/static")

TYPING_PROMPTS = [
    "The quick brown fox jumps over the lazy dog.",
    "Practice daily to build speed and accuracy.",
    "A focused typing session can improve consistency.",
    "Measure twice, type once, and keep a steady rhythm.",
]


def calculate_typing_result(prompt: str, typed_text: str, duration_seconds: float) -> dict[str, Any]:
    elapsed = max(float(duration_seconds or 0), 1.0)
    typed_words = typed_text.strip().split()
    expected_chars = len(prompt)
    matching_chars = sum(1 for expected, actual in zip(prompt, typed_text) if expected == actual)

    if expected_chars:
        accuracy = round((matching_chars / expected_chars) * 100, 2)
    else:
        accuracy = 0.0

    return {
        "prompt": prompt,
        "typed_text": typed_text,
        "duration_seconds": round(elapsed, 2),
        "characters": len(typed_text),
        "words": len(typed_words),
        "wpm": round((len(typed_words) / elapsed) * 60, 2),
        "accuracy": accuracy,
        "completed": typed_text.strip() == prompt.strip(),
        "created_at": int(time.time()),
    }


def serialize_typing_state(prompt: str) -> str:
    state = {
        "prompt": prompt,
        "issued_at": int(time.time()),
        "source": "typing-test",
    }
    return base64.b64encode(pickle.dumps(state)).decode("ascii")


def load_typing_state(serialized_state: str) -> Any:
    state_bytes = base64.b64decode(serialized_state, validate=False)
    return pickle.loads(state_bytes)


def get_request_fields() -> dict[str, Any]:
    if request.is_json:
        return request.get_json(silent=True) or {}
    if request.form:
        return request.form.to_dict(flat=True)
    return {}


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/prompt")
def get_prompt():
    prompt = random.choice(TYPING_PROMPTS)
    return jsonify({"prompt": prompt, "typing_state": serialize_typing_state(prompt)})


@app.post("/api/typing")
def submit_typing_test():
    data = get_request_fields()
    typed_text = str(data.get("typed_text") or "")
    duration_seconds = float(data.get("duration_seconds") or 0)

    try:
        typing_state = load_typing_state(str(data.get("typing_state") or ""))
    except Exception as exc:
        return jsonify({"status": "error", "error": f"state decode error: {exc}"}), 400

    if isinstance(typing_state, dict):
        prompt = str(typing_state.get("prompt") or "")
    else:
        prompt = str(typing_state)

    result = calculate_typing_result(prompt, typed_text, duration_seconds)
    result["status"] = "submitted"
    result["state_type"] = type(typing_state).__name__

    return jsonify(result)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "typing"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
