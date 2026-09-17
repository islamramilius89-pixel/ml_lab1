# Лабораторная работа 2: ML API + PostgreSQL + CI/CD

## Описание
Проект предоставляет API на `FastAPI` для предсказания вида пингвина по 4 признакам.

В рамках лабы реализовано:
- REST API с endpoint для предсказания;
- сохранение результатов предсказаний в `PostgreSQL`;
- контейнеризация через `Docker` и `docker compose`;
- CI/CD для автопроверки (unit + functional);
- Jenkins Pipeline для Windows-агента (`Jenkinsfile`).

Модель (`model.pkl`) обязательна для запуска контейнера.

## Стек
- Python 3.11+ (локально допустим Python 3.13)
- FastAPI
- Uvicorn
- PostgreSQL 15
- Docker / Docker Compose
- Pytest
- Jenkins

## Структура (ключевые файлы)
- `main.py` — API и валидация входа
- `database.py` — подключение к PostgreSQL, запись истории
- `docker-compose.yml` — сервисы `app` и `postgres`
- `Dockerfile` — сборка API-образа
- `entrypoint.sh` — старт приложения в контейнере
- `wait_for_db.py` — ожидание доступности БД
- `tests/unit/test_main.py` — unit-тесты
- `tests/functional/test_api.py` — функциональные тесты
- `.github/workflows/ci-cd.yml` — GitHub Actions
- `Jenkinsfile` — Jenkins Pipeline (Windows)

## Переменные окружения
Используются следующие переменные:

- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `DB_CONTAINER_HOST`
- `APP_PORT`
- `APP_HOST_PORT`

Пример для локального запуска:

```env
DB_HOST=localhost
DB_CONTAINER_HOST=postgres
DB_PORT=5432
DB_USER=myuser
DB_PASSWORD=your_strong_password
DB_NAME=predictions_db
APP_PORT=800
APP_HOST_PORT=8001
```

## Локальный запуск через Docker
Из корня проекта:

```powershell
docker compose down -v --remove-orphans
docker compose build --no-cache app
docker compose up -d
```

Проверка:

```powershell
docker compose ps
Invoke-RestMethod http://localhost:8001/health
```

Документация API:

```text
http://localhost:8001/docs
```

## Основные endpoint
- `GET /health` — статус API и БД
- `POST /predict` — предсказание вида пингвина
- `GET /history` — история предсказаний из PostgreSQL

Пример запроса к `/predict`:

```json
{
  "culmen_length_mm": 40.0,
  "culmen_depth_mm": 18.0,
  "flipper_length_mm": 200.0,
  "body_mass_g": 400.0
}
```

## Тесты
Unit:

```powershell
pytest tests/unit/
```

Functional (требуется запущенное API):

```powershell
$env:RUN_LIVE_TESTS = "1"
$env:BASE_URL = "http://localhost:8001"
pytest tests/functional/
```

## Jenkins (Windows)
В репозитории есть готовый `Jenkinsfile` для ветки `lab2`.

### Что нужно в Jenkins
Credentials (тип **Secret text**):
- `lab-db-user`
- `lab-db-password`
- `lab-db-name`

DockerHub credentials:
- `dockerhub-credentials` (тип **Username with password**)

### Важно
Если в консоли Jenkins есть предупреждения:

```text
DB_USER variable is not set
DB_PASSWORD variable is not set
DB_NAME variable is not set
```

значит credentials в Jenkins пустые или заданы с неверным типом.

## GitHub Actions
Workflow находится в:

```text
.github/workflows/ci-cd.yml
```

Пайплайн выполняет:
- запуск тестов;
- сборку Docker;
- запуск compose-окружения;
- функциональные проверки;
- публикацию Docker-образа (для целевой ветки по правилам workflow).

## Частые проблемы
1. **`postgres_db is unhealthy`**
   - проверь, что `DB_PASSWORD` непустой;
   - проверь, что переменные окружения действительно подхватываются.

2. **Ошибка `entrypoint.sh` в Docker**
   - в Dockerfile уже добавлена нормализация `CRLF -> LF`.

3. **Порт занят**
   - измени `APP_HOST_PORT` (например, `8001` или `8010`).

## Результат выполнения лабы 2
Минимальный критерий готовности:
- `docker compose up -d` запускает `app` и `postgres`;
- `GET /health` возвращает `healthy` и `database: connected`;
- `POST /predict` работает;
- `GET /history` показывает сохраненные записи;
- unit-тесты проходят;
- pipeline в Jenkins/GitHub выполняется без ошибок.