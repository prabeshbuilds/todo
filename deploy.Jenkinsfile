pipeline {
    agent any

    triggers {
        githubPush()
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    environment {
        APP_NAME      = 'django-todo'
        IMAGE_TAG     = "${env.GIT_COMMIT.take(7)}"

        DEPLOY_SERVER = '185.199.53.175'
        DEPLOY_USER   = 'prabesh'
        DEPLOY_PORT   = '22'
        APP_PORT      = '8000'

        ENV_FILE      = '/home/prabesh/.env'
    }

    stages {

        stage('📋 Pipeline Info') {
            steps {
                echo """
🚀 DJANGO CI/CD PIPELINE
Build   : #${env.BUILD_NUMBER}
Branch  : ${env.BRANCH_NAME ?: 'N/A'}
Commit  : ${IMAGE_TAG}
Server  : ${DEPLOY_SERVER}
"""
            }
        }

        stage('🐍 Setup Python Virtualenv') {
            steps {
                sh '''
                set -e

                # Remove old venv if exists
                [ -d venv ] && rm -rf venv

                # Create virtual environment
                python3 -m venv venv

                # Activate and upgrade pip safely
                . venv/bin/activate
                python -m pip install --upgrade pip setuptools wheel --break-system-packages

                # Install dependencies
                if [ -f requirements.txt ]; then
                    pip install -r requirements.txt --break-system-packages
                fi

                # Verify installation
                python --version
                pip --version
                '''
            }
        }

        stage('🧪 Django Lint & Test') {
            steps {
                sh '''
                # Activate virtualenv
                . venv/bin/activate


                # Run Django checks and migrations
                python manage.py check
                python manage.py migrate

                # Run Django tests
                python manage.py test
                '''
            }
        }

        stage('🔨 Build Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh '''
                    set -e
                    echo "Building Docker image..."
                    docker build --pull -t $DOCKER_USERNAME/$APP_NAME:$IMAGE_TAG .
                    docker tag $DOCKER_USERNAME/$APP_NAME:$IMAGE_TAG $DOCKER_USERNAME/$APP_NAME:latest
                    '''
                }
            }
        }

        stage('📤 Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh '''
                    set -e
                    echo "Logging in to DockerHub..."
                    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

                    echo "Pushing Docker images..."
                    docker push $DOCKER_USERNAME/$APP_NAME:$IMAGE_TAG
                    docker push $DOCKER_USERNAME/$APP_NAME:latest
                    '''
                }
            }
        }

        stage('🚀 Deploy to Production') {
    steps {
        withCredentials([usernamePassword(
            credentialsId: 'dockerhub-credentials',
            usernameVariable: 'DOCKER_USERNAME',
            passwordVariable: 'DOCKER_PASSWORD'
        )]) {
            sshagent(['deployment-server-ssh']) {
                sh '''
                set -e
                echo "Starting deployment..."

                ssh -o StrictHostKeyChecking=accept-new -p $DEPLOY_PORT $DEPLOY_USER@$DEPLOY_SERVER "
                    set -e
                    echo '✅ Connected to server'

                    # Create Docker network if missing
                    docker network inspect private-net >/dev/null 2>&1 || docker network create private-net

                    # Login to DockerHub on remote
                    echo '$DOCKER_PASSWORD' | docker login -u '$DOCKER_USERNAME' --password-stdin

                    # Stop old container by name if exists
                    docker ps -q --filter 'name=$APP_NAME' | xargs -r docker stop
                    docker ps -a -q --filter 'name=$APP_NAME' | xargs -r docker rm

                    # Pull latest image
                    docker pull $DOCKER_USERNAME/$APP_NAME:$IMAGE_TAG

                    # Run new container
                    docker run -d \
                        --name $APP_NAME \
                        --restart unless-stopped \
                        --network private-net \
                        --env-file $ENV_FILE \
                        -p $APP_PORT:8000 \
                        $DOCKER_USERNAME/$APP_NAME:$IMAGE_TAG

                    # Show last 20 logs
                    sleep 5
                    docker logs --tail 20 $APP_NAME

                    # Cleanup old images, keep last 5
                    docker images --format '{{.Repository}} {{.ID}} {{.CreatedAt}}' \
                        | grep $DOCKER_USERNAME/$APP_NAME \
                        | sort -rk3 \
                        | tail -n +6 \
                        | awk '{print \$2}' \
                        | xargs -r docker rmi || true
                "
                '''
            }
        }
    }
}
        stage('💚 Health Check') {
            steps {
                sh '''
                echo "=== Health Check ==="
                success=0
                for i in $(seq 1 10); do
                    if curl -s http://127.0.0.1:8000/ | grep -q "OK"; then
                        echo "✅ App is healthy"
                        success=1
                        break
                    else
                        echo "Waiting..."
                        sleep 5
                    fi
                done

                if [ $success -ne 1 ]; then
                    echo "❌ Health check failed"
                    exit 1
                fi
                '''
            }
        }

    }

    post {
        always {
            sh 'docker image prune -f'
        }
        success {
            echo "✅ Deployment succeeded!"
        }
        failure {
            echo "❌ Deployment failed!"
        }
    }
}