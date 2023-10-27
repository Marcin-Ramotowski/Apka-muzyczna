pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build app container') {
            steps {
                script {
                    sh '''
                    echo "SECRET_KEY=$(head -c 64 /dev/urandom | base64 | tr -d '/+=')" > .env
                    docker-compose up -d
                    docker exec muse python manage.py migrate
                    '''
                }
            }
        }
        stage('Test app container') {
            steps {
                script {
                    sh './test_container.sh'
                }
            }
            post {
                success {
                    echo "Container started successfully"
                }
                failure {
                    echo "Container do not started correctly"
                    sh 'docker logs muse'
                }
            }
        }
        stage('Test python app') {
            steps {
                sh 'docker exec muse pytest . --junit-xml=pytest_junit.xml'
                sh 'docker cp muse:/app/pytest_junit.xml .'
            }
            post {
                always {
                    junit testResults: 'pytest_junit.xml'
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    sh 'docker tag python-django-app_web <registry_url>/muse:latest'
                    docker.withRegistry('<registry_url>', '<credentials-id>') {
                    sh 'docker push <registry_url>/muse:latest'
                        }
                    }
                }
            }
        }
    post {
        cleanup {
            cleanWs()
        }
        always {
            sh 'docker-compose down'
        }
    }
}
