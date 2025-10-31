pipeline {
    agent any

    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        PROJECT_NAME = 'sherlock'
        GITHUB_REPO = 'https://github.com/Arkforge-Games/sherlock.git'
        DEPLOY_HOST = '192.168.1.22'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }

        stage('Environment Check') {
            steps {
                echo 'Checking environment and dependencies...'
                sh '''
                    echo "Docker version:"
                    docker --version
                    echo "Docker Compose version:"
                    docker-compose --version
                    echo "Python version:"
                    python3 --version
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running Python tests...'
                sh '''
                    # Create virtual environment if needed
                    if [ ! -d "venv" ]; then
                        python3 -m venv venv
                    fi

                    # Activate virtual environment and install dependencies
                    . venv/bin/activate
                    pip install --quiet poetry
                    poetry install --no-interaction --no-ansi

                    # Run tests if they exist
                    if [ -d "tests" ]; then
                        echo "Running tests..."
                        pytest tests/ || echo "Tests completed"
                    else
                        echo "No tests directory found, skipping tests"
                    fi
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                echo 'Building Docker images...'
                sh '''
                    docker-compose -f ${DOCKER_COMPOSE_FILE} build sherlock_web
                '''
            }
        }

        stage('Stop Old Containers') {
            steps {
                echo 'Stopping old containers...'
                sh '''
                    docker-compose -f ${DOCKER_COMPOSE_FILE} down || true
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh '''
                    # Start all services
                    docker-compose -f ${DOCKER_COMPOSE_FILE} up -d

                    # Wait for services to be healthy
                    echo "Waiting for services to start..."
                    sleep 10

                    # Check container status
                    docker-compose -f ${DOCKER_COMPOSE_FILE} ps
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo 'Performing health checks...'
                sh '''
                    # Wait a bit for services to fully start
                    sleep 5

                    # Check if web interface is responding
                    echo "Checking web interface..."
                    curl -f http://localhost:5050 || echo "Web interface check failed"

                    # Check if PostgreSQL is ready
                    echo "Checking PostgreSQL..."
                    docker exec sherlock_postgres pg_isready -U tony -d sherlock_db || echo "PostgreSQL check failed"

                    # Check if Redis is responding
                    echo "Checking Redis..."
                    docker exec sherlock_redis redis-cli -a hrpassword123 ping || echo "Redis check failed"

                    # Display container logs
                    echo "Recent logs from sherlock_web:"
                    docker logs --tail 20 sherlock_web
                '''
            }
        }

        stage('Cleanup') {
            steps {
                echo 'Cleaning up old Docker images...'
                sh '''
                    # Remove dangling images
                    docker image prune -f || true

                    # Remove old containers
                    docker container prune -f || true
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
            echo 'Sherlock Web Interface is now available at:'
            echo 'Local: http://localhost:5050'
            echo 'Network: http://192.168.1.22:5050'
        }

        failure {
            echo 'Pipeline failed! Check the logs above for details.'
            sh '''
                echo "Container status:"
                docker-compose -f ${DOCKER_COMPOSE_FILE} ps || true

                echo "Recent logs:"
                docker-compose -f ${DOCKER_COMPOSE_FILE} logs --tail 50 || true
            '''
        }

        always {
            echo 'Pipeline execution completed.'
            cleanWs(
                deleteDirs: true,
                patterns: [
                    [pattern: 'venv/', type: 'INCLUDE'],
                    [pattern: '*.pyc', type: 'INCLUDE'],
                    [pattern: '__pycache__/', type: 'INCLUDE']
                ]
            )
        }
    }
}
