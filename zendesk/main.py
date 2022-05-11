import base64
import json
import logging
import os
from pprint import pprint
from urllib.parse import urlencode

import requests
from google.cloud import secretmanager
from google.cloud import pubsub

"""
Summary: Workflow
- find matching ticket based on vendor case #, if it exists add an internal comment to the ticket.
- triggered by PubSub message delivery.

References
https://developer.zendesk.com/documentation/developer-tools/working-with-the-zendesk-apis/making-requests-to-the-zendesk-api/
https://developer.zendesk.com/documentation/ticketing/using-the-zendesk-api/searching-with-the-zendesk-api/
"""

PROJECT_ID = os.environ.get("GCP_PROJECT", "")


def main(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
        event (dict): Event payload.
            {'@type': 'type.googleapis.com/google.pubsub.v1.PubsubMessage', 
            'attributes': {'case_number': '255', 'message_id': 'xyz'}, 
            'data': 'bWF5IDQsIDI6NTUgUE0gQ1NU'}
        context (google.cloud.functions.Context): Metadata for the event.
            {event_id: 4530563910852428, 
            timestamp: 2022-05-04T19:54:58.835Z, 
            event_type: google.pubsub.topic.publish, 
            resource: {
                'service': 'pubsub.googleapis.com', 
                'name': 'projects/garrett-00001/topics/cfn-test-topic', 
                'type': 'type.googleapis.com/google.pubsub.v1.PubsubMessage'}
            }
    """
    try:
        payload = base64.b64decode(event['data']).decode('utf-8')
        attrs = None
        case_number = ""

        if 'attributes' in event:
            attrs = dict(event['attributes'])
            case_number = attrs.get("case_number", "")
        # print(f"Case #: {case_number}, Data: {data}")
        if len(case_number) > 2:
            _update_zendesk_case(case_number, payload)
        else:
            print("Case number value not found in payload. Nothing to update in ZD.")

    except Exception as ex:
        print(f"Error occurred processing pubsub message. Error is: {ex}")        
        print(f"Error processing pubsub message {context.event_id} published at {context.timestamp}. Payload: {payload}")


def update_ZenDesk(vendorCaseNumber, vendorComment):
    ticketId = status = -1
    zendeskId = _get_zendesk_case_id(vendorCaseNumber)
    if zendeskId > 0:
        status = _update_zendesk_case(zendeskId, vendorComment)
        return status
    else:
        print(f"ZenDesk ticket not found for case number: {vendorCaseNumber}")
        return False


def _get_zendesk_case_id(vendorCaseNumber):
    ZD_FIELD_KEY = os.getenv('ZD_FIELD_KEY', "")
    ZD_SUBDOMAIN = os.getenv('ZD_SUBDOMAIN', "")

    id = -1
    vendorFieldValue = vendorCaseNumber

    # search_params = { 'query': 'type:ticket status:open' }
    search_params = { 'query': f'type:ticket custom_field_{ZD_FIELD_KEY}:{vendorFieldValue}' }
    url = f'https://{ ZD_SUBDOMAIN }.zendesk.com/api/v2/search.json?' + urlencode(search_params)
    logging.info(f"Url to be called: { url }")

    response = requests.get(url, auth=(secret("ZD_USER"), secret("ZD_TOKEN")))
    if response.status_code != 200:
        print('Status:', response.status_code, 'There was a problem retrieving ZenDesk case Id. Exiting.')
        exit()
    data = response.json()
    for result in data['results']:
        # print(result['subject'])
        id = result['id']
    if id:
        if id < 1:
            logging.debug(f"Matching ZenDesk case NOT found for vendor ticket # [{ vendorTicketNumber }]")
        else:
            logging.debug(f'Found matching ZenDesk case for value [{ vendorTicketNumber }]. match is ZD [{id}]')
    return id


def _update_zendesk_case(zendeskId, commentText):
    logging.info(f"Updating ZenDesk case: {zendeskId} to add comment: {commentText}")
    retVal = "-1"

    data = { 'ticket': { 'comment': { 'body': commentText, 'public': 'false' } } }
    payload = json.dumps(data)

    url = f'https://{ ZD_SUBDOMAIN }.zendesk.com/api/v2/tickets/' + str(zendeskId) + '.json'
    headers = {'content-type': 'application/json'}
    logging.info(f"Url to be called: { url }")

    response = requests.put(url, data=payload, auth=(secret("ZD_USER"), secret("ZD_TOKEN")), headers=headers)
    if response.status_code != 200:
        # print('Status:', response.status_code, 'Problem updating ticket. Exiting.')
        logging.error(f"There was an error updating the ZenDesk case: {zendeskId}. Response Code: { response.status_code }")
    
    retVal = response.status_code
    logging.info(f"ZenDesk case: {zendeskId} successfultly updated.")
    # pprint(response.json())
    return retVal


secrets_client = secretmanager.SecretManagerServiceClient()

def secret(secret_name):
    try:
        name = f"projects/{ PROJECT_ID }/secrets/{secret_name}/versions/latest"
        response = secrets_client.access_secret_version(request={"name": name})
        # logging.debug(f"Secret retrieval success [{ name }]", exc_info=True)
        return response.payload.data.decode("UTF-8")
    except Exception as ex:
        logging.error(f"Secret retrieval error [{ name }]", exc_info=True)
        return "" 