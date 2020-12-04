#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dev import *


ENABLE_S3_UPLOAD = True
S3_ACCESS_KEY = 'AKIAIOZWGUMS7XE6XG4A'
S3_SECRET_KEY = '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'
VIDEOS_PREFIX = '/games/demos/'
S3_BUCKET = 'electronics3'

REDIS_URL = '54.171.117.35'

# Celery config
RABBITMQ_SERVER = 'electronic:conejitoF3liz@52.18.192.120:5672'
CORE_QUEUE = 'core'
broker_url = 'amqp://%s//' % RABBITMQ_SERVER
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
imports = (
    'backend.games.counter.tasks',
    'backend.games.rfactor.tasks',
)
worker_hijack_root_logger = False
task_default_queue = CORE_QUEUE
task_default_exchange_type = 'direct'
task_default_routing_key = CORE_QUEUE
task_default_exchange = CORE_QUEUE
task_queues = (
   Queue(CORE_QUEUE, routing_key=CORE_QUEUE),
)

task_protocol = 1

# Log config
LOGGING_CONFIG = {
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
            'tags': ['cringer', 'beta']
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
dictConfig(LOGGING_CONFIG)


class CringerConfig(object):
    LOGCONFIG = LOGGING_CONFIG
    LOGCONFIG_QUEUE = ['cringer']
    LOGCONFIG_REQUESTS_ENABLED = True
    LOGCONFIG_REQUESTS_LOGGER = ''
    FLASK_LOG_LEVEL = 'DEBUG'
