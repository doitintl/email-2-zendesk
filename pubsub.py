import env
import logging
import utils

from google.cloud import pubsub
from google.cloud.pubsub import types


@utils.timer_func
def send_to_pubsub(messageId, caseNumber, content):
    
    client = pubsub.PublisherClient(
        batch_settings=types.BatchSettings(
            max_messages=500, # default 100
            max_bytes=1024, # default 1 MB
            max_latency=1.0 # default .01 seconds
        ),
    )
    future = client.publish(env.PUBSUB_TOPIC(), content.encode(encoding = 'UTF-8'), case_number=caseNumber, message_id=messageId)
    # future = client.publish(env.PUBSUB_TOPIC(), content)
    message_id = future.result()
    return message_id