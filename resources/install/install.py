#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import env, run, sudo, cd, put, get
from fabric.contrib.files import exists, append
import json

supervisor_config = """
; supervisor config file

[unix_http_server]
file=/tmp/supervisor.sock   ; (the path to the socket file)
chmod=0777                       ; sockef file mode (default 0700)

[supervisord]
logfile=/var/log/supervisor/supervisord.log ; (main log file;default $CWD/supervisord.log)
pidfile=/var/run/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
childlogdir=/var/log/supervisor            ; ('AUTO' child log dir, default $TEMP)

; the below section must remain in the config file for RPC
; (supervisorctl/web interface) to work, additional interfaces may be
; added by defining them in separate rpcinterface: sections
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///tmp/supervisor.sock ; use a unix:// URL  for a unix socket

; The [include] section can just contain the "files" setting.  This
; setting can list multiple files (separated by whitespace or
; newlines).  It can also contain wildcards.  The filenames are
; interpreted as relative to this file.  Included files *cannot*
; include files themselves.

[include]
files = /etc/supervisor/conf.d/*.conf
"""

supervisor_cringer_config = """
[program:cringer]
command=gunicorn -w 4 -b 0.0.0.0:8080 cringer_app:app
directory=/home/steam/cringer
autostart=true
autorestart=true
user=steam
environment=CRINGERCONF=config.%s
"""

nginx_config = """
server {
    listen 80;
    server_name %s;
    location / {
        proxy_pass http://127.0.0.1:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
"""

_execute = None
last_value = None


def append_log(text, path='/var/log/electronic/current'):
    append(path, text, _execute == sudo)


def execute(cmd, append_text=True):
    global last_value
    value = _execute(cmd)
    last_value = str(value)
    if append_text:
        append_log('$ ' + cmd)
        if not value.failed:
            append_log(value)
        else:
            append_log('[ERROR]: ' + value)
    return not value.failed


def exist_steam_user():
    return execute('id steam')


def exist_steam_dir():
    return exists('/home/steam')


def remove_steam_user():
    results = [
        execute('killall -u steam'),
        execute('userdel -r steam'),
        execute('rm -Rf /home/steam')
    ]
    return all(results)


def exist_supervisor_package():
    return execute('dpkg -l | grep supervisor')


def stop_supervisor():
    return execute('supervisorctl stop all')


def install_packages():
    results = [
        execute('apt-get update'),
        execute(
            'apt-get install -y lib32stdc++6 python-pip python-dev libevent-dev git supervisor nginx lib32gcc1 expect expect-dev'),
        execute('pip install --upgrade pip'),
        execute('pip install supervisor'),
        execute('pip install awscli'),
        execute('pip install requests'),
        execute('pip install gunicorn')
    ]
    return all(results)


def create_steam_user():
    return execute('groupadd steam && useradd --create-home --home-dir /home/steam -g steam steam')


def reboot_services():
    import time
    execute('rm /var/log/supervisor/*')
    execute('service supervisor restart')
    time.sleep(5)
    execute('supervisorctl reread')
    execute('supervisorctl update')
    print execute('service nginx restart')


def clone_cringer():
    with cd('/home/steam/'):
        put('cringer2', '/home/steam', use_sudo=_execute == sudo)
        execute('chmod 600 cringer2')
        execute('rm -Rf /home/steam/cringer')
        return execute('eval `ssh-agent -s`; ssh-add cringer2; git clone git@bitbucket.org:electronicstars/cringer.git')


def configure_cringer(branch):
    with cd('/home/steam/cringer'):
        results = [
            execute('git checkout ' + branch),
            execute('pip install -r requirements.txt'),
            execute('chown -R steam:steam /home/steam/cringer'),
            execute('chmod +x /home/steam/cringer/runner.sh')
        ]
        return all(results)


def install_csgo():
    execute('mkdir /home/steam/steamcmd')
    with cd('/home/steam/steamcmd'):
        results = [
            execute('wget http://media.steampowered.com/client/steamcmd_linux.tar.gz'),
            execute('tar -xzf steamcmd_linux.tar.gz'),
            execute('./steamcmd.sh +login anonymous +force_install_dir ../csgo/ +app_update 740 validate +quit')
        ]
        return all(results)


def configure_csgo():
    results = [
        execute('cp /home/steam/cringer/cs_configs/csgo/gamemode_competitive_server.cfg /home/steam/csgo/csgo/cfg'),
        execute('cp /home/steam/cringer/cs_configs/csgo/gamemode_deathmatch_server.cfg /home/steam/csgo/csgo/cfg'),
        execute('cp /home/steam/cringer/cs_configs/csgo/server.cfg /home/steam/csgo/csgo/cfg'),
        execute('mkdir /home/steam/.steam'),
        execute('mkdir /home/steam/.steam/sdk32'),
        execute('cp -Rf /home/steam/csgo/bin/* /home/steam/.steam/sdk32')
    ]
    return all(results)


