#!/usr/bin/env python
# -*- coding: utf-8 -*-

import envoy
from cringer import JINJA_ENV
from cringer import config
from parse import parse
import os


def running_processes():
    val = envoy.run('supervisorctl status ')
    if val.std_out:
        lines = val.std_out.split('\n')
        processes = [parse('{identifier}RUNNING    pid {pid:d}, uptime {time}', l).named for l in lines if 'RUNNING' in l]
        for p in processes:
            p['identifier'] = p['identifier'].strip()
        processes = {p['identifier']: p for p in processes}
        return processes
    return None


def get_pid(identifier):
    val = envoy.run('supervisorctl status ' + str(identifier))
    if val.std_out:
        result = parse(str(identifier) + '{}RUNNING    pid {pid:d}, uptime {time}', val.std_out)
        if result:
            return result.named['pid']
    return None


def terminate_subprocess(identifier):
    import re
    r = envoy.run('ps -aux')
    vals = r.std_out
    lines = vals.split('\n')
    pids = [re.split(r' +', v)[1] for v in lines if 'port ' + str(identifier) in v]
    for pid in pids:
        envoy.run('kill -9 ' + str(pid))


def write_config(identifier, content):
    fname = identifier + '.conf'
    path = os.path.join(config.SUPERVISOR_CONFIG_PATH, fname)
    f = file(path, 'w')
    f.write(content)
    f.close()


def change_config(identifier, command, directory, **kwargs):
    template = JINJA_ENV.get_template('supervisord.conf.tpl')
    template_vals = {
        'name': identifier,
        'command': command,
        'directory': directory
    }
    template_vals.update(kwargs)
    content = template.render(template_vals)
    write_config(identifier, content)


def update():
    envoy.run('supervisorctl reread')
    envoy.run('supervisorctl update')


def start(identifier):
    r = envoy.run('supervisorctl start ' + str(identifier))
    return {
        'std_out': r.std_out,
        'std_err': r.std_err
    }


def run(identifier, command, directory, **kwargs):
    change_config(identifier, command, directory, **kwargs)
    update()
    return start(identifier)


def terminate(identifier):
    stop(identifier)
    terminate_subprocess(identifier)


def stop(identifier):
    pid = get_pid(identifier)
    envoy.run('supervisorctl stop ' + str(identifier))
    if pid:
        envoy.run('kill -9 ' + str(pid))


def kill_process_in_port(port):
    protocols = ['tcp', 'udp']
    for prot in protocols:
        r = envoy.run('fuser %s/%s' % (str(port), prot)).std_out
        if r:
            pid = r[r.rfind(' ')+1:]
            envoy.run('kill -9 ' + pid)


def status():
    pass
