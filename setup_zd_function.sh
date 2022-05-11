#!/bin/bash

# ----------------------------------
# Installs Cloud Function for ZenDesk updates from PubSub.
# ----------------------------------
source scripts/args.bash

NAME=pubsub_2_zendesk
ENTRY_POINT=main
LABELS="app=pubsub_2_zendesk"
MEMORY=128MB
REGION=us-central1
SOURCE_DIR="zendesk/"
TOPIC="gcp-vendor-support-messages"

if [ $ACTION = "apply" ]; then
    gcloud functions deploy $NAME \
        --entry-point $ENTRY_POINT \
        --memory $MEMORY \
        --region $REGION \
        --runtime python38 \
        --set-env-vars "project_id=$(gcloud config get-value project)" \
        --source $SOURCE_DIR \
        --trigger-topic $TOPIC \
        --update-labels $LABELS \
        --retry 
else
    echo ${bold}"Removing function..."${reset}
    gcloud functions delete $NAME --region $REGION
fi