
pipeline {

    agent any

    environment {

        IMAGE_NAME = "autoheal-app"

        IMAGE_TAG = "1.0"
    }

    stages {

        stage('Checkout') {

            steps {

                checkout scm
            }
        }

        stage('Install Dependencies') {

            steps {

                sh '''
                    python3 -m pip install -r app/requirements.txt
                    python3 -m pip install -r controller/requirements.txt
                '''
            }
        }

        stage('Run Tests') {

            steps {

                sh '''
                    python3 -m unittest discover -s tests -v
                '''
            }
        }

        stage('Build Docker Image') {

            steps {

                sh '''
                    docker build \
                    -t ${IMAGE_NAME}:${IMAGE_TAG} \
                    ./app
                '''
            }
        }
    }

    post {

        always {

            echo 'AutoHeal CI/CD pipeline completed.'
        }
    }
}

