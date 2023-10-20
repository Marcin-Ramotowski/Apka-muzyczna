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
                }
            }
        }
        stage('Test python app') {
            steps {
                sh 'docker exec muse pytest . --junit-xml=pytest_junit.xml'
            }
            post {
                always {
                    junit testResults: '**/*pytest_junit.xml'
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    sh 'docker tag muse registry.byst.re/muse:latest'
                    docker.withRegistry('https://registry.byst.re', '3c074810-ffdd-48a5-87c3-6f44051fca6d') {
                        docker.push('registry.byst.re/muse:latest')
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
