# Запуск лабораторной работы в Jenkins на Windows

## 1. Требования

Jenkins должен работать на Windows-агенте, где установлены:

- Docker Desktop;
- Docker Compose v2;
- Git;
- Python 3.11 с командой `py`;
- Jenkins Pipeline plugin;
- Git plugin;
- Credentials Binding plugin.

Проверь в PowerShell от имени пользователя Jenkins или в Jenkins Pipeline:

```powershell
docker version
docker compose version
py --version
git --version
```

В выводе `docker version` должны присутствовать разделы `Client` и `Server`.

## 2. Доступ Jenkins к Docker

Если Jenkins установлен как Windows-служба, добавь учётную запись службы в группу `docker-users`.

PowerShell от имени администратора:

```powershell
net localgroup docker-users jenkins /add
Restart-Service jenkins
```

Если служба Jenkins работает под другой учётной записью, добавь в группу `docker-users` именно её. После изменения группы перезапусти Jenkins и Docker Desktop.

## 3. Credentials в Jenkins

Открой `Manage Jenkins → Credentials → System → Global credentials` и создай записи с такими ID:

| ID | Тип | Значение |
|---|---|---|
| `lab-db-user` | Secret text | пользователь PostgreSQL |
| `lab-db-password` | Secret text | пароль PostgreSQL |
| `lab-db-name` | Secret text | имя базы данных |
| `dockerhub-credentials` | Username with password | логин DockerHub и Access Token |

Не записывай реальные пароли в `Jenkinsfile`, GitHub или отчёт.

## 4. Настрой DockerHub

В файле `Jenkinsfile` замени:

```groovy
DOCKER_IMAGE = 'YOUR_DOCKER_USERNAME/penguin-api'
```

на имя своего DockerHub-репозитория:

```groovy
DOCKER_IMAGE = 'myusername/penguin-api'
```

Для публикации лучше использовать DockerHub Access Token вместо пароля аккаунта.

## 5. Создание Pipeline

1. В Jenkins нажми `New Item`.
2. Укажи имя задания, например `ml-lab2-windows`.
3. Выбери тип `Pipeline`.
4. В разделе `Pipeline` выбери `Pipeline script from SCM`.
5. SCM: `Git`.
6. Укажи URL GitHub-репозитория.
7. В поле Branch указать:

```text
*/lab2
```

8. В поле Script Path укажи:

```text
Jenkinsfile
```

9. Сохрани задание и нажми `Build Now`.

Если Jenkins использует конкретный Windows-агент, укажи его label в настройках задания или замени в `Jenkinsfile` строку `agent any` на нужный label.

## 6. Что выполняет Pipeline

Pipeline автоматически:

1. получает код из GitHub;
2. проверяет Docker, Compose и Python;
3. создаёт виртуальное окружение `.venv`;
4. устанавливает зависимости из `requirements.txt`;
5. запускает unit-тесты;
6. запускает PostgreSQL и API через Docker Compose;
7. ждёт успешного ответа `/health`;
8. запускает функциональные тесты;
9. для ветки `main` собирает Docker-образ;
10. для ветки `main` отправляет образ в DockerHub;
11. после выполнения удаляет контейнеры и виртуальное окружение.

## 7. Порты

В текущем `Jenkinsfile` настроено:

```text
APP_HOST_PORT=8001
APP_PORT=8000
BASE_URL=http://localhost:8001
```

Это означает:

- внутри контейнера API слушает порт `8000`;
- на Windows-хосте Jenkins API доступно на порту `8001`.

Если порт `8001` занят, измени одновременно:

```groovy
APP_HOST_PORT = '8010'
BASE_URL = 'http://localhost:8010'
```

Внутренний `APP_PORT` менять не нужно.

## 8. Ожидаемый результат

В консоли Jenkins должны успешно завершиться этапы:

```text
Check tools       SUCCESS
Unit tests        SUCCESS
Start application SUCCESS
Wait for API      SUCCESS
Functional tests  SUCCESS
```

Для ветки `lab2` этапы публикации DockerHub будут пропущены. Для публикации выполни Pipeline на ветке `main`.

## 9. Проверка вручную на Windows

Из каталога проекта можно проверить те же команды вручную:

```powershell
$env:DB_USER = 'локальный_пользователь'
$env:DB_PASSWORD = 'локальный_пароль'
$env:DB_NAME = 'predictions_db'
$env:DB_PORT = '5432'
$env:DB_CONTAINER_HOST = 'postgres'
$env:APP_HOST_PORT = '8001'
$env:APP_PORT = '8000'

docker compose down -v --remove-orphans
docker compose up --build -d
docker compose ps
Invoke-RestMethod http://localhost:8001/health
```

После проверки останови сервисы:

```powershell
docker compose down -v --remove-orphans
```

## 10. Типичные ошибки

### Docker Engine не запущен

Запусти Docker Desktop и проверь:

```powershell
docker info
```

### Порт уже занят

Проверь порт:

```powershell
Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
```

Если порт занят, измени `APP_HOST_PORT` и `BASE_URL` в `Jenkinsfile`.

### API не запускается

Посмотри логи:

```powershell
docker compose ps -a
docker compose logs app --tail 100
```

### PostgreSQL не готов

Проверь:

```powershell
docker compose logs postgres --tail 100
```

Убедись, что credentials `lab-db-user`, `lab-db-password` и `lab-db-name` существуют в Jenkins.

### Не найден `model.pkl`

Файл `model.pkl` должен находиться в корне проекта и быть доступен в Git. Dockerfile проверяет его наличие во время сборки.
