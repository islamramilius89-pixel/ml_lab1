import pytest
from main import PenguinRequest
from pydantic import ValidationError


def test_valid_request():
    data = {
        "culmen_length_mm": 40.0,
        "culmen_depth_mm": 18.0,
        "flipper_length_mm": 200.0,
        "body_mass_g": 4000.0
    }
    req = PenguinRequest(**data)
    assert req.culmen_length_mm == 40.0

def test_invalid_request_missing_field():
    data = {
        "culmen_length_mm": 40.0,
        "culmen_depth_mm": 18.0,
        "flipper_length_mm": 200.0,
    }
    with pytest.raises(ValidationError):
        PenguinRequest(**data)


def test_invalid_request_wrong_type():
    data = {
        "culmen_length_mm": "not_a_number",
        "culmen_depth_mm": 18.0,
        "flipper_length_mm": 200.0,
        "body_mass_g": 4000.0
    }
    try:
        PenguinRequest(**data)
        assert False, "Ожидалась ошибка валидации"
    except ValidationError:
        pass