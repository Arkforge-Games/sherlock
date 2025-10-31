# Jenkins CI/CD Setup for Sherlock

Complete guide to set up Jenkins for automated building and deployment of the Sherlock project.

## Overview

Jenkins is configured to:
- Automatically build on Git push
- Run Python tests
- Build Docker images
- Deploy to Docker containers
- Perform health checks
- Clean up old resources

## Quick Start

### 1. Start Jenkins

```bash
# Start all services including Jenkins
docker-compose up -d

# Check if Jenkins is running
docker ps | grep sherlock_jenkins
```

### 2. Get Initial Admin Password

```bash
# Get the initial admin password
docker exec sherlock_jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Copy this password - you'll need it for the initial setup.

### 3. Access Jenkins

Open your browser to:
- **Local:** http://localhost:8081
- **Network:** http://192.168.1.22:8081

### 4. Initial Setup

1. Paste the admin password you copied
2. Click "Install suggested plugins"
3. Wait for plugins to install
4. Create your admin user:
   - Username: `admin`
   - Password: `Jer64admin!!123` (or your preferred password)
   - Full name: `Admin`
   - Email: `dev.anthonycastor@gmail.com`

5. Click "Save and Continue"
6. Keep the Jenkins URL as is and click "Save and Finish"

## Configure GitHub Integration

### 1. Install Additional Plugins

1. Go to **Manage Jenkins** → **Manage Plugins**
2. Click on **Available** tab
3. Search and install:
   - GitHub Integration Plugin
   - Docker Pipeline Plugin
   - Python Plugin
4. Restart Jenkins after installation

### 2. Add GitHub Credentials

1. Go to **Manage Jenkins** → **Manage Credentials**
2. Click on **(global)** domain
3. Click **Add Credentials**
4. Fill in:
   - Kind: `Username with password`
   - Username: `Arkforge-Games`
   - Password: `[Use your GitHub Personal Access Token]`
   - ID: `github-token`
   - Description: `GitHub Access Token`
5. Click **OK**

### 3. Create Jenkins Pipeline Job

1. Click **New Item**
2. Enter name: `Sherlock-Pipeline`
3. Select **Pipeline**
4. Click **OK**

5. Configure the pipeline:

#### General Section:
- ☑ GitHub project
- Project url: `https://github.com/Arkforge-Games/sherlock/`

#### Build Triggers:
- ☑ GitHub hook trigger for GITScm polling
- ☑ Poll SCM (optional, for backup)
  - Schedule: `H/5 * * * *` (every 5 minutes)

#### Pipeline Section:
- Definition: `Pipeline script from SCM`
- SCM: `Git`
- Repository URL: `https://github.com/Arkforge-Games/sherlock.git`
- Credentials: Select `github-token`
- Branch: `*/master`
- Script Path: `Jenkinsfile`

6. Click **Save**

## Configure GitHub Webhook

### 1. Go to GitHub Repository

1. Open https://github.com/Arkforge-Games/sherlock
2. Go to **Settings** → **Webhooks**
3. Click **Add webhook**

### 2. Configure Webhook

- Payload URL: `http://192.168.1.22:8081/github-webhook/`
- Content type: `application/json`
- Which events: `Just the push event`
- ☑ Active
- Click **Add webhook**

## Test the Pipeline

### 1. Manual Build

1. Go to your pipeline job
2. Click **Build Now**
3. Watch the build progress in **Console Output**

### 2. Automatic Build (Git Push)

```bash
# Make a small change
echo "# Test" >> README.md

# Commit and push
git add README.md
git commit -m "Test Jenkins pipeline"
git push origin master

# Jenkins will automatically start building
```

## Pipeline Stages

The Jenkinsfile includes these stages:

1. **Checkout** - Pull code from GitHub
2. **Environment Check** - Verify Docker, Python versions
3. **Run Tests** - Execute Python tests
4. **Build Docker Images** - Build sherlock_web container
5. **Stop Old Containers** - Clean up running containers
6. **Deploy** - Start new containers
7. **Health Check** - Verify services are running
8. **Cleanup** - Remove old Docker images

