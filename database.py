# database.py - работа с базой данных PostgreSQL

import psycopg2
import os
from datetime import datetime

# Параметры подключения передаются только через окружение.
def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Не задана переменная окружения {name}")
    return value


def get_connection():
    """Создаёт и возвращает подключение к базе данных."""
    return psycopg2.connect(
        host=_required_env("DB_HOST"),
        port=_required_env("DB_PORT"),
        user=_required_env("DB_USER"),
        password=_required_env("DB_PASSWORD"),
        dbname=_required_env("DB_NAME"),
    )


def check_connection() -> bool:
    """Проверяет доступность базы данных."""
    try:
        with get_connection():
            return True
    except (OSError, psycopg2.Error, RuntimeError):
        return False

def create_table():
    """Создаёт таблицу для хранения предсказаний (если её нет)"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            culmen_length_mm FLOAT,
            culmen_depth_mm FLOAT,
            flipper_length_mm FLOAT,
            body_mass_g FLOAT,
            predicted_species VARCHAR(50),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Таблица predictions готова")

def save_prediction(data, prediction):
    """Сохраняет предсказание в базу данных"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO predictions 
        (culmen_length_mm, culmen_depth_mm, flipper_length_mm, body_mass_g, predicted_species, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data.get('culmen_length_mm'),
        data.get('culmen_depth_mm'),
        data.get('flipper_length_mm'),
        data.get('body_mass_g'),
        prediction,
        datetime.now()
    ))
    
    conn.commit()
    cur.close()
    conn.close()

def get_prediction_history(limit=10):
    """Получает последние предсказания из базы"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT culmen_length_mm, culmen_depth_mm, flipper_length_mm, body_mass_g, 
               predicted_species, timestamp
        FROM predictions
        ORDER BY timestamp DESC
        LIMIT %s
    """, (limit,))
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            'culmen_length_mm': row[0],
            'culmen_depth_mm': row[1],
            'flipper_length_mm': row[2],
            'body_mass_g': row[3],
            'predicted_species': row[4],
            'timestamp': str(row[5])
        })
    
    return history