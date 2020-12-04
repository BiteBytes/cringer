#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from urlparse import urlparse
from flask import Flask, Response, request
from jsonpickle import encode
import common.csgo as csgo
import amazon
import supervisor
from SourceLib import SourceQuery
from common import utils
from cringer import JINJA_ENV, config
from common import logengine

app = Flask(__name__)
app.config.from_object(config.CringerConfig)


@app.before_request
def log_request():
    logengine.request_received(
        url=request.url,
        method=request.method,
        remote_addr=request.remote_addr,
        append='%s %s' % (request.method, request.url),
        loglevel='DEBUG' if request.url.endswith('/check') else 'INFO'
    )


@app.errorhandler(Exception)
def all_exception_handler(error):
    logengine.something_failed(
        error=error,
        url=request.url,
        method=request.method,
        remote_addr=request.remote_addr,
        append=str(error)
    )
    return 'Internal server error', 500


@app.after_request
def log_response(response):
    logengine.response_sended(
        status=response.status,
        data=response.get_data(),
        url=request.url,
        remote_addr=request.remote_addr,
        append='%s %s %s' % (request.method, request.url, str(response.status)),
        loglevel='DEBUG' if request.url.endswith('/check') else 'INFO'
    )
    return response


def log_response(value):
    _result = {
        'verb': request.method,
        'path': request.path,
        'from': extract_ip(request.base_url),
        'form': encode({k: request.form[k] for k in request.form.keys()}),
        'response': value
    }
    _value = 'For Request: {verb} {path}, {form}, from {from}. Response is: {response}'.format(**_result)
    app.logger.debug(_value)


def response_from_dict(value):
    json = encode(value)
    log_response(json)
    return Response(json, mimetype='application/json')


def response_error_dict(exception):
    return response_from_dict({
        'result': 'error',
        'message': str(exception)
    })


def response_ok_dict(**kwargs):
    okd = {
        'result': 'ok'
    }
    okd.update(kwargs)
    return response_from_dict(okd)


def response_not_allowed_dict():
    return response_from_dict({})


def allowed():
    return request.remote_addr in config.WHITE_LIST or '*' in config.WHITE_LIST


def extract_ip(url):
    val = urlparse(url)
    return val.hostname


def get_new_configfile(config_path):
    utils.prepare_path(config_path)
    return utils.get_new_file(config_path, prefix='hb_', sufix='.cfg')


def write_file_config(content, gtype):
    conf_path = csgo.config_path()
    f = get_new_configfile(conf_path)
    f.write(content)
    f.close()
    app.logger.debug('Created file ' + f.name)
    return os.path.basename(f.name)


def write_config(password, logaddress, srv_password, gtype, server_name, enable_tv):
    tv_text = """
tv_enable 1 
tv_autorecord 0
tv_maxclients 128
tv_debug 1
tv_autorecord 0
tv_advertise_watchable 1
        """

    _password_line = 'sv_password "%s"' % password if password is not None else ''
    template = JINJA_ENV.get_template('servercfg.tpl')
    template_vals = {
        'password': _password_line,
        'logaddress': logaddress,
        'srv_password': srv_password,
        'srv_name': server_name,
        'tv_text': tv_text if enable_tv else ''
    }
    content = template.render(template_vals)
    return write_file_config(content, gtype)


def run_server(**kwargs):
    try:
        port = kwargs['port']
        cmd, base_path = csgo.start_command(**kwargs)
        assert cmd is not None
        logengine.starting_server(command=cmd, append=cmd)
        supervisor.kill_process_in_port(port)
        result = supervisor.run(port, cmd, base_path, **kwargs)
        if result['std_err']:
            raise Exception(result['std_err'])
        return response_ok_dict()
    except Exception as e:
        return response_error_dict(e)


@app.route("/stop_server", methods=['POST'])
def stop_server():
    if not allowed():
        return response_not_allowed_dict()
    port = request.form['port']
    try:
        supervisor.terminate(str(port))
        result = response_ok_dict()
    except Exception as e:
        result = response_error_dict(e)
    return result


@app.route("/start_server", methods=['POST'])
def start_server():
    if not allowed():
        return response_not_allowed_dict()
    result = run_server(
        config_file=request.form.get('config', ''),
        gtype=request.form.get('game_type', ''),
        ip=extract_ip(request.base_url),
        port=request.form.get('port', ''),
        mode=request.form.get('mode', 'csgo'),
        map=request.form.get('map', None),
        system=request.form.get('system', 'DEV'),
        token=request.form.get('token', ''),
        match=request.form.get('match', 'not_known')
    )
    return result


@app.route("/create_config", methods=['POST'])
def create_config():
    if not allowed():
        return response_not_allowed_dict()
    password = request.form.get('password', None)
    logaddress = request.form.get('logaddress', '')
    gtype = request.form.get('game_type', '')
    srv_pass = request.form.get('server_password', 'nocr1p')
    server_name = request.form.get('match_name', 'Electronicstars')
    enable_tv = request.form.get('enable_tv', True)
    try:
        path = write_config(password, logaddress, srv_pass, gtype, server_name, enable_tv)
        return response_ok_dict(config_path=path)
    except Exception as e:
        return response_error_dict(e)


@app.route("/status", methods=['POST'])
def status():
    if not allowed():
        return response_not_allowed_dict()
    port = int(request.form['port'])
    ip = request.form.get('server', extract_ip(request.base_url))
    ip = ip.split(':')[0]
    try:
        server = SourceQuery.SourceQuery(ip, port)
        return response_ok_dict(status=server.info())
    except Exception as e:
        return response_error_dict(e)