## Monitoring

### View Build History

1. Go to your pipeline job
2. See **Build History** on the left
3. Click on any build number to see details

### View Console Output

1. Click on a build number
2. Click **Console Output**
3. See real-time logs

### View Build Status

- 🔵 Blue ball = Success
- 🔴 Red ball = Failed
- ⚪ Gray ball = Aborted

## Jenkins Credentials Reference

| Item | Value |
|------|-------|
| URL (Local) | http://localhost:8081 |
| URL (Network) | http://192.168.1.22:8081 |
| Username | admin |
| Initial Password | `docker exec sherlock_jenkins cat /var/jenkins_home/secrets/initialAdminPassword` |
| GitHub Token | [Use your GitHub Personal Access Token from credentials file] |
| GitHub Repo | https://github.com/Arkforge-Games/sherlock.git |

## Common Commands

```bash
# Start Jenkins
docker-compose up -d sherlock_jenkins

# Stop Jenkins
docker-compose stop sherlock_jenkins

# View Jenkins logs
docker logs -f sherlock_jenkins

# Get initial password
docker exec sherlock_jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# Restart Jenkins
docker-compose restart sherlock_jenkins

# Access Jenkins container
docker exec -it sherlock_jenkins bash

# Backup Jenkins data
docker exec sherlock_jenkins tar czf - /var/jenkins_home > jenkins_backup.tar.gz

# Restore Jenkins data
docker exec -i sherlock_jenkins tar xzf - -C / < jenkins_backup.tar.gz
```

## Troubleshooting

### Jenkins Won't Start

```bash
# Check container status
docker ps -a | grep sherlock_jenkins

# View logs
docker logs sherlock_jenkins

# Restart container
docker-compose restart sherlock_jenkins
```

### Can't Access Jenkins UI

1. Check if port 8081 is available:
   ```bash
   lsof -i :8081
   ```

2. Check firewall settings

3. Try accessing via localhost:
   ```bash
   curl http://localhost:8081
   ```

### Build Fails

1. Check console output for errors
2. Verify Docker is running
3. Check if containers have enough resources
4. Verify GitHub credentials are correct

### GitHub Webhook Not Triggering

1. Check webhook delivery in GitHub:
   - Go to Settings → Webhooks
   - Click on your webhook
   - Check "Recent Deliveries"

2. Verify Jenkins URL is accessible from internet:
   ```bash
   curl http://192.168.1.22:8081/github-webhook/
   ```

3. Check Jenkins logs:
   ```bash
   docker logs sherlock_jenkins | grep webhook
   ```

## Environment Variables

Jenkins uses these environment variables from the pipeline:

```
PROJECT_NAME=sherlock
GITHUB_REPO=https://github.com/Arkforge-Games/sherlock.git
DEPLOY_HOST=192.168.1.22
DOCKER_COMPOSE_FILE=docker-compose.yml
```

## Best Practices

1. **Regular Backups**: Backup Jenkins data regularly
2. **Monitor Builds**: Check failed builds promptly
3. **Update Plugins**: Keep Jenkins plugins up to date
4. **Resource Management**: Monitor Docker resource usage
5. **Security**: Change default passwords
6. **Clean Up**: Regularly remove old Docker images

## Integration with eBOSS Project

Jenkins is configured to avoid conflicts with eboss_jenkins:

| Service | eBOSS Port | Sherlock Port |
|---------|-----------|---------------|
| Jenkins Web | 8080 | 8081 |
| Jenkins Agent | 50000 | 50001 |
| Container Name | eboss_jenkins | sherlock_jenkins |
| Volume | eboss_jenkins_data | sherlock_jenkins_data |

Both Jenkins instances can run simultaneously on the same server.

## Next Steps

After setting up Jenkins:

1. Configure email notifications for build failures
2. Set up build badges in GitHub README
3. Add more comprehensive tests
4. Configure deployment to production
5. Set up monitoring and alerts
