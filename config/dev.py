#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kombu import Queue
from logging.config import dictConfig

PORT = 8080
CSGO_PATH = '/home/steam/csgo'
UTILS_PATH = '/home/steam/cringer'
CSS_PATH = '/home/steam/css_server'
STEAM_PATH = '/home/steam/steamcmd/'
SUPERVISOR_CONFIG_PATH = '/etc/supervisor/conf.d/'
WHITE_LIST = ['*']
ENABLE_S3_UPLOAD = True
S3_ACCESS_KEY = 'AKIAIOZWGUMS7XE6XG4A'
S3_SECRET_KEY = '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'
VIDEOS_PREFIX = '/games/demos_dev/'

S3_BUCKET = 'electronics3'
S3_BUCKET_PREFIX_CSGO_ES_MAPS = 's3://electronics3/csgomaps/maps.es'
S3_BUCKET_PREFIX_CSGO_PUBLIC_MAPS = 's3://electronics3/csgomaps/maps'
S3_BUCKET_PREFIX_CSGO_OFFICIAL_MAPS = 's3://electronics3/csgomaps/maps.official'

CSGO_LOG_PATH = '/home/steam/csgo/csgo/logs/'
CSGO_BCK_ROUND_PATH = '/home/steam/csgo/csgo/'
LOG_ERASE_LAST_HOURS = 12


FLUENTD_SERVER = '52.24.81.71'
REDIS_URL = '34.253.186.31'
REDIS_PASSWORD = 'sYBiLgMlOMh1'

# Celery config

CORE_QUEUE = 'core'
task_protocol = 1

broker_url = 'amqp://estest:bi9cah8U@52.30.236.204:5672//'
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

def configure_log(level):
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
                'host': 'd5bd3498-f59a-4ae8-8185-d8d881beb99a-ls.logit.io',
                'port': 16998,  # Default value: 5959
                'message_type': 'logstash',  # 'type' field in logstash message. Default value: 'logstash'.
                'fqdn': False,  # Fully qualified domain name. Default value: false.
                'tags': ['cringer', 'dev']
            },
        },
        'loggers': {
            '': {
                'handlers': ['console', 'logstash'],
                'level': level,
                'propagate': False
            },
        }
    }
    dictConfig(LOGGING_CONFIG)
    return LOGGING_CONFIG


class CringerConfig(object):
    LOGCONFIG = configure_log('INFO')
    LOGCONFIG_QUEUE = ['cringer']
    LOGCONFIG_REQUESTS_ENABLED = True
    LOGCONFIG_REQUESTS_LOGGER = ''
    FLASK_LOG_LEVEL = 'DEBUG'

