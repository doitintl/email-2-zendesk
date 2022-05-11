_mainScript_() {

  if [ $ACTION = "apply" ]; then
    if serviceAccountExists $SA_ACCOUNT == 0; then
      echo "Service Account [$SA_ACCOUNT] does not exists."
    else
      if topicExists $TOPIC; then
        echo "Topic [$TOPIC] already exists."
      else
        echo ${bold}"Applying resources in project [$PROJECT_ID]..."${reset}

        gcloud pubsub topics create $TOPIC --labels $LABELS
        gcloud pubsub subscriptions create $SUBSCRIPTION --topic $TOPIC --labels $LABELS
        gcloud pubsub topics add-iam-policy-binding projects/$PROJECT_ID/topics/$TOPIC \
          --member "serviceAccount:"$SA_ACCOUNT \
          --role $SA_ROLE_PUBSUB  > /dev/null
        # Test message
        gcloud pubsub topics publish $TOPIC --message "{\"welcome\": {\"app\": \"$APP\", \"next\": \"Install the logging Cloud Function\"}}"
      fi
    fi
  else
    echo ${bold}"Removing resources..."${reset}
    gcloud pubsub subscriptions delete $SUBSCRIPTION
    deleteTopic $TOPIC 1
  fi

  echo ${bold}"Script complete."${reset}

} # end _mainScript_