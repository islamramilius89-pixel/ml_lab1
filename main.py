# main.py - FastAPI для предсказания вида пингвина с сохранением в БД

import json
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query, status
from kafka import KafkaProducer
from pydantic import BaseModel, Field

import database

MODEL_PATH = Path(__file__).with_name("model.pkl")
model = joblib.load(MODEL_PATH)


def _kafka_topic() -> str:
    return os.getenv("KAFKA_TOPIC", "predictions")


@lru_cache(maxsize=1)
def get_kafka_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        retries=5,
    )


def publish_prediction_event(request_data: dict[str, float], prediction: str, timestamp: str) -> None:
    event = {
        "request_data": request_data,
        "prediction": prediction,
        "timestamp": timestamp,
    }
    future = get_kafka_producer().send(_kafka_topic(), event)
    future.get(timeout=10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.create_table()
    yield


app = FastAPI(
    title="Penguin Classifier API",
    description="Определяет вид пингвина по параметрам",
    lifespan=lifespan,
)


class PenguinRequest(BaseModel):
    culmen_length_mm: float = Field(gt=0)
    culmen_depth_mm: float = Field(gt=0)
    flipper_length_mm: float = Field(gt=0)
    body_mass_g: float = Field(gt=0)

# Модель данных для ответа
class PenguinResponse(BaseModel):
    predicted_species: str
    timestamp: str

@app.get("/")
def root():
    return {"message": "Penguin Classifier API is running! Go to /docs"}

@app.get("/health")
def health():
    """Проверяет доступность API и PostgreSQL."""
    if not database.check_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        )
    return {"status": "healthy", "database": "connected"}


@app.post("/predict", response_model=PenguinResponse)
def predict(penguin: PenguinRequest):
    """
    Предсказывает вид пингвина и отправляет результат в Kafka.
    """
    data = pd.DataFrame([[
        penguin.culmen_length_mm,
        penguin.culmen_depth_mm,
        penguin.flipper_length_mm,
        penguin.body_mass_g,
    ]], columns=["culmen_length_mm", "culmen_depth_mm", "flipper_length_mm", "body_mass_g"])

    prediction = str(model.predict(data)[0])

    try:
        request_data = penguin.model_dump()
    except AttributeError:
        request_data = penguin.dict()

    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        publish_prediction_event(request_data, prediction, timestamp)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Kafka is unavailable",
        ) from exc

    return PenguinResponse(
        predicted_species=prediction,
        timestamp=timestamp,
    )


@app.get("/history")
def get_history(limit: int = Query(default=10, ge=1, le=100)):
    """
    Возвращает последние предсказания из базы данных
    """
    history = database.get_prediction_history(limit)
    return {"history": history, "count": len(history)}