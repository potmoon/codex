import os
import tempfile

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient


def _build_single_payload() -> dict:
    return {
        "ticker": "WIMI",
        "facts": {
            "ticker": "WIMI",
            "mtf_view": {"daily": "available", "h4": "available", "h1": "available"},
            "levels": {"daily": {}, "h4": {}, "h1": {}},
            "signals": {
                "daily_allows_long": True,
                "h4_setup_active": True,
                "h1_late_after_ignition": False,
            },
            "reason_flags": {
                "daily_allows_long": True,
                "h4_setup_active": True,
                "h1_late_after_ignition": False,
                "prior_entry_likely_happened": False,
                "local_climax_present": False,
                "major_bc_risk": False,
                "extended_from_break": False,
            },
            "decision_context": {"action": "buy", "entry_stage": "best", "conflict_level": "low"},
        },
        "llm_payload": {
            "ticker": "WIMI",
            "mtf_view": {"daily": "available", "h4": "available", "h1": "available"},
            "levels": {"daily": {}, "h4": {}, "h1": {}},
            "signals": {
                "daily_allows_long": True,
                "h4_setup_active": True,
                "h1_late_after_ignition": False,
            },
            "reason_flags": {
                "daily_allows_long": True,
                "h4_setup_active": True,
                "h1_late_after_ignition": False,
                "prior_entry_likely_happened": False,
                "local_climax_present": False,
                "major_bc_risk": False,
                "extended_from_break": False,
            },
            "decision_context": {"action": "buy", "entry_stage": "best", "conflict_level": "low"},
        },
        "interpretation": {
            "ticker": "WIMI",
            "action": "buy",
            "setup_type": "confirmed_bullish_setup",
            "entry_stage": "best",
            "confidence": 0.82,
            "summary": "Good setup",
            "mtf_view": {"daily": "available", "h4": "available", "h1": "available"},
            "invalidation": {"type": "price_level", "value": 10.0},
        },
    }


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    temp_db.close()
    monkeypatch.setenv("SESSION_DB_PATH", temp_db.name)

    from importlib import reload

    import backend.app.db.base as db_base
    reload(db_base)
    import backend.app.db.session_store as ss
    reload(ss)
    import backend.app.api.routes.sessions as sessions_route
    reload(sessions_route)
    import backend.app.main as main_mod
    reload(main_mod)

    test_client = TestClient(main_mod.app)
    yield test_client
    os.unlink(temp_db.name)


def test_save_single_and_get_and_list(client: TestClient) -> None:
    payload = _build_single_payload()
    save = client.post("/sessions/save-single", json={"label": "run1", "payload": payload})
    assert save.status_code == 200
    session_id = save.json()["id"]

    listed = client.get("/sessions")
    assert listed.status_code == 200
    assert any(item["id"] == session_id for item in listed.json()["items"])

    detail = client.get(f"/sessions/{session_id}")
    assert detail.status_code == 200
    assert detail.json()["session_type"] == "single_ticker_analysis"


def test_save_batch_and_compare_shapes(client: TestClient) -> None:
    single = _build_single_payload()
    left = client.post("/sessions/save-single", json={"payload": single}).json()["id"]

    single2 = _build_single_payload()
    single2["interpretation"]["action"] = "wait"
    single2["interpretation"]["entry_stage"] = "late"
    right = client.post("/sessions/save-single", json={"payload": single2}).json()["id"]

    cmp_resp = client.get(f"/sessions/compare?left_id={left}&right_id={right}")
    assert cmp_resp.status_code == 200
    cmp = cmp_resp.json()
    assert set(cmp.keys()) == {"left_id", "right_id", "ticker", "changes"}
    assert cmp["changes"]["action_changed"] is True
    assert cmp["changes"]["entry_stage_changed"] is True


def test_watchlist_compare_detects_changes(client: TestClient) -> None:
    batch_left = {
        "count": 1,
        "sorted_by": "ranking.score",
        "items": [
            {
                "ticker": "WIMI",
                "status": "ok",
                "facts": {},
                "llm_payload": {},
                "interpretation": {
                    "ticker": "WIMI",
                    "action": "buy",
                    "setup_type": "x",
                    "entry_stage": "best",
                    "confidence": 0.8,
                    "summary": "x",
                    "mtf_view": {"daily": "a", "h4": "a", "h1": "a"},
                    "invalidation": {"type": "price_level", "value": 1.0},
                },
                "ranking": {"score": 80, "priority": "high", "reason": "x"},
            }
        ],
    }
    batch_right = {
        "count": 1,
        "sorted_by": "ranking.score",
        "items": [
            {
                "ticker": "WIMI",
                "status": "ok",
                "facts": {},
                "llm_payload": {},
                "interpretation": {
                    "ticker": "WIMI",
                    "action": "wait",
                    "setup_type": "x",
                    "entry_stage": "late",
                    "confidence": 0.6,
                    "summary": "x",
                    "mtf_view": {"daily": "a", "h4": "a", "h1": "a"},
                    "invalidation": {"type": "price_level", "value": 1.0},
                },
                "ranking": {"score": 50, "priority": "medium", "reason": "x"},
            }
        ],
    }

    l = client.post("/sessions/save-batch", json={"payload": batch_left}).json()["id"]
    r = client.post("/sessions/save-batch", json={"payload": batch_right}).json()["id"]
    cmp = client.get(f"/sessions/compare?left_id={l}&right_id={r}").json()
    assert "changed_rankings" in cmp["changes"]
    assert "WIMI" in cmp["changes"]["changed_rankings"]
