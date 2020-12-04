#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery import Celery
import common.redis_con as redis
import datetime
from common import logengine
from uuid import uuid4
from time import sleep


celery = None
ip = None
port = None
uuid = str(uuid4())
match = None

BACKEND_QUEUE = 'backend'
LIST_OF_QUEUES = 'HB_ATTACHED_QUEUES'

celery_config = {
    'broker_url': '',
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


def read(ip, port):
    import random
    import time
    f = open('firehb/log.log')
    lines = f.readlines()
    log_line_number = 0
    last_msg = None
    for line in lines:
        server = {'ip': ip, 'port': port}
        logengine.carrot_logline_received_inspection(server=server, running=uuid, logline=line, match=match)
        if line == "" or not line:
            break
        else:
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
                logline_number=log_line_number)

            log_line_number += 1
            print line


def send_line(last_msg, line, log_line_number, server):
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
        logline_number=log_line_number)
    log_line_number += 1
    return line, last_msg


def configure_celery():
    global celery
    celery = Celery()
    celery.config_from_object(celery_config)


def random_string():
    import random
    import string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))


def random_int():
    return 10


def define_match(ip, port):
    from celery import Celery
    _celery_config = {
        'broker_url': celery_config['broker_url'],
        'task_serializer': 'json',
        'result_serializer': 'json',
        'accept_content': ['json'],
        'worker_hijack_root_logger': False,
        'task_default_queue': 'backend',
        'task_default_exchange_type': 'direct',
        'task_default_routing_key': 'backend',
        'task_default_exchange': 'backend',
        'task_protocol': 1
    }
    celery = Celery()
    celery.config_from_object(_celery_config)
    with open('firehb/01.txt') as f:
        lines = f.readlines()
        for i in xrange(len(lines)):
            lines[i] = lines[i].replace('{{ip}}', ip).replace('{{port}}', str(port))
        celery.send_task('backend.css.startmatch', [''.join(lines)], queue='backend', countdown=2)


def launch(ip=random_string(), port=random_int()):
    define_match(ip, port)
    read(ip, port)


if __name__ == "__main__":
    import multiprocessing
    import json

    config = json.load(open('firehb/config.json'))
    config = config['config']

    celery_config['broker_url'] = config['broker_url']
    configure_celery()
    redis.redis_connect(config['redis_ip'], redis_password=config['redis_password'])
    prepare_redis()

    while True:
        processes = []
        for n, i in enumerate(xrange(config['processes'])):
            server = config['servers'][n % len(config['servers'])]
            t = multiprocessing.Process(target=launch, args=(server['ip'], server['port']))
            processes.append(t)
            t.start()

        for i in processes:
            t.join()
