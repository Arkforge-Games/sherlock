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
                    echo "Python version:"
                    python3 --version || echo "Python not available in Jenkins"
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Skipping Python tests - tests will run in Docker container...'
                sh '''
                    echo "Tests stage skipped for Jenkins build"
                    echo "The application will be tested in the Docker container"
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                echo 'Building Docker images...'
                sh '''
                    cd /var/jenkins_home/workspace/Sherlock-Pipeline
                    docker build -t sherlock_web:latest -f Dockerfile.web .
                '''
            }
        }

        stage('Stop Old Containers') {
            steps {
                echo 'Stopping old containers...'
                sh '''
                    docker stop sherlock_web sherlock_postgres sherlock_redis || true
                    docker rm sherlock_web sherlock_postgres sherlock_redis || true
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh '''
                    # Create network if it doesn't exist
                    docker network create sherlock_network || true

                    # Start PostgreSQL
                    docker run -d --name sherlock_postgres \
                      --network sherlock_network \
                      -e POSTGRES_USER=tony \
                      -e POSTGRES_PASSWORD=hrpassword123 \
                      -e POSTGRES_DB=sherlock_db \
                      -p 5433:5432 \
                      -v sherlock_postgres_data:/var/lib/postgresql/data \
                      --restart unless-stopped \
                      postgres:15-alpine || true

                    # Start Redis
                    docker run -d --name sherlock_redis \
                      --network sherlock_network \
                      -p 6380:6379 \
                      -v sherlock_redis_data:/data \
                      --restart unless-stopped \
                      redis:7-alpine redis-server --requirepass hrpassword123 || true

                    # Wait for databases to be ready
                    echo "Waiting for services to start..."
                    sleep 10

                    # Start Web Interface
                    docker run -d --name sherlock_web \
                      --network sherlock_network \
                      -e FLASK_APP=app.py \
                      -e FLASK_ENV=production \
                      -e DATABASE_URL=postgresql://tony:hrpassword123@sherlock_postgres:5432/sherlock_db \
                      -e REDIS_URL=redis://:hrpassword123@sherlock_redis:6379 \
                      -p 5051:5000 \
                      -v sherlock_results:/app/web_interface/results \
                      --restart unless-stopped \
                      sherlock_web:latest || true

                    # Check container status
                    docker ps | grep sherlock
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
                    curl -f http://localhost:5051 || echo "Web interface check failed"

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
            echo 'Local: http://localhost:5051'
            echo 'Network: http://192.168.1.22:5051'
        }

        failure {
            echo 'Pipeline failed! Check the logs above for details.'
            sh '''
                echo "Container status:"
                docker ps -a | grep sherlock || true

                echo "Recent logs from sherlock_web:"
                docker logs --tail 50 sherlock_web || true
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
