#!/bin/bash

# Jenkins Configuration
JENKINS_URL="http://192.168.1.22:8080"
JENKINS_USER="admin"
JENKINS_PASSWORD="Jer64admin!!123"
JOB_NAME="Sherlock-Pipeline"

echo "Creating Jenkins job: $JOB_NAME"

# Get Jenkins crumb for CSRF protection
echo "Getting Jenkins crumb..."
CRUMB=$(curl -s --user "$JENKINS_USER:$JENKINS_PASSWORD" \
  "$JENKINS_URL/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)")

if [ -z "$CRUMB" ]; then
    echo "Warning: Could not get Jenkins crumb, trying without it..."
    CRUMB_HEADER=""
else
    echo "Got crumb: $CRUMB"
    CRUMB_HEADER="-H $CRUMB"
fi

# Create the job using Jenkins API
curl -X POST "$JENKINS_URL/createItem?name=$JOB_NAME" \
  --user "$JENKINS_USER:$JENKINS_PASSWORD" \
  $CRUMB_HEADER \
  --header "Content-Type: application/xml" \
  --data-binary @jenkins-job-config.xml

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Jenkins job '$JOB_NAME' created successfully!"
    echo "View it at: $JENKINS_URL/job/$JOB_NAME"
else
    echo ""
    echo "✗ Failed to create Jenkins job"
    echo "You may need to create it manually through the Jenkins UI"
fi
