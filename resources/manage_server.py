#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from time import sleep
from threading import Thread
import copy
import json
import carrot
import uuid
import os


def start_server(**kwargs):
    url = 'http://%s:%d/' % (kwargs['ip'], kwargs['rest_port'])
    txt = None
    try:
        requests.post(url + 'stop_server', kwargs)
        data = requests.post(url + 'create_config', kwargs)
        values = json.loads(data.text)
        txt = values
        kwargs['config'] = values['config_path']
        print 'Starting server %s:%d with token %s' % (kwargs['ip'], kwargs['port'], kwargs['token'])
        return requests.post(url + 'start_server', kwargs).text
    except Exception as e:
        added = txt if txt is not None else ''
        print 'Error', e, added
        return ''


def stop_server(**kwargs):
    print 'Stopping server', kwargs['ip'], kwargs['port']
    url = 'http://%s:%d/' % (kwargs['ip'], kwargs.get('rest_port', 80))
    try:
        return requests.post(url + 'stop_server', kwargs)
    except Exception as e:
        return 'Error', e


def check_server(ip, port):
    task_name = 'backend.css.serversterted'
    exchange = 'backend'
    routing_key = 'backend'
    queue = 'backend'

    data = {'ip': ip, 'port': port, 'match_id': str(uuid.uuid4())}
    jdata = json.dumps(data)
    carrot.celery.send_task(task_name, (jdata,), exchange=exchange, routing_key=routing_key, queue=queue)


def status(**kwargs):
    from SourceLib import SourceRcon
    ip, port = (kwargs['ip'], kwargs['port'])
    rcon = SourceRcon.SourceRcon(ip, port, 'nocr1p')
    value = rcon.rcon('status')
    print 'status to %s:%s %s' % (ip, str(port), value)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='This script communicates with Cringer to start o stop a server')

    parser.add_argument('-s', help='Server IP', dest='ip', required=True)
    parser.add_argument('-p', help='Cringer Port', dest='rest_port', default=80, type=int)
    parser.add_argument('-sp', help='Server port', dest='port', type=int, default=27600)
    parser.add_argument('-n', help='Number of servers', dest='number', default=1, type=int)
    parser.add_argument('-secs', help='Number of seconds between calls', dest='secs', default=10, type=float)
    parser.add_argument('-m', help='Do it in multithreading', dest='multi', default=None, action='store_true')
    parser.add_argument('-t', help='Token', dest='token', default=None)
    parser.add_argument('-c', help='Call prepare server', dest='cprepare', default=False, action='store_true')
    parser.add_argument('-b', help='Brocker address', dest='brocker', default=None)
    parser.add_argument('-a', help='Action [start|stop|status]', dest='action', default='start')
    parser.add_argument('-tf', help='Token file, default: ' + os.path.dirname(os.path.realpath(__file__)) + '/tokens.txt', dest='tfile', default=os.path.dirname(os.path.realpath(__file__)) + '/tokens.txt')
    parser.add_argument('-o', help='Use only one port', dest='only_one', default=False, action='store_true')
    parser.add_argument('-mid', help='The match identifier', dest='match', default=None)
    parser.add_argument('-sl', help='Stops later', dest='stoplater', default=False, action='store_true')

    args = parser.parse_args()

    f = open(args.tfile)
    tokens = f.readlines()
    f.close()
    tokens = [args.token] if args.token else tokens
    tokens = [t.replace('\n', '') for t in tokens]

    inc = 0 if args.only_one else 1

    n = 0
    initial_port = args.port

    if args.cprepare:
        if args.brocker:
            carrot.celery_config['BROKER_URL'] = args.brocker
        carrot.configure_celery()

    action = None
    if args.action == 'stop':
        action = stop_server
    elif args.action == 'status':
        action = status
    else:
        action = start_server

    if args.multi:
        threads = []
        results = []

        def threadable_manage_server(position, values):
            import time
            time1 = time.time()
            results[position] = action(**values.__dict__)
            time2 = time.time()
            print '%s function took %0.3f ms' % ('start server', (time2 - time1) * 1000.0)

        while n < args.number:
            args.port = initial_port + (n * inc)
            args.token = tokens[n % len(tokens)]
            results.append(None)

            t = Thread(target=threadable_manage_server, args=(n, copy.deepcopy(args)))
            threads.append(t)
            t.start()

            if args.cprepare and action == start_server:
                check_server(args.ip, initial_port + (n * inc))

            n += 1
            if n >= args.number:
                break

        for t in threads:
            t.join()

        for n, r in enumerate(threads):
            print 'Server {0}, {1}, {2}'.format(n + 1, initial_port + (n * inc), str(results[n]))
            url = 'http://%s/status' % args.ip
            print requests.post(url, {'port': initial_port + n}).text

    else:
        while n < args.number:
            args.port = initial_port + (n * inc)
            args.token = tokens[n % len(tokens)]
            d = args.__dict__
            print 'Server {0}, {1}, {2}'.format(n + 1, args.port, action(**d))
            if args.cprepare and action == start_server:
                check_server(args.ip, args.port)
            n += 1
            if n >= args.number:
                break
            sleep(args.secs)
            if args.stoplater:
                stop_server(ip=args.ip, port=args.port)

"""
            from threading import Thread

            def function_start_server(num):
                args.port = initial_port + (num * inc)
                args.token = tokens[n % len(tokens)]
                d = args.__dict__
                print 'Server {0}, {1}, {2}'.format(num + 1, args.port, action(**d))
                if args.cprepare and action == start_server:
                    check_server(args.ip, args.port)
                sleep(args.secs)
                if args.stoplater:
                    stop_server(ip=args.ip, port=args.port)

            threads = []
            for x in xrange(5):
                n += 1
                if n >= args.number:
                    break
                t = Thread(target=function_start_server, args=(n, ))
                threads.append(t)
                t.start()
            for t in threads:
                t.join()
"""
