# ML_LaB4 — Лабораторная работа №4 (Интеграция Apache Kafka)

## Цель
Реализовать интеграцию Kafka Producer/Consumer в ML-сервис и сохранить защищённый доступ к PostgreSQL через Hashicorp Vault.

## Что реализовано
- Реализован **Kafka Producer** в `main.py`:
  - endpoint `POST /predict` формирует событие и отправляет его в Kafka topic `predictions`.
- Реализован **Kafka Consumer** в `kafka_consumer.py`:
  - отдельный контейнер читает события из Kafka;
  - сохраняет предсказания в PostgreSQL через `database.py`.
- Сохранена интеграция с хранилищем секретов:
  - `secrets_store.py` получает `DB_USER/DB_PASSWORD/DB_NAME` из Vault (KV v2);
  - путь секрета обновлён на `ml-lab4/db`.
- Обновлён `docker-compose.yml`:
  - сервисы `vault`, `postgres`, `zookeeper`, `kafka`, `app`, `consumer`;
  - все сервисы поднимаются в едином стенде.
- Обновлены CI/CD конфигурации:
  - `.github/workflows/ci-cd.yml`
  - `Jenkinsfile`

## Архитектура потока данных
1. Клиент вызывает `POST /predict`.
2. API вычисляет предсказание моделью.
3. API публикует событие в Kafka.
4. `consumer` получает событие и пишет результат в PostgreSQL.
5. `GET /history` читает историю из БД.

## Структура сервисов (docker-compose)
- `vault` — хранение секретов БД.
- `postgres` — база данных предсказаний.
- `zookeeper` — координатор Kafka.
- `kafka` — брокер сообщений.
- `app` — FastAPI сервис (producer).
- `consumer` — Python consumer (читает из Kafka и пишет в БД).

## Переменные окружения
Пример `.local.env`:

```env
POSTGRES_USER=vault_user
POSTGRES_PASSWORD=vault_password
POSTGRES_DB=predictions_db
DB_CONTAINER_HOST=postgres
DB_PORT=5432
APP_PORT=8000
APP_HOST_PORT=8001
VAULT_ADDR=http://vault:8200
VAULT_TOKEN=<vault_token>
VAULT_SECRET_PATH=ml-lab4/db
VAULT_KV_MOUNT=secret
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC=predictions
KAFKA_GROUP_ID=prediction-consumer
```

## Локальный запуск (Windows PowerShell)
Из корня проекта `ML_LaB4`:

1. Поднять стенд:

```powershell
docker compose --env-file .local.env up --build -d
```

2. Проверить контейнеры:

```powershell
docker compose --env-file .local.env ps
```

3. Проверить health API:

```powershell
irm http://localhost:8001/health
```

4. Проверить предсказание:

```powershell
$body = @{
  culmen_length_mm = 40.0
  culmen_depth_mm = 18.0
  flipper_length_mm = 200.0
  body_mass_g = 4000.0
} | ConvertTo-Json

irm http://localhost:8001/predict -Method Post -ContentType 'application/json' -Body $body
```

5. Проверить историю:

```powershell
irm http://localhost:8001/history
```

6. Запустить unit-тесты:

```powershell
$env:PYTHONPATH='.'
python -m pytest tests/unit -q
```

7. Запустить functional-тесты (на живом стенде):

```powershell
$env:PYTHONPATH='.'
$env:RUN_LIVE_TESTS='1'
$env:BASE_URL='http://localhost:8001'
python -m pytest tests/functional -q
```

8. Остановить стенд:

```powershell
docker compose --env-file .local.env down -v --remove-orphans
```

## CI/CD
### GitHub Actions (`.github/workflows/ci-cd.yml`)
- CI:
  - установка зависимостей;
  - запуск unit-тестов.
- CI (ветка `main`):
  - сборка Docker image;
  - push image в DockerHub.
- CD:
  - запуск `docker compose`;
  - запуск functional-тестов;
  - запуск по `workflow_dispatch`, `schedule`, и `push` в `main`.

### Jenkins (`Jenkinsfile`)
- Подготовка окружения и зависимостей.
- Unit + functional тестирование.
- Подъём/остановка стенда через docker-compose.
- Сборка/публикация Docker image для ветки `main`.

## Что приложить к отчёту по ЛР4
1. Ссылка на GitHub-репозиторий (fork от ЛР3).
2. Ссылка на DockerHub image.
3. Скрипты CI/CD:
   - `.github/workflows/ci-cd.yml`
   - `Jenkinsfile`
4. Результаты functional-тестов (логи/скриншоты).
5. Zip-архив актуального дистрибутива модели.

## Файлы, добавленные/обновлённые в ЛР4
- `main.py` — producer.
- `kafka_consumer.py` — consumer.
- `database.py` — сохранение с `event_timestamp`.
- `docker-compose.yml` — Kafka + consumer сервисы.
- `secrets_store.py`, `vault/entrypoint.sh` — путь секрета `ml-lab4/db`.
- `.github/workflows/ci-cd.yml`, `Jenkinsfile` — обновлённые CI/CD сценарии.
- `requirements.txt` — добавлен `kafka-python`.
