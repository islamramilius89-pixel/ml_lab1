import os

import httpx
import pytest

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
RUN_LIVE_TESTS = os.getenv("RUN_LIVE_TESTS") == "1"


@pytest.mark.skipif(not RUN_LIVE_TESTS, reason="Требуется запущенный сервис")
def test_health_check():
    response = httpx.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.skipif(not RUN_LIVE_TESTS, reason="Требуется запущенный сервис")
def test_predict_valid():
    payload = {
        "culmen_length_mm": 40.0,
        "culmen_depth_mm": 18.0,
        "flipper_length_mm": 200.0,
        "body_mass_g": 4000.0
    }
    response = httpx.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_species" in data
    assert "timestamp" in data

@pytest.mark.skipif(not RUN_LIVE_TESTS, reason="Требуется запущенный сервис")
def test_predict_invalid():
    payload = {
        "culmen_length_mm": -10.0,  # допустимо по типу, но может быть нелогично
        "culmen_depth_mm": 18.0,
        "flipper_length_mm": 200.0,
        "body_mass_g": 4000.0
    }
    response = httpx.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 422
