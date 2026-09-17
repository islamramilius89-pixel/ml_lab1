# main.py - FastAPI для предсказания вида пингвина с сохранением в БД

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

import database

MODEL_PATH = Path(__file__).with_name("model.pkl")
model = joblib.load(MODEL_PATH)


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
    Предсказывает вид пингвина и сохраняет запрос в базу данных
    """
    # Подготавливаем данные для модели
    data = pd.DataFrame([[
        penguin.culmen_length_mm,
        penguin.culmen_depth_mm,
        penguin.flipper_length_mm,
        penguin.body_mass_g
    ]], columns=["culmen_length_mm", "culmen_depth_mm", "flipper_length_mm", "body_mass_g"])
    
    # Предсказываем
    prediction = model.predict(data)[0]
    
    try:
        request_data = penguin.model_dump()
    except AttributeError:
        request_data = penguin.dict()

    try:
        database.save_prediction(request_data, prediction)
    except (OSError, RuntimeError, database.psycopg2.Error) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from exc

    return PenguinResponse(
        predicted_species=str(prediction),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/history")
def get_history(limit: int = Query(default=10, ge=1, le=100)):
    """
    Возвращает последние предсказания из базы данных
    """
    history = database.get_prediction_history(limit)
    return {"history": history, "count": len(history)}