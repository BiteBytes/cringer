#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from multiprocessing import Process
import datetime
from cringer import config
import logengine

gmodes = {
    'dm': '+game_type 1 +game_mode 2',
    'gm': '+game_type 1 +game_mode 0',
    'csgo': '+game_type 0 +game_mode 1'
}

PROCESSES = []


def start_maintenance():
    f = open('./maintenance', 'w')
    f.close()


def stop_maintenance():
    import os
    os.remove('./maintenance')


def config_path():
    return os.path.join(config.CSGO_PATH, 'csgo', 'cfg')


def start_command(**kwargs):
    from cringer import config

    _map = kwargs.get('map', None)
    _mode = kwargs.get('mode', 'classic')
    _port = kwargs['port']
    _ip = kwargs['ip']
    _confile = kwargs['config_file']
    _csgo_path = config.CSGO_PATH
    _system = kwargs['system']
    _token = kwargs['token']
    _match = kwargs['match']

    params = {
        'mode': gmodes.get(_mode, '+game_type 0 +game_mode 1'),
        'map': '+map ' + _map if _map else '',
        'port': _port,
        'ip': _ip,
        'config_file': _confile,
        'exec_cmd': os.path.join(_csgo_path, 'srcds_run'),
        'tvport': int(_port) + 1000,
        'broker': config.broker_url.replace('amqp://', '').replace('//', ''),
        'runner_cmd': os.path.join(config.UTILS_PATH, 'runner.sh'),
        'gslt_token': _token,
        'match': _match,
        'redis_url': config.REDIS_URL,
        'redis_password': config.REDIS_PASSWORD
    }
    exec_str = 'bash {runner_cmd} {port} {ip} {broker} {match} {redis_url} {redis_password} {exec_cmd} -console -usercon -port {port} -game csgo {mode} +mapgroup mg_active {map}  +tv_port {tvport} -maxplayers_override 32 +exec {config_file} +sv_pure 2 -tickrate 128 +host_workshop_collection  +workshop_start_map -authkey E17DEB80BABE5F83BF1C1A797F24A554 +sv_setsteamaccount {gslt_token} -net_port_try 1 -ip {ip}'
    cmd = exec_str.format(**params), config.CSGO_PATH
    return cmd


def notify_end_update(ip, start_time='', finish_time='', result='OK', **kwargs):
    from common import core_communication
    from common import constants

    message = {
        'server': ip,
        'start': start_time,
        'finish': finish_time,
        'result': result,
        'gtype': constants.CSGO,
        'errors': kwargs.get('errors', '')
    }
    core_communication.send_to_core(message, constants.CORE_UPDATE_FINISHED)


def run_update(command, ip):
    try:
        logengine.update_started()
        stime = str(datetime.datetime.utcnow())
        errors = None

        try:
            _restore(
                do_download_plugins=False,
                do_replace_configs=False,
                do_remove_maps=True,
                do_restore=True,
                do_upload_official_maps=True,
                do_sync_official_maps=True,
                do_download_es_maps=True,
                do_sync_public_maps=True
            )
        except Exception as e:
            errors = str(e)
            logengine.logging.error('Update went wrong - ' + str(e))

        etime = str(datetime.datetime.utcnow())
        notify_end_update(
            ip,
            start_time=stime,
            finish_time=etime,
            result='OK' if not errors else 'ERROR',
            errors=errors
        )
        logengine.update_ended()
    except Exception as e:
        notify_end_update(
            ip,
            start_time=stime,
            result='ERROR',
            errors='Exception error: ' + str(e),
            append=str(e)
        )
        logengine.update_failed()


def replace_configs():
    import os
    import shutil
    import cringer

    conf_path = config_path()

    fpath = os.path.realpath(cringer.__file__)
    files_path = os.path.join(os.path.dirname(fpath), 'cs_configs')
    files_path = os.path.join(files_path, 'csgo')
    files = os.listdir(files_path)

    for _file in files:
        _file = os.path.join(files_path, _file)
        fname = os.path.basename(_file)
        dest = os.path.join(conf_path, fname)
        shutil.copy(_file, dest)

    logengine.config_files_replaced()


def update_command():
    params = {
        'steam_cmd': os.path.join(config.STEAM_PATH, 'steamcmd.sh'),
        'csgo_path': config.CSGO_PATH
    }
    s = '{steam_cmd} +login anonymous +force_install_dir {csgo_path} +app_update 740 validate +quit'
    return s.format(**params)


def update(**kwargs):
    _cmd = update_command()
    _ip = kwargs['ip']
    p = Process(target=run_update, args=(_cmd, _ip,))
    p.start()
    PROCESSES.append(p)


def file_to_upload(**kwargs):
    _csgo_path = config.CSGO_PATH
    _game_name = kwargs['game_name']
    basepath = os.path.join(_csgo_path, 'csgo')
    files = [os.path.join(basepath, f) for f in os.listdir(basepath) if f.endswith(_game_name + '.dem')]
    if len(files) > 1:
        raise Exception('There is at least another file that matches with the pattern')
    elif len(files) == 0:
        raise Exception('There is no file that matches with the pattern')
    return files[0]


def download_plugins():
    import requests
    import envoy
    import os
    from common.html_parser import TagFinder

    logengine.looking_for_sourcemod()
    r = requests.get('http://www.sourcemod.net/downloads.php?branch=stable')
    if r.status_code == 200:
        logengine.sourcemod_found()
    else:
        logengine.sourcemod_not_found_error()
        return

    parser = TagFinder(_class=u'quick-download')
    parser.feed(r.text)
    linux_results = [r[1]['href'] for r in parser.tags if r[0] == 'a' and 'linux' in r[1]['href']]
    assert len(linux_results) == 1
    script = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/../resources/installmods.sh')
    executable = 'sh {script} {url}'.format(
        **{
            'script': script,
            'url': linux_results[0]
        }
    )

    logengine.update_files_started()
    r = envoy.run(executable)

    log_function = logengine.update_files_ended if r.status_code == 0 else logengine.update_files_ended_with_error
    log_function(std_out=r.std_out, std_error=r.std_err)


