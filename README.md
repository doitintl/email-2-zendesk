<h1 align="center">
<img  src="img/email-2-zendesk.png" alt="Email-2-ZenDesk" width="140px">
<br>Email-2-ZenDesk
</h1>
<h5 align="center"></h5>
<p align="center">
  <a href="#features">Features</a> •
  <a href="#requirements">Requirements</a> • 
  <a href="#installation">Installation</a> •
  <a href="#cleanup">Cleanup</a>
</p>

### Summary

Application service to retrieve email (gmail) messages to ZenDesk via Pub/Sub. Namely, this is used for retrieving vendor support (GCP) email responses with the final goal of adding these vendor response messages to the ZenDesk customer request.

### Features & Notes

The 'application' is two components.

1. Email to PubSub app that retrieves gmail messages and sends toPub/Sub

2. Cloud function triggered by Pub/Sub and updates ZenDesk

#### Notes

- Query capability is limited. It is not possible to retrieve a query such as 'get 5 most recent'. 

- If I high number of emails exist the request call can take a good amount of time. For this the app uses a 'number of days' variable to limit the days requested.

- The vendor ticket number is parsed from the email subject. If a number is not found it will not be updates to ZenDesk.

- The gmail message (email) is archived when it is inserted to Pub/Sub
  
  <!-- - add the email message content to the ZenDesk ticket as an internal comment -->
  
  <!-- - reformat the vendor web link as a hyperlink in the ZenDesk ticket -->

### Requirements

- Gmail account credentials
  - GCP production email: gcp.support@doit-intl.com 
    - tbd
  - GCP development email: gcp-support-dev@gdemo.co.il 
    - D01TD01T
    - D01T@gcp
- Apps should be enabled in the gmail account and a token generated instead of using a password
- Create/update the GCP secrets with the email credentials
- ZenDesk credentials
  - Production
    - Subdomain: tbd
    - Custom field ID: tbd
    - Username & password
  - Development
    - Subdomain: doitintl1602227475
    - Custom field ID: 360031367857
    - Username & password

### Installation

Enable project services

```bash
# Enable the services if it is not already enabled
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

Installation is two parts, one for each component.

##### Email-2-PubSub

Set the env variables & run setup apply | delete

```bash
# .env file variables
PROJECT="REPLACE_WITH_PROJECT_ID"
ARCHIVE_MESSAGES=1
PUBSUB_TOPIC=gcp-vendor-support-messages
SEARCH_DAYS=1

gcloud config set core/project $PROJECT

# create secret GCP_IMAP_CREDS; username & token comma delimited
#     such as username,token
print "GCP_IMAP_CREDS" | \
    gcloud secrets create GCP_IMAP_CREDS --data-file=- \
    --replication-policy user-managed \
    --locations us-central1

.setup.sh apply
```

##### PubSub-2-ZenDesk

Set the env variables, secrets & run setup apply | delete

```bash
# .env file variables
ZD_FIELD_KEY="360031367857"
ZD_SUBDOMAIN="doitintl1602227475"

gcloud config set core/project $PROJECT

# create secret ZenDesk username & password.
print "ZD_USER" | \
    gcloud secrets create ZD_USER --data-file=- \
    --replication-policy user-managed \
    --locations us-central1
print "ZD_TOKEN" | \
    gcloud secrets create ZD_TOKEN --data-file=- \
    --replication-policy user-managed \
    --locations us-central1

# grant access to CFN
gcloud secrets add-iam-policy-binding ZD_USER \
    --member serviceAccount:$(gcloud config get-value project)@appspot.gserviceaccount.com \
    --role roles/secretmanager.secretAccessor \
    --condition None
gcloud secrets add-iam-policy-binding ZD_PASSWORD \
    --member serviceAccount:$(gcloud config get-value project)@appspot.gserviceaccount.com \
    --role roles/secretmanager.secretAccessor \
    --condition None

# deploy
./setup_zd_function.sh apply 
```

### Cleanup

To remove resources use the gcloud scripts below.

```bash
# remove the Pubsub-2-ZenDesk & secrets
./setup_zd_function.sh delete
gcloud secrets delete ZD_USER
gcloud secrets delete ZD_TOKEN

# remove the Email-2-Pubsub & secrets
./setup.sh delete
gcloud secrets delete GCP_IMAP_CREDS
```
