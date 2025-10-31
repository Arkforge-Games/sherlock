# Quick Manual Jenkins Pipeline Setup

Since you already have Jenkins running at http://192.168.1.22:8080, follow these steps to add the Sherlock pipeline:

## Step 1: Create New Pipeline Job

1. Go to http://192.168.1.22:8080
2. Click **"+ New Item"** (top left)
3. Enter name: `Sherlock-Pipeline`
4. Select: **Pipeline**
5. Click **OK**

## Step 2: Configure General Settings

In the configuration page:

### General Section:
- ☑ Check **"GitHub project"**
- **Project url**: `https://github.com/Arkforge-Games/sherlock/`

## Step 3: Configure Build Triggers

### Build Triggers Section:
- ☑ Check **"GitHub hook trigger for GITScm polling"**

(This will trigger builds when you push to GitHub)

## Step 4: Configure Pipeline

### Pipeline Section:

1. **Definition**: Select `Pipeline script from SCM`

2. **SCM**: Select `Git`

3. **Repository URL**: `https://github.com/Arkforge-Games/sherlock.git`

4. **Credentials**:
   - If you already have GitHub credentials, select them
   - If not, click **"Add"** → **"Jenkins"**:
     - **Kind**: `Username with password`
     - **Username**: `Arkforge-Games`
     - **Password**: `[Use your GitHub Personal Access Token from .myDocs/Credentials.txt]`
     - **ID**: `github-sherlock-token`
     - **Description**: `GitHub Token for Sherlock`
     - Click **Add**
   - Then select the credential you just created

5. **Branches to build**: `*/master`

6. **Script Path**: `Jenkinsfile`

## Step 5: Save

Click **"Save"** at the bottom

## Step 6: Test the Pipeline

1. Click **"Build Now"** on the left sidebar
2. Watch the build progress
3. Click on the build number (e.g., #1) to see details
4. Click **"Console Output"** to see logs

## What the Pipeline Will Do

The Jenkinsfile in the repo will automatically:

1. ✓ Checkout code from GitHub
2. ✓ Check Docker and Python versions
3. ✓ Run Python tests
4. ✓ Build Docker images
5. ✓ Stop old containers
6. ✓ Deploy new containers
7. ✓ Run health checks
8. ✓ Clean up old images

## Expected Result

After the pipeline runs successfully, you'll have:
- Sherlock web interface at: http://localhost:5050
- PostgreSQL at: localhost:5433
- Redis at: localhost:6380

## Troubleshooting

### If the build fails:

1. Check Console Output for errors
2. Make sure Docker is running on the Jenkins server
3. Verify GitHub credentials are correct
4. Check that ports 5050, 5433, 6380 are available

### To run builds automatically:

Set up a GitHub webhook:
1. Go to https://github.com/Arkforge-Games/sherlock/settings/hooks
2. Add webhook: `http://192.168.1.22:8080/github-webhook/`
3. Content type: `application/json`
4. Events: `Just the push event`

Now every git push will trigger a Jenkins build!
