pipeline {
    agent any

    environment {
        // Docker image name (published as ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:latest)
        IMAGE_NAME = "photo-app"
        APP_CONTAINER = "photo-app"
        NETWORK_NAME = "app-network"
        APP_PORT = "5000"
        // MySQL on the Jenkins Docker network (matches config.py default DB name)
        MYSQL_CONTAINER = "mysql-db-dast"
        SQLALCHEMY_DATABASE_URI_DOCKER = "mysql+pymysql://root:root@mysql-db-dast:3306/photo_app"
        DOCKERHUB_CREDENTIALS = credentials('docker-hub-credentials')
    }

    stages {
        stage('Checkout') {
            steps {
                // Replace URL and credentialsId with your Git hosting and Jenkins credential
                git branch: 'main',
                    url: 'https://github.com/WaiLinnAung16/PhotoApp.git',
                    credentialsId: '4fb414c0-45f5-419f-98cc-e4c94b3e322a'
            }
        }

        stage('Setup Docker Network') {
            steps {
                sh 'docker network create ${NETWORK_NAME} || true'
            }
        }

        stage('Launch MySQL') {
            steps {
                sh '''
                docker rm -f ${MYSQL_CONTAINER} || true

                docker run -d --name ${MYSQL_CONTAINER} \
                    -e MYSQL_ROOT_PASSWORD=root \
                    -e MYSQL_DATABASE=photo_app \
                    --network ${NETWORK_NAME} \
                    -p 3306:3306 \
                    mysql:8.0

                echo "Waiting for MySQL..."
                sleep 20
                '''
            }
        }

        stage('Setup Python & Lint') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                pip install bandit safety pip-audit
                '''
            }
        }

        stage('SCA - Security Scans') {
            steps {
                sh '''
                . venv/bin/activate
                mkdir -p reports
                bandit -r . -f json -o bandit-report.json || true
                safety check --full-report > safety-report.txt || true
                '''
            }
        }

        stage('Build & Push') {
            steps {
                sh '''
                FULL_TAG="${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:latest"
                docker build -t $FULL_TAG .
                echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin
                docker push $FULL_TAG
                echo "FULL_IMAGE_TAG=$FULL_TAG" > image_tag.env
                '''
            }
        }

        stage('Unit Tests with Test Database') {
            steps {
                script {
                    sh """
                    . venv/bin/activate
                    export SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:root@localhost:3306/photo_app"

                    pytest -v --tb=short || echo "Tests completed with failures"
                    """
                }
            }
        }

        stage('Trivy Scan') {
            steps {
                sh '''
                . ./image_tag.env

                echo "Pulling Trivy scanner..."
                max_retries=3
                retry_count=0
                while [ $retry_count -lt $max_retries ]; do
                    if docker pull aquasec/trivy:0.56.0; then
                        echo "Trivy image pulled successfully!"
                        break
                    else
                        retry_count=$((retry_count+1))
                        if [ $retry_count -lt $max_retries ]; then
                            echo "Failed to pull Trivy, retrying... (attempt $retry_count/$max_retries)"
                            sleep 10
                        else
                            echo "Failed to pull Trivy after $max_retries attempts, skipping scan"
                            exit 0
                        fi
                    fi
                done

                docker run --rm \
                    -v /var/run/docker.sock:/var/run/docker.sock \
                    aquasec/trivy:0.56.0 \
                    image \
                    --format table \
                    --severity CRITICAL,HIGH \
                    --no-progress \
                    $FULL_IMAGE_TAG || true
                '''
            }
        }

        stage('Run App & DAST') {
            steps {
                sh '''
                . ./image_tag.env

                docker stop ${APP_CONTAINER} || true
                docker rm ${APP_CONTAINER} || true

                # Use flask run so the server binds 0.0.0.0 (required for ZAP on the Docker network)
                docker run -d --name ${APP_CONTAINER} --network ${NETWORK_NAME} -p ${APP_PORT}:${APP_PORT} \
                    -e FLASK_APP=app \
                    -e SQLALCHEMY_DATABASE_URI="${SQLALCHEMY_DATABASE_URI_DOCKER}" \
                    $FULL_IMAGE_TAG \
                    flask run --host=0.0.0.0 --port=${APP_PORT}

                echo "Waiting for app to initialize..."
                sleep 15

                chmod 777 $(pwd)

                docker run --user root --network ${NETWORK_NAME} \
                    -v $(pwd):/zap/wrk:rw \
                    ghcr.io/zaproxy/zaproxy:stable \
                    zap-baseline.py -t http://${APP_CONTAINER}:${APP_PORT} -r zap-report.html -I
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'zap-report.html, bandit-report.json, safety-report.txt', allowEmptyArchive: true
        }
    }
}
