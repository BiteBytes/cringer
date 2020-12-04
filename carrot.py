import sys
from celery import Celery
from argparse import ArgumentParser
import common.redis_con as redis
import datetime
from common import logengine
from uuid import uuid4

celery = None
ip = None
port = None
uuid = str(uuid4())
match = None

BACKEND_QUEUE = 'backend'
LIST_OF_QUEUES = 'HB_ATTACHED_QUEUES'
IS_ATTACHED = False

celery_config = {
    'broker_url': None,
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],

    'worker_hijack_root_logger': False,
    'task_default_queue': BACKEND_QUEUE,
    'task_default_exchange_type': 'direct',
    'task_default_routing_key': BACKEND_QUEUE,
    'task_default_exchange': BACKEND_QUEUE,
    'task_protocol': 1
}


def queue_name():
    name = 'hb_queue_%s_%s' % (ip, port)
    return name


def parser_guard():
    name = 'hb_parsing_guard_%s_%s' % (ip, port)
    return name


def prepare_redis():
    redis.delete(parser_guard())
    redis.delete(queue_name())


def read():
    last_msg = None
    log_line_number = 0
    while True:
        line = sys.stdin.readline()
        server = {'ip': ip, 'port': port}
        logengine.carrot_logline_received_inspection(server=server, running=uuid, logline=line, match=match)
        if line == "" or not line:
            break
        else:
            if line.startswith("L "):
                last_msg = send_line(line, last_msg=last_msg, log_line_number=log_line_number)
            elif 'restarted in order to receive the latest update' in line:
                # FIXME: It forces an update, however it should be revised here and into hinbrain
                send_line(
                    'L 12/19/2014 - 00:20:30: Your server needs to be restarted in order to receive the latest update.')
            print line


def send_line(line, last_msg=None, log_line_number=0):
    server = {'ip': ip, 'port': port}
    line = line.replace('\n', '').replace('\x00', '').replace('\xff', '')
    redis.redis_queue_push(queue_name(), line)
    now = datetime.datetime.now()
    secs = 0 if last_msg is None or (now - last_msg).seconds > 2 else 2
    last_msg = now
    celery.send_task('backend.css.parselogline', [{'ip': ip, 'port': port}], queue=BACKEND_QUEUE,
                     countdown=secs)
    logengine.carrot_logline_sended(
        server=server,
        running=uuid,
        logline=line,
        match=match,
        logline_number=log_line_number,
        append=line
    )
    log_line_number += 1
    return last_msg


def configure_log(config):
    log_tag = 'beta' if config == 'PROD' else 'dev'

    from logging.config import dictConfig
    # Log config
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,  # this fixes the problem

        'formatters': {
            'simple': {
                'format': '%(levelname)s\t%(asctime)s\t%(message)s\t',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'logstash': {
                'level': 'INFO',
                'class': 'logstash.TCPLogstashHandler',
                'host': '54.171.115.185',
                'port': 5044,  # Default value: 5959
                'message_type': 'logstash',  # 'type' field in logstash message. Default value: 'logstash'.
                'fqdn': False,  # Fully qualified domain name. Default value: false.
                'tags': ['carrot', log_tag]
            },
        },
        'loggers': {
            '': {
                'handlers': ['console', 'logstash'],
                'level': 'INFO',
                'propagate': False
            },
        }
    }
    dictConfig(logging_config)


def configure_celery():
    global celery
    celery = Celery()
    celery.config_from_object(celery_config)


#
if __name__ == "__main__":
    parser = ArgumentParser(conflict_handler='resolve')
    parser.add_argument("-p", dest="port", default=None, help="Port of server sending lines")
    parser.add_argument("-b", dest="broker", help="Rabbit broker to use, ampq url")
    parser.add_argument("-r", dest="redis_url", help="Redis url")
    parser.add_argument("-q", dest="redis_password", help="Redis password")
    parser.add_argument("-h", dest="ip", default=None, help="ip of server sending lines")
    parser.add_argument("-m", dest="match", default='match_not_received')

    args = parser.parse_args()

    port = args.port
    ip = args.ip
    celery_config['broker_url'] = 'amqp://' + args.broker + '//'
    match = args.match

    print port
    print ip
    print celery_config['broker_url']

    configure_log(args.broker)
    configure_celery()
    redis.redis_connect(redis_url=args.redis_url, redis_password=args.redis_password, redis_db=0)
    prepare_redis()

    logengine.carrot_started(server={'ip': ip, 'port': port}, running=uuid, append=repr(args.__dict__))

    read()
