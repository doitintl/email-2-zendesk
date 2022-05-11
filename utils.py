# import datetime
# import env
import logging
from time import time
import arrow


def write_to_file(message_id, case_number, content):
    with open(f'messages/{message_id}.txt', 'w') as f:
        f.write(content)
    return 1


def timer_func(func):
    # This function shows the execution time of 
    # the function object passed
    def elapsed_time_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        logging.info(f'Function {func.__name__!r} executed at {arrow.get(t1).format(arrow.FORMAT_ATOM)} for {(t2-t1):.4f}s')
        return result
    return elapsed_time_func


log_config = {
    "version": 1,
    "root":{
        "handlers" : ["console"],
        "level": "DEBUG"
    },
    "handlers":{
        "console":{
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "DEBUG"
        }
    },
    "formatters":{
        "std_out": {
            "format": "%(asctime)s : %(levelname)s : %(module)s.%(funcName)s : %(lineno)d : %(message)s",
            "datefmt":"%d-%m-%Y %I:%M:%S"
        }
    },
}

log_config_debug = {
    "version": 1,
    "root":{
        "handlers" : ["console", "file"],
        "level": "DEBUG"
    },
    "handlers":{
        "console":{
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "DEBUG"
        },
        "file":{
            "formatter":"std_out",
            "class":"logging.FileHandler",
            "level":"INFO",
            "filename":"all_messages.log"
        }
    },
    "formatters":{
        "std_out": {
            "format": "%(asctime)s : %(levelname)s : %(module)s : %(funcName)s : %(lineno)d : %(message)s",
            "datefmt":"%d-%m-%Y %I:%M:%S"
        }
    },
}