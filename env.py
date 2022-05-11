import datetime
import logging
import os
from dotenv import load_dotenv


load_dotenv('.env')

def ARCHIVE_GMAIL_MESSAGES():
    return os.getenv('ARCHIVE_MESSAGES', 0)

def DEBUG():
    return os.getenv('DEBUG')

def IMAP_HOST():
    return os.getenv('IMAP_HOST', "imap.gmail.com")

def IMAP_SECRET_NAME():
    return os.getenv('IMAP_SECRET_NAME')

def LOG_LEVEL():
    level = os.getenv('LOG_LEVEL', "WARNING")
    if level == "DEBUG":
        return logging.DEBUG
    elif level == "INFO":
        return logging.INFO
    elif level == "WARNING":
        return logging.WARNING
    elif level == "ERROR":
        return logging.ERROR
    elif level == "CRITICAL":
        return logging.CRITICAL
    else:
        return logging.WARNING

def PUBSUB_TOPIC():
    _topic = os.getenv('PUBSUB_TOPIC')
    return f"projects/{PROJECT_ID()}/topics/{_topic}"

def PROJECT_ID():
    return os.getenv('PROJECT_ID')

def SEARCH_DAYS():
    return os.getenv('SEARCH_DAYS', 2)

def SEARCH_DATE():
    try:
        search_string = os.getenv('SEARCH_DATE', datetime.datetime.now())
        search_date = datetime.datetime.strptime(search_string, '%d-%b-%Y')
        # print(f"ENV DATE is {search_date}, type { type(search_date) }")
        return search_date
    except:
        # print(f"ENV value not readable. {search_string}")
        return datetime.datetime.now()

def SUPPORT_URL_SEARCHSTRING():
    return os.getenv('SUPPORT_URL_SEARCHSTRING', '>>><<<>>><<<')
