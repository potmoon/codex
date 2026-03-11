import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient


from backend.app.main import app


client = TestClient(app)


def _post_interpret(payload: dict) -> dict:
    response = client.post('/analyze/interpret', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {'ticker', 'facts', 'llm_payload', 'interpretation'}
    return data


def test_interpret_best_buy_case() -> None:
    data = _post_interpret(
        {
            'ticker': 'BEST',
            'candles': {
                'daily': [
                    {'timestamp': '1', 'open': 10.0, 'high': 10.3, 'low': 9.8, 'close': 10.1},
                    {'timestamp': '2', 'open': 10.1, 'high': 10.5, 'low': 10.0, 'close': 10.45},
                ],
                'h4': [
                    {'timestamp': '1', 'open': 10.2, 'high': 10.4, 'low': 10.1, 'close': 10.3},
                    {'timestamp': '2', 'open': 10.3, 'high': 10.45, 'low': 10.2, 'close': 10.44},
                ],
                'h1': [
                    {'timestamp': '1', 'open': 10.38, 'high': 10.42, 'low': 10.3, 'close': 10.4},
                    {'timestamp': '2', 'open': 10.4, 'high': 10.5, 'low': 10.35, 'close': 10.47},
                ],
            },
        }
    )

    interpretation = data['interpretation']
    assert interpretation['action'] == 'buy'
    assert interpretation['entry_stage'] == 'best'
    assert interpretation['setup_type'] == 'confirmed_bullish_setup'
    assert isinstance(interpretation['confidence'], float)
    assert interpretation['summary']


def test_interpret_late_chase_case() -> None:
    data = _post_interpret(
        {
            'ticker': 'LATE',
            'candles': {
                'daily': [
                    {'timestamp': '1', 'open': 20.0, 'high': 21.0, 'low': 19.8, 'close': 20.5},
                    {'timestamp': '2', 'open': 20.5, 'high': 21.2, 'low': 20.3, 'close': 21.0},
                ],
                'h4': [
                    {'timestamp': '1', 'open': 20.8, 'high': 21.0, 'low': 20.7, 'close': 20.9},
                    {'timestamp': '2', 'open': 20.9, 'high': 21.1, 'low': 20.8, 'close': 21.0},
                ],
                'h1': [
                    {'timestamp': '1', 'open': 21.0, 'high': 21.05, 'low': 20.95, 'close': 21.0},
                    {'timestamp': '2', 'open': 21.0, 'high': 21.8, 'low': 20.98, 'close': 21.7},
                ],
            },
        }
    )

    interpretation = data['interpretation']
    assert interpretation['action'] == 'wait'
    assert interpretation['entry_stage'] == 'late'
    assert interpretation['setup_type'] == 'bullish_but_extended'
    assert isinstance(interpretation['confidence'], float)
    assert interpretation['summary']


def test_interpret_major_bc_risk_case() -> None:
    data = _post_interpret(
        {
            'ticker': 'RISK',
            'candles': {
                'daily': [
                    {'timestamp': '1', 'open': 5.0, 'high': 5.2, 'low': 4.9, 'close': 5.1},
                    {'timestamp': '2', 'open': 5.1, 'high': 5.3, 'low': 5.0, 'close': 5.2},
                ],
                'h4': [
                    {'timestamp': '1', 'open': 5.1, 'high': 5.2, 'low': 5.0, 'close': 5.1},
                    {'timestamp': '2', 'open': 5.1, 'high': 5.25, 'low': 5.05, 'close': 5.6},
                ],
                'h1': [
                    {'timestamp': '1', 'open': 5.55, 'high': 5.6, 'low': 5.5, 'close': 5.58},
                    {'timestamp': '2', 'open': 5.58, 'high': 5.65, 'low': 5.55, 'close': 5.6},
                ],
            },
        }
    )

    interpretation = data['interpretation']
    assert interpretation['action'] == 'wait'
    assert interpretation['entry_stage'] == 'setup'
    assert interpretation['setup_type'] == 'major_bc_risk'
    assert isinstance(interpretation['confidence'], float)
    assert interpretation['summary']
