# ML_LaB3 — Лабораторная работа №3 (DevOps для ML)

## Цель
Реализовать хранение секретов подключения к БД во внешнем хранилище секретов и интегрировать это в локальный запуск и CI/CD.

## Что сделано
- Создана копия проекта `ML_LaB3` на основе `ML_LaB2`.
- Выбран вариант хранилища секретов: **Hashicorp Vault**.
- Добавлен сервис Vault в `docker-compose`.
- Реализована инициализация секрета в Vault (KV v2) по пути `ml-lab3/db`.
- Приложение получает `DB_USER`, `DB_PASSWORD`, `DB_NAME` из Vault через `secrets_store.py`.
- `database.py` и `wait_for_db.py` переведены на использование секретов из Vault.
- Обновлены CI/CD сценарии:
  - `.github/workflows/ci-cd.yml`
  - `Jenkinsfile`

## Структура сервисов
`docker-compose.yml` поднимает:
- `vault` — хранилище секретов;
- `postgres` — база данных;
- `app` — FastAPI сервис.

## Переменные окружения
Для локального запуска используется файл `ML_LaB3/.local.env`.

Пример:

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
VAULT_SECRET_PATH=ml-lab3/db
VAULT_KV_MOUNT=secret
```

> Рекомендуется оставить `APP_HOST_PORT=8001`, чтобы избежать конфликта с занятым `8000` на хосте.

## Пошаговый запуск (Windows PowerShell)
Из корня workspace `ml_lab2`:

1. Поднять стенд:

```powershell
docker compose -f ML_LaB3/docker-compose.yml --env-file ML_LaB3/.local.env up --build -d
```

2. Проверить состояние контейнеров:

```powershell
docker compose -f ML_LaB3/docker-compose.yml --env-file ML_LaB3/.local.env ps
```

3. Проверить health API:

```powershell
irm http://localhost:8001/health
```

4. Запустить unit-тесты:

```powershell
$env:PYTHONPATH="ML_LaB3"
python -m pytest ML_LaB3/tests/unit -q
```

5. Запустить functional-тесты:

```powershell
$env:PYTHONPATH="ML_LaB3"
$env:RUN_LIVE_TESTS="1"
$env:BASE_URL="http://localhost:8001"
python -m pytest ML_LaB3/tests/functional -q
```

6. Остановить стенд:

```powershell
docker compose -f ML_LaB3/docker-compose.yml --env-file ML_LaB3/.local.env down -v --remove-orphans
```

## Проверки и результаты
Локально получены результаты:
- Unit tests: `3 passed` (есть предупреждения `InconsistentVersionWarning` по версии `scikit-learn`, тесты не блокируют).
- Functional tests: `3 passed`.

## CI/CD
- **GitHub Actions**: `ML_LaB3/.github/workflows/ci-cd.yml`
  - unit тесты;
  - сборка/публикация образа (для `main`);
  - деплой и functional тесты по расписанию/ручному запуску/пушу в `main`.

- **Jenkins**: `ML_LaB3/Jenkinsfile`
  - unit + functional тесты;
  - запуск через `docker compose`;
  - сборка/пуш образа для ветки `main`.

## Что приложить к отчёту
- Ссылка на GitHub репозиторий.
- Ссылка на DockerHub image.
- Логи/скриншоты успешного прогона unit и functional тестов.
- Краткое описание, что секреты БД берутся из Vault (`VAULT_SECRET_PATH`, `VAULT_KV_MOUNT`).