def configure_supervisor(cringer_conf):
    cringer_config = supervisor_cringer_config % (cringer_conf,)
    execute('rm /etc/supervisor/conf.d/*')
    execute('rm /etc/supervisor/supervisord.conf')
    append('/etc/supervisor/supervisord.conf', supervisor_config, use_sudo=_execute == sudo)
    append('/etc/supervisor/conf.d/cringer.conf', cringer_config, use_sudo=_execute == sudo)


def configure_nginx(host):
    execute('rm /etc/nginx/sites-enabled/default')
    execute('rm /etc/nginx/sites-available/default')
    nginx_conf = nginx_config % (host,)
    append('/etc/nginx/sites-available/default', nginx_conf, use_sudo=_execute == sudo)
    execute('ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/')


def fix_permissions():
    results = [
        execute('chown -R steam:steam /home/steam'),
        execute('chown -R steam:steam /etc/supervisor/conf.d')
    ]
    return all(results)


def restore_maps():
    return execute('wget http://127.0.0.1:80/restore')


def prepare_log_folder():
    execute('mkdir /var/log/electronic')


def prepare_log():
    import uuid
    execute('rm /var/log/electronic/current', append_text=False)
    name = str(uuid.uuid4()).replace('-', '') + '.txt'
    current_log = '/var/log/electronic/' + name
    append_log('', path=current_log)
    execute('ln -s %s /var/log/electronic/current' % current_log, append_text=False)
    return name


def read_index():
    success = execute('cat /var/log/electronic/index.json', append_text=False)
    if not success:
        return {'index': []}
    return json.loads(str(last_value))


def write_index(jindex):
    execute('rm /var/log/electronic/index.json', append_text=False)
    append('/var/log/electronic/index.json', jindex, use_sudo=_execute == sudo)


def append_index(record):
    index = read_index()
    index['index'].append(record)
    index['installing'] = False
    jindex = json.dumps(index)
    write_index(jindex)


def start_installing():
    index = read_index()
    index['installing'] = True
    jindex = json.dumps(index)
    write_index(jindex)


def install(host, username, password, branch='develop', pem=False, cringer_config='test', ssh_port=22):
    global _execute
    env.host_string = "%s:%s" % (host, ssh_port)
    env.user = username
    if pem:
        env.key_filename = password
    else:
        env.password = password
    env.warn_only = True
    _execute = run if username == 'root' else sudo

    prepare_log_folder()
    start_installing()
    name = prepare_log()

    try:
        stop_supervisor()
        remove_steam_user()
        assert install_packages(), 'Problems when installing packages'
        assert create_steam_user(), 'User steam could not be created'
        assert clone_cringer(), 'Cringer was not cloned'
        assert configure_cringer(branch), 'Problems when configuring Cringer'

        assert install_csgo(), 'CSGO was not installed'
        assert configure_csgo(), 'CSGO was not properly configured'

        configure_supervisor(cringer_conf=cringer_config)
        configure_nginx(host)
        assert fix_permissions(), 'Problems when assigning permissions'

        reboot_services()
        assert restore_maps(), 'Problems restoring maps'

        append_log('>>> INSTALL FINISHED AND IT SEEMS SUCCESSFUL!! ヽ༼ຈل͜ຈ༽ﾉ ')
        status = 'ok'
        message = 'Properly finished'
    except Exception as exc:
        status = 'error'
        message = str(exc)

    index_obj = {
        'name': name,
        'status': status,
        'message': message
    }
    append_index(index_obj)


def get_log(host, username, password, ssh_port=22, pem=False, log_file='current'):
    import io
    global _execute
    env.host_string = "%s:%s" % (host, ssh_port)
    env.user = username
    if pem:
        env.key_filename = password
    else:
        env.password = password
    env.warn_only = True
    try:
        a = get('/var/log/electronic/' + log_file, use_sudo=username != 'root')
        with io.open(a[0], mode="r", encoding="utf-8") as f:
            return f.read()
    except:
        return ''


# install('185.154.160.67', 'electronicastars', 'Electronic1212--')
# install('147.135.136.36', 'root', 'UcC5h1zQikD9', ssh_port=77)
install('52.67.8.141', 'ubuntu', 'D:/Projectos/Electronicstars/recursos/pem keys/electronicstars-brasil.pem',
        pem=True, ssh_port=22, cringer_config='prod')


# print get_log('151.80.110.37', 'root', 'g6TkHUD6DD9w', ssh_port=77, log_file='6c03dc14a6054d56a9610c0f12b7dd9d.txt')
