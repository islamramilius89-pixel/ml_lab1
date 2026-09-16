pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    environment {
        DB_HOST = 'localhost'
        DB_CONTAINER_HOST = 'postgres'
        DB_PORT = '5432'
        APP_PORT = '8000'
        APP_HOST_PORT = '8001'
        RUN_LIVE_TESTS = '1'
        BASE_URL = 'http://localhost:8001'
        PYTHON_EXE = 'C:/Users/111/AppData/Local/Programs/Python/Python313/python.exe'
        DOCKER_IMAGE = 'YOUR_DOCKER_USERNAME/penguin-api'
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
                    python -m pytest tests\\unit\\
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

                        > .jenkins.env (
                            echo DB_USER=%DB_USER%
                            echo DB_PASSWORD=%DB_PASSWORD%
                            echo DB_NAME=%DB_NAME%
                            echo DB_PORT=%DB_PORT%
                            echo DB_CONTAINER_HOST=%DB_CONTAINER_HOST%
                            echo APP_PORT=%APP_PORT%
                            echo APP_HOST_PORT=%APP_HOST_PORT%
                        )

                        docker compose --env-file .jenkins.env down -v --remove-orphans
                        docker compose --env-file .jenkins.env up --build -d
                        docker compose --env-file .jenkins.env ps
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

                    docker compose --env-file .jenkins.env ps
                    docker compose --env-file .jenkins.env logs app --tail 100
                    throw "API did not become healthy"
                '''
            }
        }

        stage('Functional tests') {
            steps {
                bat '''
                    call .venv\\Scripts\\activate.bat
                    pytest tests\\functional\\
                '''
            }
        }

        stage('Build Docker image') {
            when {
                branch 'main'
            }
            steps {
                bat '''
                    docker build -t "%DOCKER_IMAGE%:%BUILD_NUMBER%" -t "%DOCKER_IMAGE%:latest" .
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
            withCredentials([
                string(credentialsId: 'lab-db-user', variable: 'DB_USER'),
                string(credentialsId: 'lab-db-password', variable: 'DB_PASSWORD'),
                string(credentialsId: 'lab-db-name', variable: 'DB_NAME')
            ]) {
                bat 'docker compose logs --no-color'
                bat 'docker compose down -v --remove-orphans'
            }

            bat 'if exist .venv rmdir /s /q .venv >nul 2>&1 || exit /b 0'
        }
    }
}
