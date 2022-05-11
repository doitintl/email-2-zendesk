# import datetime
import email
import imaplib
import logging
from logging import config

import env
import mailbox
import pubsub
import secrets
import utils

"""
Summary: Pull vendor ticket responses from email and push into PubSub.
Workflow:
    Get email messages (vendor ticket responses)
    Validate case # & copy each message to Topic

References
- https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
- Imap search operators https://gist.github.com/martinrusev/6121028

"""

if env.DEBUG() == 1:
    config.dictConfig(utils.log_config_debug)
else:
    config.dictConfig(utils.log_config)


global imap_client


@utils.timer_func
def main():
    """
    """
    imap_client = None
    try:
        FOLDER_INBOX = 'Inbox'
        imap_client = mailbox.connect()

        count, messages = mailbox.get_messages(imap_client, FOLDER_INBOX)
        list_count = len(messages)
        if list_count < 1: 
            logging.info("No messages found.")
            return

        # logging.debug(f"Number of messages found for processing: { list_count }.")
        
        emails = sorted(messages, key = lambda i: i['mail_id'], reverse=False)   # Oldest first
        for email in emails:
            vendorTicketNumber = mailbox.parse_case_number(email.get('subject'))
            if vendorTicketNumber is None:
                logging.error(f"No ticket number found in subject: [{ email.get('subject') }]")
                break

            # logging.info(f"Processing message start for case #: {vendorTicketNumber}, { email.get('date') }, { email.get('subject')[0:34] }")
            
            result = pubsub.send_to_pubsub(email.get('message-id'), vendorTicketNumber, email.get('body'))
            # result = utils.write_to_file(email.get('message-id'), vendorTicketNumber, email.get('body'))

            if result:
                print(f"Result: { result }")
                if env.ARCHIVE_GMAIL_MESSAGES() == 1:
                    # mark message as deleted (archived)
                    mailbox.delete_message(imap_client, FOLDER_INBOX, email.get('message-id'))
            else:
                print(f"Error: { result }")
            # logging.info(f"Processing message finish for case #: {vendorTicketNumber}")

    except Exception as ex:
        logging.error(f"Error processing messages.", exc_info=True)
    finally:
        if imap_client:
            resp_code, response = imap_client.logout()
            # logging.info(f"Logout response: {resp_code}, {response}")


main()