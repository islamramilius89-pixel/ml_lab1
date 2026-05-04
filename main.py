from fastapi import FastAPI
import joblib
import pandas as pd

app = FastAPI()

# Загружаем обученную модель
model = joblib.load("model.pkl")

@app.get("/")
def root():
    return {"message": "Пингвиний API работает! Перейдите на /docs"}

@app.post("/predict")
def predict(culmen_length_mm: float, culmen_depth_mm: float, flipper_length_mm: float, body_mass_g: float):
    # Создаём таблицу из одного пингвина
    data = pd.DataFrame([[
        culmen_length_mm,
        culmen_depth_mm,
        flipper_length_mm,
        body_mass_g
    ]], columns=["culmen_length_mm", "culmen_depth_mm", "flipper_length_mm", "body_mass_g"])
    
    # Предсказываем вид
    prediction = model.predict(data)[0]
    
    return {"predicted_species": prediction}