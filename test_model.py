import os
import joblib
import pandas as pd
import pytest


FEATURES = ["culmen_length_mm", "culmen_depth_mm", "flipper_length_mm", "body_mass_g"]


@pytest.fixture(scope="module")
def model():
    assert os.path.exists("model.pkl"), "model.pkl не найден, запустите train.py"
    return joblib.load("model.pkl")


def test_model_is_loaded(model):
    assert model is not None


def test_model_predict_single(model):
    X = pd.DataFrame([[39.1, 18.7, 181.0, 3750.0]], columns=FEATURES)
    pred = model.predict(X)[0]
    assert pred in ["Adelie", "Chinstrap", "Gentoo"]


def test_model_accuracy_on_dataset(model):
    df = pd.read_csv("data/penguins_size.csv").dropna()
    X = df[FEATURES]
    y = df["species"]
    acc = (model.predict(X) == y).mean()
    assert acc > 0.9, f"Accuracy слишком низкая: {acc}"


def test_api_module_importable():
    from main import app
    assert app is not None