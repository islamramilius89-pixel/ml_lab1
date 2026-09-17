# wait_for_db.py - ждёт, пока база данных будет готова

import sys
import time

import psycopg2

from database import _db_connection_params


def wait_for_db():
    params = _db_connection_params()
    print(f"Ожидание подключения к PostgreSQL {params['host']}:{params['port']}...")

    for _ in range(30):
        try:
            conn = psycopg2.connect(**params)
            conn.close()
            print("PostgreSQL готов")
            return True
        except psycopg2.OperationalError:
            print("PostgreSQL ещё не готов, ждём 1 секунду...")
            time.sleep(1)

    print("PostgreSQL не запустился за 30 секунд")
    return False

if __name__ == "__main__":
    if wait_for_db():
        sys.exit(0)
    else:
        sys.exit(1)