@app.route("/list_servers", methods=['get', 'post'])
def list_servers():
    if not allowed():
        return response_not_allowed_dict()
    try:
        value = supervisor.running_processes()
        if value is None:
            raise Exception('Not status')
        log_response(value.keys())
        return Response(str(value.keys()))
    except Exception as e:
        return response_error_dict(e)


@app.route("/update", methods=['post'])
def update_server():
    if not allowed():
        return response_not_allowed_dict()
    try:
        ip = request.host.split(':')[0]
        csgo.update(
            ip=ip
        )
        return response_ok_dict()
    except Exception as e:
        return response_error_dict(e)


@app.route("/current_config", methods=['post'])
def current_config():
    from cringer import config_file, config
    if not allowed():
        return response_not_allowed_dict()
    try:
        return response_ok_dict(
            config_file=config_file,
            core_queue=config.CORE_QUEUE
        )
    except Exception as e:
        return response_error_dict(e)


def upload_demo(gname):
    fle = csgo.file_to_upload(
        game_name=gname
    )
    target = config.VIDEOS_PREFIX + gname + '.dem'
    if config.ENABLE_S3_UPLOAD:
        amazon.upload_file(fle, target, gname)
    return target


def remove_log_files():
    import os
    import datetime
    try:
        pth = config.CSGO_LOG_PATH
        now = datetime.datetime.now()
        log_files = [(os.path.join(pth, f), now - datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(pth, f))))
                     for f in os.listdir(pth) if f.endswith('.log')]
        frontier_seconds = config.LOG_ERASE_LAST_HOURS * 60 * 60
        valid_log_files = [f[0] for f in log_files if f[1].total_seconds() >= frontier_seconds]
        num_files = len(valid_log_files)
        for f in valid_log_files:
            os.remove(f)
        return num_files
    except Exception as e:
        return 'Error ' + str(e)


def remove_round_files(gname):
    import os
    try:
        pth = config.CSGO_BCK_ROUND_PATH
        files = [os.path.join(pth, f) for f in os.listdir(pth) if f.startswith(gname) and 'round' in f]
        round_files = len(files)
        for f in files:
            os.remove(f)
        return round_files
    except Exception as e:
        return 'Error ' + str(e)


@app.route("/upload_demofile", methods=['post'])
def upload_video():
    if not allowed():
        return response_not_allowed_dict()
    try:
        gname = request.form['game_name']
        target = upload_demo(gname)
        n_round = remove_round_files(gname)
        n_log = remove_log_files()
        return response_ok_dict(
            video_file=target,
            round_files_removed=n_round,
            log_files_removed=n_log
        )
    except Exception as e:
        return response_error_dict(e)


@app.route("/delete_demofile", methods=['post'])
def delete_video():
    if not allowed():
        return response_not_allowed_dict()
    try:
        import os
        gname = request.form['game_name']
        fle = csgo.file_to_upload(
            game_name=gname
        )
        os.remove(fle)
        return response_ok_dict()
    except Exception as e:
        return response_error_dict(e)


@app.route("/check", methods=['get'])
def check_cringer():
    from common.redis_con import redis_ping, redis_connect
    import carrot
    import time
    import psutil
    import datetime

    values = {}

    try:
        logengine.logging.debug("Checking redis")
        redis_connect(
            redis_url=config.REDIS_URL,
            redis_password=config.REDIS_PASSWORD,
            redis_db=0
        )
        start_time = time.time()
        values['redis'] = {
            'ping': redis_ping(),
            'time': (time.time() - start_time)
        }
    except:
        logengine.check_redis_error()

    try:
        carrot.celery_config['broker_url'] = config.broker_url
        logengine.logging.debug("Checking celery " + repr(carrot.celery_config))
        carrot.configure_celery()
        logengine.logging.debug("Celery configured")
        start_time = time.time()
        values['celery'] = {
            'ping': carrot.celery.control.ping(),
            'time': (time.time() - start_time)
        }
    except:
        logengine.check_celery_error()

    try:
        logengine.logging.debug("Checking the system")
        values['running'] = supervisor.running_processes().keys()

        values['cpu'] = dict(psutil.cpu_times().__dict__)
        values['cpu']['percent'] = psutil.cpu_percent(interval=1, percpu=True)
        values['cpu']['percent_avg'] = sum(values['cpu']['percent'])/float(len(values['cpu']['percent']))
        values['memory'] = {
            'virtual': dict(psutil.virtual_memory().__dict__),
            'swap': dict(psutil.swap_memory().__dict__)
        }

        values['disk'] = [dict(d.__dict__) for d in psutil.disk_partitions()]
        [v.update(psutil.disk_usage(v['mountpoint']).__dict__) for v in values['disk']]

        logengine.logging.debug("Checkeck everything")
        restoring_time = -1
        if os.path.exists('./maintenance'):
            restoring_time = (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime('./maintenance'))).total_seconds()
        values['maintenance'] = 'Maintenance started %s secs ago' % int(restoring_time) if restoring_time != -1 else -1
    except:
        logengine.check_system_error()

    return response_ok_dict(result=values)


@app.route("/restore", methods=['get'])
def restore():
    from common.csgo import restore
    restore()
    return response_ok_dict()


@app.route("/sync_maps")
def sync_maps():
    csgo.sync_new_maps(True)
    return response_ok_dict()
