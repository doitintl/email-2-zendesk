#!/bin/bash

# ----------------------------------
# DON NOT EDIT SOURCE INCLUDES
# ----------------------------------
source scripts/utils.bash
source scripts/args.bash
source scripts/main.bash
source scripts/functions.bash

# ----------------------------------
# DESC
# Setup resources for gmail to Pub/Sub processing. 
# 
# Requirements
#   Role: Project Owner or Editor
# 
# Components (to be created)
#   PubSub Topic and Subscription
#   Cloud Function
# 
# Use
#   # use gcloud CLI to set current project.
#   gcloud config set project 'project_id'
#   
#   ./setup.sh action 
#   - action is one of apply or delete
# ----------------------------------

# ----------------------------------
# SET CONFIG'S/VARIABLES HERE...
# ----------------------------------

# Change the next three vars.
PROJECT_ID=$(gcloud config get-value project)

# Use custom or default compute service account
# SA_ACCOUNT="INSERT_SERVICE_ACCOUNT_EMAIL_HERE"
SA_ACCOUNT="562362468268-compute@developer.gserviceaccount.com"


APP="gcp-support-emails-to-pubsub"
TOPIC="gcp-vendor-support-messages"
SUBSCRIPTION="gcp-vendor-support-messages-default-sub"
SA_ROLE_PUBSUB="roles/pubsub.admin"
# SA_ROLE_SCC="roles/securitycenter.notificationConfigEditor"

# Appended to label 'created_by' key.
USER="bash_script"
LABELS="app=$APP,created_by=$USER,date=$(currentDateTimeAsLabel)"

# ----------------------------------
# DONT EDIT BELOW
# ----------------------------------

_mainScript_