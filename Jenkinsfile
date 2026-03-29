pipeline {
    agent any

    environment {
        IMAGE_NAME = "todo-django-ci"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/prabeshbuilds/todo.git'
            }
        }

       stage('Setup Python Virtualenv') {
    steps {
        sh '''
            python3 -m venv venv
            venv/bin/python -m pip install --upgrade pip
            venv/bin/python -m pip install -r requirements.txt
        '''
    }
}

        stage('Run Lint') {
            steps {
                sh '''
                  . venv/bin/activate
                
                '''
            }
        }

        stage('Run Django Tests') {
            steps {
                sh '''
                  . venv/bin/activate
                  python manage.py test
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                  docker build -t ${IMAGE_NAME}:latest .
                '''
            }
        }
    }

    post {
        success {
            echo '✅ CI Pipeline Succeeded'
        }
        failure {
            echo '❌ CI Pipeline Failed'
        }
        always {
            cleanWs()
        }
    }
}