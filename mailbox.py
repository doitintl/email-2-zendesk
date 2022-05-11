import email
import env
import imaplib
import logging
import utils
import secrets

global imap_client

import arrow


# gcp-support-dev@gdemo.co.il,tzvwisohofrqcnkg
@utils.timer_func
def connect():
    try:
        imap = imaplib.IMAP4_SSL( env.IMAP_HOST() )
        un, pwd = secrets.IMAP_CREDS()

        resp_code, response = imap.login(un, pwd)
        return imap
    except Exception as ex:
        logging.error(f"Error connecting to mail.", exc_info=True)
        return None


@utils.timer_func
def delete_message(imap, folder, messageId):
    """
    The imap search function returns a sequential id, meaning id 5 is the 5th email in your inbox.
    That means if a user deletes email 5, all email id's above email 5 are now pointing to the wrong email.

    That's not good and changes could affect the wrong email. Instead, use the UID
    """
    imap.select(mailbox=folder, readonly=False)
    DELETE_FILTER = '(HEADER Message-ID "%s")' % messageId
    # logging.info(f"Delete filter is: { DELETE_FILTER }")
    resp_code, response = imap.uid('search', None, DELETE_FILTER)

    for uid in response[0].decode().split():
        resp_code, response = imap.uid('STORE', uid, '+X-GM-LABELS', '\\Trash')
        # logging.debug(f"Delete success: {resp_code}, {response}; Message-ID: { messageId }")


@utils.timer_func
def get_messages(imap, folder):
    """
    """
    resp_code, message_count = imap.select(mailbox=folder, readonly=True)
    message_count = message_count[0].decode('UTF-8')

    tickets = []
    resp_code, message_ids = imap.search('UTF-8', search_filter())

    # retrieve content detail of each message
    for mail_id in message_ids[0].decode().split():
        resp_code, mail_data = imap.fetch(mail_id, '(RFC822)')
        message = email.message_from_bytes(mail_data[0][1])
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                # text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
                body = part.get_payload(decode=True).decode()
            if part.get_content_type() == 'text/html':
                body = part.get_payload(decode=True).decode()
        message_data = {
            'mail_id': mail_id, 
            'from': message.get('From'),
            'date': message.get('Date'),
            'subject': message.get('Subject'),
            'message-id': message.get('message-id'),
            'body': format_support_link(body),
            'message': message}
        tickets.append( message_data )
    return message_count, tickets


def search_filter():
    """ 
    Env variable 'SEARCH_DAYS' indicates how many days back to start.  
    """
    NUMBER_DAYS_TO_SEARCH = env.SEARCH_DAYS()

    SINCE_DATE = arrow.utcnow().shift(days=-int(NUMBER_DAYS_TO_SEARCH))
    filter = f'(FROM "esupport@google.com" SINCE "{ SINCE_DATE.strftime("%d-%b-%Y") }" SUBJECT "[Case#")'
    return filter


def parse_case_number(subject: str):
    """
    Searching for a valid case # in the subject.
    """
    subject = subject.replace(" ", "")
    idx1 = subject.index("[Case#")
    idx2 = subject.index("]")
    if (idx1 >= 0) and (idx2 > idx1 + 6):
        return subject[idx1 + 6:idx2]
    return None


def print_message(mail_id, msg):
    print(f"Mail ID   : {mail_id}")
    print("To         : {}".format(msg.get("To")))
    print("From       : {}".format(msg.get("From")))
    print("Date       : {}".format(msg.get("Date")))
    print("Subject    : {}".format(msg.get("Subject")))


def format_support_link(content):
    start = content.find(env.SUPPORT_URL_SEARCHSTRING())
    stop = content.find(" ", start)
    if start > -1:
        url = content[start:stop]
        br = url.find('<br/>')
        if br > -1:
            url = url[0:br].strip()
        link = f"<a href='{url}' target='_blank'>{url}</a>"
        content = content.replace(url, link)

    return content