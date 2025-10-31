#!/bin/bash

# Jenkins Configuration
JENKINS_URL="http://192.168.1.22:8080"
JENKINS_USER="admin"
JENKINS_PASSWORD="Jer64admin!!123"
JOB_NAME="Sherlock-Pipeline"

echo "Creating Jenkins job: $JOB_NAME"
echo ""

# Get Jenkins crumb
echo "Step 1: Getting Jenkins CSRF crumb..."
CRUMB=$(curl -s --user "$JENKINS_USER:$JENKINS_PASSWORD" "$JENKINS_URL/crumbIssuer/api/json" | grep -o '"crumb":"[^"]*"' | cut -d'"' -f4)

if [ -z "$CRUMB" ]; then
    echo "Error: Could not retrieve Jenkins crumb"
    exit 1
fi

echo "✓ Got crumb successfully"
echo ""

# Create the job
echo "Step 2: Creating pipeline job..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$JENKINS_URL/createItem?name=$JOB_NAME" \
  --user "$JENKINS_USER:$JENKINS_PASSWORD" \
  -H "Jenkins-Crumb:$CRUMB" \
  -H "Content-Type: application/xml" \
  --data-binary @jenkins-job-config.xml)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Jenkins job '$JOB_NAME' created successfully!"
    echo ""
    echo "View it at: $JENKINS_URL/job/$JOB_NAME/"
    echo ""
    echo "Next steps:"
    echo "1. Go to Jenkins: $JENKINS_URL"
    echo "2. Click on 'Sherlock-Pipeline'"
    echo "3. Click 'Build Now' to test the pipeline"
else
    echo "✗ Failed to create Jenkins job (HTTP $HTTP_CODE)"
    if echo "$BODY" | grep -q "already exists"; then
        echo "Job already exists! You can view it at: $JENKINS_URL/job/$JOB_NAME/"
    else
        echo "Error response:"
        echo "$BODY"
    fi
fi
