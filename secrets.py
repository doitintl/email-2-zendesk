import logging
from google.cloud import secretmanager
import env


secrets_client = secretmanager.SecretManagerServiceClient()


def secret(secret_name):
    try:
        name = f"projects/{ env.PROJECT_ID() }/secrets/{secret_name}/versions/latest"
        response = secrets_client.access_secret_version(request={"name": name})
        # logging.debug(f"Secret retrieval success [{ name }]", exc_info=True)
        return response.payload.data.decode("UTF-8")
    except Exception as ex:
        logging.error(f"Secret retrieval error [{ name }]", exc_info=True)
        return "" 


def IMAP_CREDS():
    secret_value = secret(env.IMAP_SECRET_NAME())
    creds = secret_value.split(',')
    try:
        if len(creds) == 2:
            return creds[0], creds[1]
    except Exception as ex:
        logging.debug(f"ERROR: error retrieving credentials from {env.IMAP_SECRET_NAME}. {ex}")
    return None, None
