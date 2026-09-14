# wait_for_db.py - ждёт, пока база данных будет готова

import psycopg2
import time
import os
import sys

def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Не задана переменная окружения {name}")
    return value


def wait_for_db():
    db_host = _required_env("DB_HOST")
    db_port = _required_env("DB_PORT")
    db_user = _required_env("DB_USER")
    db_password = _required_env("DB_PASSWORD")
    db_name = _required_env("DB_NAME")

    print(f"Ожидание подключения к PostgreSQL {db_host}:{db_port}...")
    for _ in range(30):
        try:
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                dbname=db_name,
            )
            conn.close()
            print("✅ PostgreSQL готов!")
            return True
        except psycopg2.OperationalError:
            print("⏳ PostgreSQL ещё не готов, ждём 1 секунду...")
            time.sleep(1)
    print("❌ PostgreSQL не запустился за 30 секунд")
    return False

if __name__ == "__main__":
    if wait_for_db():
        sys.exit(0)
    else:
        sys.exit(1)