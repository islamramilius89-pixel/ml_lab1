pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    environment {
        PROJECT_DIR = '.'
        DB_HOST = 'localhost'
        DB_CONTAINER_HOST = 'postgres'
        DB_PORT = '5432'
        APP_PORT = '8000'
        APP_HOST_PORT = '8001'
        RUN_LIVE_TESTS = '1'
        BASE_URL = 'http://localhost:8001'
        PYTHON_EXE = 'C:/Users/111/AppData/Local/Programs/Python/Python313/python.exe'
        DOCKER_IMAGE = 'YOUR_DOCKER_USERNAME/penguin-api'
        VAULT_TOKEN = 'root-token'
        VAULT_SECRET_PATH = 'ml-lab4/db'
        KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
        KAFKA_TOPIC = 'predictions'
        KAFKA_GROUP_ID = 'prediction-consumer'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check tools') {
            steps {
                bat 'docker version'
                bat 'docker compose version'
                bat '"%PYTHON_EXE%" --version'
            }
        }

        stage('Install dependencies') {
            steps {
                bat '''
                    if exist .venv rmdir /s /q .venv
                    "%PYTHON_EXE%" -m venv .venv
                    call .venv\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Unit tests') {
            steps {
                bat '''
                    call .venv\\Scripts\\activate.bat
                    set "PYTHONPATH=%PROJECT_DIR%"
                    python -m pytest %PROJECT_DIR%\\tests\\unit\\
                '''
            }
        }

        stage('Start application') {
            steps {
                withCredentials([
                    string(credentialsId: 'lab-db-user', variable: 'DB_USER'),
                    string(credentialsId: 'lab-db-password', variable: 'DB_PASSWORD'),
                    string(credentialsId: 'lab-db-name', variable: 'DB_NAME')
                ]) {
                    bat '''
                        setlocal
                        if "%DB_USER%"=="" set "DB_USER=jenkins"
                        if "%DB_PASSWORD%"=="" set "DB_PASSWORD=jenkins_pass"
                        if "%DB_NAME%"=="" set "DB_NAME=predictions_db"

                        > %PROJECT_DIR%\\.jenkins.env (
                            echo POSTGRES_USER=%DB_USER%
                            echo POSTGRES_PASSWORD=%DB_PASSWORD%
                            echo POSTGRES_DB=%DB_NAME%
                            echo DB_PORT=%DB_PORT%
                            echo DB_CONTAINER_HOST=%DB_CONTAINER_HOST%
                            echo APP_PORT=%APP_PORT%
                            echo APP_HOST_PORT=%APP_HOST_PORT%
                            echo VAULT_ADDR=http://vault:8200
                            echo VAULT_TOKEN=%VAULT_TOKEN%
                            echo VAULT_SECRET_PATH=%VAULT_SECRET_PATH%
                            echo VAULT_KV_MOUNT=secret
                            echo KAFKA_BOOTSTRAP_SERVERS=%KAFKA_BOOTSTRAP_SERVERS%
                            echo KAFKA_TOPIC=%KAFKA_TOPIC%
                            echo KAFKA_GROUP_ID=%KAFKA_GROUP_ID%
                        )

                        docker compose -f %PROJECT_DIR%\\docker-compose.yml --env-file %PROJECT_DIR%\\.jenkins.env down -v --remove-orphans
                        docker compose -f %PROJECT_DIR%\\docker-compose.yml --env-file %PROJECT_DIR%\\.jenkins.env up --build -d
                        docker compose -f %PROJECT_DIR%\\docker-compose.yml --env-file %PROJECT_DIR%\\.jenkins.env ps
                    '''
                }
            }
        }

        stage('Wait for API') {
            steps {
                powershell '''
                    $maxAttempts = 30
                    $healthUrl = "$env:BASE_URL/health"

                    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
                        try {
                            $response = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 5
                            if ($response.status -eq "healthy") {
                                Write-Host "API is healthy"
                                exit 0
                            }
                        }
                        catch {
                            Write-Host "API is not ready. Attempt: $attempt/$maxAttempts"
                        }

                        Start-Sleep -Seconds 2
                    }

                    docker compose -f "$env:PROJECT_DIR/docker-compose.yml" --env-file "$env:PROJECT_DIR/.jenkins.env" ps
                    docker compose -f "$env:PROJECT_DIR/docker-compose.yml" --env-file "$env:PROJECT_DIR/.jenkins.env" logs app --tail 100
                    docker compose -f "$env:PROJECT_DIR/docker-compose.yml" --env-file "$env:PROJECT_DIR/.jenkins.env" logs vault --tail 100
                    throw "API did not become healthy"
                '''
            }
        }

        stage('Functional tests') {
            steps {
                bat '''
                    call .venv\\Scripts\\activate.bat
                    set "PYTHONPATH=%PROJECT_DIR%"
                    pytest %PROJECT_DIR%\\tests\\functional\\
                '''
            }
        }

        stage('Build Docker image') {
            when {
                branch 'main'
            }
            steps {
                bat '''
                    docker build -t "%DOCKER_IMAGE%:%BUILD_NUMBER%" -t "%DOCKER_IMAGE%:latest" %PROJECT_DIR%
                '''
            }
        }

        stage('Push Docker image') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    powershell '''
                        $env:DOCKER_PASSWORD | docker login --username $env:DOCKER_USERNAME --password-stdin
                        docker push "$env:DOCKER_IMAGE`:$env:BUILD_NUMBER"
                        docker push "$env:DOCKER_IMAGE`:latest"
                    '''
                }
            }
        }
    }

    post {
        always {
            bat 'if exist %PROJECT_DIR%\\.jenkins.env docker compose -f %PROJECT_DIR%\\docker-compose.yml --env-file %PROJECT_DIR%\\.jenkins.env logs --no-color'
            bat 'if exist %PROJECT_DIR%\\.jenkins.env docker compose -f %PROJECT_DIR%\\docker-compose.yml --env-file %PROJECT_DIR%\\.jenkins.env down -v --remove-orphans'
            bat 'if exist .venv rmdir /s /q .venv >nul 2>&1 || exit /b 0'
            bat 'if exist %PROJECT_DIR%\\.jenkins.env del /f /q %PROJECT_DIR%\\.jenkins.env'
        }
    }
}
