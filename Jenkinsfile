pipeline {
    agent any
    
    parameters {
        choice(name: 'ACTION', choices: ['train', 'test', 'both'], description: 'Что сделать?')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "Код успешно загружен из репозитория"
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo "Настройка Python окружения..."
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
                echo "Зависимости установлены"
            }
        }
        
        stage('Check Data') {
            steps {
                echo "Проверка наличия данных..."
                sh '''
                    . venv/bin/activate
                    if [ ! -f "data/penguins_size.csv" ]; then
                        echo "ОШИБКА: Файл data/penguins_size.csv не найден!"
                        echo "Скачайте датасет с https://www.kaggle.com/datasets/parulpandey/palmer-archipelago-antarctica-penguin-data"
                        exit 1
                    fi
                    echo "Данные найдены"
                '''
            }
        }
        
        stage('Train Model') {
            when {
                expression { params.ACTION == 'train' || params.ACTION == 'both' }
            }
            steps {
                echo "Запуск обучения модели..."
                sh '''
                    . venv/bin/activate
                    python train.py
                '''
                echo "Модель успешно обучена"
            }
            post {
                success {
                    archiveArtifacts artifacts: 'model.pkl', fingerprint: true
                    echo "Файл model.pkl сохранен как артефакт"
                }
            }
        }
        
        stage('Test API') {
            when {
                expression { params.ACTION == 'test' || params.ACTION == 'both' }
            }
            steps {
                echo "Запуск тестирования API..."
                sh '''
                    . venv/bin/activate
                    # Запускаем API в фоне
                    python -m uvicorn main:app --port 8000 &
                    API_PID=$!
                    
                    # Ждем запуска API
                    sleep 5
                    
                    # Тестируем API
                    curl -X POST "http://localhost:8000/predict" \
                        -H "Content-Type: application/json" \
                        -d '{
                            "culmen_length_mm": 39.1,
                            "culmen_depth_mm": 18.7,
                            "flipper_length_mm": 181.0,
                            "body_mass_g": 3750.0
                        }' || echo "Тест не прошел"
                    
                    # Останавливаем API
                    kill $API_PID
                '''
                echo "Тестирование API завершено"
            }
        }
    }
    
    post {
        always {
            echo "Очистка..."
            sh '''
                # Останавливаем процессы, если они еще работают
                pkill -f "uvicorn main:app" || true
            '''
        }
        success {
            echo "Pipeline выполнен успешно!"
        }
        failure {
            echo "Pipeline завершился с ошибкой!"
        }
    }
}