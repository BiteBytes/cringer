#!/usr/bin/env python
# -*- coding: utf-8 -*-

IP = None
LAST_CONFIG = ''

# 5.57.224.145
# 54.171.47.86:2701


def get_result(result):
    import jsonpickle
    r = jsonpickle.decode(result)
    return r['result'], r


def ask_default_value(value, defvalue):
    cmd = '%s [%s] > ' % (value, defvalue)
    val = raw_input(cmd)
    return defvalue if not val else val


def call_webservice(ws, **kwargs):
    import requests
    url = 'http://%s/%s' % (IP, ws)
    try:
        return requests.post(url, kwargs).text
    except Exception as e:
        print e
        return ''


def create_config(game_type=None):
    global LAST_CONFIG
    log_address = ask_default_value('log address', '')
    if not game_type:
        game_type = ask_default_value('game type', 'csgo')
    srv_pass = ask_default_value('server password', 'nocr1p')
    result = call_webservice('create_config',
                             logaddress=log_address,
                             game_type=game_type,
                             server_password=srv_pass)
    result, res = get_result(result)
    if result == 'ok':
        LAST_CONFIG = res['config_path']
    print 'Result for creating config:', res
    return result == 'ok'


def start_server(num=1, ini_port=None):
    from time import sleep
    gtype = ask_default_value('game type', 'csgo')
    port = ask_default_value('port', '27504') if not ini_port else ini_port
    config = ask_default_value('config', LAST_CONFIG)
    mode = ask_default_value('mode', 'classic')
    map = ask_default_value('map', 'de_aztec')
    system = ask_default_value('system', 'DEV')
    token = ask_default_value('token', '1A637631A1E0280E516247445CD54CAA')

    if not config:
        create_config(gtype)
        config = LAST_CONFIG

    for val in xrange(int(num)):
        tport = int(port) + int(val)
        result = call_webservice('start_server',
                                 game_type=gtype,
                                 port=tport,
                                 config=config,
                                 mode=mode,
                                 map=map,
                                 system=system,
                                 token=token)
        print 'Result for start server', tport, ':', result
        sleep(2)



def start_servers():
    port = ask_default_value('initial port', '27500')
    num = ask_default_value('num of servers', '2')
    start_server(num, port)


def show_help():
    print commands.keys()


def stop_server(port=None):
    if port is None:
        port = ask_default_value('port', '27500')
    result = call_webservice('stop_server',
                             port=port)
    print result
    print 'Result for stop server:', get_result(result)


def stop_servers():
    port = ask_default_value('initial port', '27500')
    num = ask_default_value('num of servers', '2')
    for n in range(int(num)):
        stop_server(port + str(n))


def update():
    gtype = ask_default_value('game type', 'csgo')
    result = call_webservice('update',
                             game_type=gtype)
    print result
    print 'Result for update:', get_result(result)


def list_servers():
    result = call_webservice('list_servers')
    print result


def status():
    ip = ask_default_value('ip', IP)
    port = ask_default_value('port', '27500')
    result = call_webservice('status',
                             server=ip,
                             port=port)
    print result


def update_config():
    gtype = ask_default_value('game type', 'csgo')
    result = call_webservice('prepare',
                             game_type=gtype)
    print result


def change_ip():
    global IP
    IP = None
    while not IP:
        IP = raw_input('Insert the IP:PORT like 127.0.0.1:8080 > ')


def close_all():
    import jsonpickle
    result = call_webservice('list_servers')
    print result
    result = '{"result":' + result.replace("'", '"') + '}'
    l = jsonpickle.decode(result)
    vals = l['result']
    ws = ask_default_value('Web services identifier', 'ws')
    for v in vals:
        if v != ws:
            stop_server(v)


def current_config():
    result = call_webservice('current_config')
    print result


def upload_video():
    gtype = ask_default_value('game type', 'csgo')
    gname = ask_default_value('game name', 'file')
    result = call_webservice('upload_demofile',
                             game_type=gtype,
                             game_name=gname)
    print result


def define_match():
    from celery import Celery
    celery_config = {
        'broker_url': 'amqp://52.18.75.89//',
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
    celery.config_from_object(celery_config)
    with open('start_match/01.txt') as f:
        lines = f.readlines()
        celery.send_task('backend.css.startmatch', [''.join(lines)], queue='backend', countdown=2)


def doit():
    create_config()
    start_server()
    define_match()


commands = {
    'create_config': create_config,
    'help': show_help,
    'exit': exit,
    'start_server': start_server,
    'stop_server': stop_server,
    'update': update,
    'status': status,
    'list': list_servers,
    'replace_configs': update_config,
    'change_ip': change_ip,
    'start_servers': start_servers,
    'stop_all': close_all,
    'current_config': current_config,
    'stop_servers': stop_servers,
    'upload_video': upload_video,
    'define_match': define_match,
    'do': doit
}

if __name__ == '__main__':
    import sys

    global IP
    if len(sys.argv) > 1:
        IP = sys.argv[1]
    if IP:
        print 'Connection to', IP
    else:
        change_ip()
    while True:
        cmd = raw_input('> ')
        cmd = commands.get(cmd, None)
        if cmd is None:
            continue
        cmd()