def delete_official_maps():
    import os
    file_patterns = ['*assault*', '*aztec*', '*baggage*', '*bank*', '*cbble*', '*dust*', '*inferno*', '*italy*',
                     '*lake*', '*militia*', '*monastery*', '*nuke*', '*office*', '*overpass*', '*safehouse*',
                     '*shoots*', '*shorttrain*', '*marc*', '*train*', '*vertigo*']
    maps_folder = os.path.join(config.CSGO_PATH, 'csgo/maps')
    for f in file_patterns:
        command = 'cd %s; rm %s' % (maps_folder, f)
        result = os.system(command)
        if result == 0:
            logengine.map_deleted(command=command)
        else:
            logengine.map_delete_error(command=command, result=result)


def restore_install_dir():
    import envoy
    logengine.csgo_restore_files_started()
    upd_command = update_command()
    r = envoy.run(upd_command)
    if r.status_code == 0:
        logengine.csgo_finish_restoring(std_out=r.std_out, std_error=r.std_err)
    else:
        logengine.csgo_restore_error(std_out=r.std_out, std_error=r.std_err)
        raise Exception(r.std_err)


def transfer_maps(from_path, to_path, copy=False, make_public=False, is_recursive=True, add_region=True):
    import os
    import envoy

    verb = 'cp' if copy else 'sync'
    base = "aws s3 " + verb + " %s %s"
    command = base % (from_path, to_path)
    if add_region:
        command += " --region eu-west-1"
    if copy and is_recursive:
        command += " --recursive"
    if make_public:
        command += " --acl public-read"

    os.environ['AWS_ACCESS_KEY_ID'] = config.S3_ACCESS_KEY
    os.environ['AWS_SECRET_ACCESS_KEY'] = config.S3_SECRET_KEY

    r = envoy.run(command)
    logengine.logging.info(command)
    if r.status_code == 0:
        logengine.custom_csgo_maps_obtained(command=command, std_out=r.std_out, std_error=r.std_err)
    else:
        logengine.custom_csgo_maps_obtained_error(command=command, std_out=r.std_out, std_error=r.std_err,
                                                  append=r.std_err)


def sync_new_maps(multithread=False):
    def _sync_new_maps():
        logengine.logging.info('Sync maps')
        csgo_maps_path = os.path.join(config.CSGO_PATH, 'csgo/maps/')
        transfer_maps(config.S3_BUCKET_PREFIX_CSGO_PUBLIC_MAPS, csgo_maps_path)
    if multithread:
        from multiprocessing import Process
        p = Process(target=_sync_new_maps)
        p.start()
        PROCESSES.append(p)
    else:
        _sync_new_maps()


def get_electronic_maps():
    """
    Get maps which have been updated into DB
    """
    logengine.logging.info('Get ES Maps')
    csgo_maps_path = os.path.join(config.CSGO_PATH, 'csgo/maps')
    transfer_maps(config.S3_BUCKET_PREFIX_CSGO_ES_MAPS, csgo_maps_path, copy=True)


def upload_official_maps():
    logengine.logging.info('Upload official maps')
    csgo_maps_path = os.path.join(config.CSGO_PATH, 'csgo/maps')
    transfer_maps(csgo_maps_path, config.S3_BUCKET_PREFIX_CSGO_OFFICIAL_MAPS, copy=True)


def sync_official_maps():
    logengine.logging.info('Sync official maps')
    csgo_maps_path = os.path.join(config.CSGO_PATH, 'csgo/maps')
    transfer_maps(config.S3_BUCKET_PREFIX_CSGO_OFFICIAL_MAPS, csgo_maps_path)


def publish_maps():
    """
    Publish all the maps into S3
    """
    logengine.logging.info('Publishing maps')
    csgo_maps_path = os.path.join(config.CSGO_PATH, 'csgo/maps')
    transfer_maps(csgo_maps_path, config.S3_BUCKET_PREFIX_CSGO_PUBLIC_MAPS, make_public=True)


def remove_local_maps():
    import shutil
    logengine.logging.info('Removing local maps')
    csgo_maps_path = os.path.join(config.CSGO_PATH, 'csgo/maps')
    shutil.rmtree(csgo_maps_path)


def _restore(
        do_download_plugins=True,
        do_replace_configs=True,
        do_remove_maps=True,
        do_restore=True,
        do_upload_official_maps=True,
        do_sync_official_maps=True,
        do_download_es_maps=True,
        do_sync_public_maps=True):
    start_maintenance()

    if do_download_plugins:
        download_plugins()
    if do_replace_configs:
        replace_configs()
    if do_remove_maps:          # Maps routine:
        remove_local_maps()     # - remove local maps folder
    if do_restore:
        restore_install_dir()   # - update and restore all files
    if do_upload_official_maps:
        upload_official_maps()  # - upload new official maps overriding deprecated ones and leaving old ones
    if do_sync_official_maps:
        sync_official_maps()    # - sync the old and the new official maps
    if do_download_es_maps:
        get_electronic_maps()   # - download non official maps
    if do_sync_public_maps:
        publish_maps()          # - sync the public folder

    stop_maintenance()


def restore():
    from multiprocessing import Process
    p = Process(target=_restore)
    p.start()
    PROCESSES.append(p)
