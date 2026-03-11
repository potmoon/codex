import json

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


DAILY = [
    {"timestamp": "1", "open": 10.0, "high": 10.3, "low": 9.8, "close": 10.1},
    {"timestamp": "2", "open": 10.1, "high": 10.5, "low": 10.0, "close": 10.45},
]
H4 = [
    {"timestamp": "1", "open": 10.2, "high": 10.4, "low": 10.1, "close": 10.3},
    {"timestamp": "2", "open": 10.3, "high": 10.45, "low": 10.2, "close": 10.44},
]
H1 = [
    {"timestamp": "1", "open": 10.38, "high": 10.42, "low": 10.3, "close": 10.4},
    {"timestamp": "2", "open": 10.4, "high": 10.5, "low": 10.35, "close": 10.47},
]


def _multipart_payload() -> dict:
    return {
        "ticker": "WIMI",
        "daily": json.dumps(DAILY),
        "h4": json.dumps(H4),
        "h1": json.dumps(H1),
    }


def _png_file(name: str = "chart.png", content: bytes = b"pngbytes", mime_type: str = "image/png") -> tuple:
    return ("images", (name, content, mime_type))


def test_mock_mode_with_images_works_and_ignores_images(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.api.routes import analyze as analyze_route

    monkeypatch.setattr(analyze_route, "get_settings", lambda: type("S", (), {"interpreter_mode": "mock"})())

    response = client.post(
        "/analyze/interpret-with-images",
        data=_multipart_payload(),
        files=[_png_file()],
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "WIMI"
    assert data["interpreter_context"]["mode"] == "mock"
    assert data["interpreter_context"]["used_images"] is False
    assert data["interpreter_context"]["image_count"] == 1


def test_validation_errors_for_images() -> None:
    response = client.post(
        "/analyze/interpret-with-images",
        data=_multipart_payload(),
        files=[("images", ("bad.gif", b"gif", "image/gif"))],
    )
    assert response.status_code == 415

    response_empty = client.post(
        "/analyze/interpret-with-images",
        data=_multipart_payload(),
        files=[_png_file(content=b"")],
    )
    assert response_empty.status_code == 422


def test_openai_image_path_with_fake_client(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.api.routes import analyze as analyze_route
    from backend.app.services import interpreter as interpreter_service

    monkeypatch.setattr(analyze_route, "get_settings", lambda: type("S", (), {"interpreter_mode": "openai"})())

    class FakeClient:
        def __init__(self, api_key: str, model: str = "gpt-5.4") -> None:
            pass

        def interpret_with_images(self, payload: dict, images: list[dict]) -> dict:
            return {
                "ticker": payload["ticker"],
                "action": "wait",
                "setup_type": "image_confirmed_wait",
                "entry_stage": "early",
                "confidence": 0.67,
                "summary": f"Used {len(images)} image(s) with deterministic facts",
                "mtf_view": payload["mtf_view"],
                "invalidation": {"type": "price_level", "value": 10.0},
            }

    monkeypatch.setattr(interpreter_service, "OpenAIInterpreterClient", FakeClient)

    response = client.post(
        "/analyze/interpret-with-images",
        data=_multipart_payload(),
        files=[_png_file(), _png_file("chart2.jpg", b"jpeg", mime_type="image/jpeg")],
    )
    assert response.status_code == 200
    data = response.json()
    assert data["interpreter_context"]["mode"] == "openai"
    assert data["interpreter_context"]["used_images"] is True
    assert data["interpreter_context"]["image_count"] == 2
    assert data["interpretation"]["setup_type"] == "image_confirmed_wait"


def test_openai_failure_falls_back_to_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.api.routes import analyze as analyze_route
    from backend.app.services import interpreter as interpreter_service

    monkeypatch.setattr(analyze_route, "get_settings", lambda: type("S", (), {"interpreter_mode": "openai"})())

    class FailingClient:
        def __init__(self, api_key: str, model: str = "gpt-5.4") -> None:
            pass

        def interpret_with_images(self, payload: dict, images: list[dict]) -> dict:
            raise RuntimeError("simulated openai failure")

    monkeypatch.setattr(interpreter_service, "OpenAIInterpreterClient", FailingClient)

    response = client.post(
        "/analyze/interpret-with-images",
        data=_multipart_payload(),
        files=[_png_file()],
    )
    assert response.status_code == 200
    data = response.json()
    assert data["interpreter_context"]["mode"] == "fallback_mock"
    assert data["interpreter_context"]["used_images"] is False
    assert data["interpretation"]["action"] in {"buy", "wait"}


def test_response_shape_is_stable() -> None:
    response = client.post(
        "/analyze/interpret-with-images",
        data=_multipart_payload(),
        files=[_png_file()],
    )
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"ticker", "facts", "llm_payload", "interpretation", "interpreter_context"}
