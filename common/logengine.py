#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import inspect
import traceback

"""
DEBUG:  (inspection) For logging details
INFO:   For logging expected events
WARN:   (alert) For logging expected events on the system that should not happen
ERROR:  (error) For logging unexpected events which can lead to unexpected behaviour, but system will continue working
CRITIC: (failure) For logging unexpected events that should never happen
"""


def log(values):
    func_name = inspect.currentframe().f_back.f_code.co_name
    message = func_name.replace('_', ' ').title()
    value = values  # jsonpickle.encode(values)

    append_text = ''
    if 'append' in value.keys():
        append_text = ' - ' + value['append']
        del value['append']

    loglevel = None

    if 'loglevel' in value.keys():
        loglevel = value['loglevel']
        del value['loglevel']

    assert 'message' not in value.keys()
    assert 'name' not in value.keys()
    assert 'msg' not in value.keys()

    if message.endswith('Inspection') or message.endswith('Called') or loglevel == 'DEBUG':
        value['numeric_loglevel'] = 0
        logging.debug(message + append_text, extra=value)
    elif message.endswith('Alert') or loglevel == 'WARNING':
        value['numeric_loglevel'] = 2
        logging.warning(message + append_text, extra=value)
    elif message.endswith('Error') or loglevel == 'ERROR':
        value['numeric_loglevel'] = 3
        value['traceback'] = traceback.format_exc()
        logging.error(message + append_text, extra=value)
    elif message.endswith('Failure') or message.endswith('Failed') or loglevel == 'CRITICAL':
        value['numeric_loglevel'] = 4
        value['traceback'] = traceback.format_exc()
        logging.critical(message + append_text, extra=value)
    else:
        value['numeric_loglevel'] = 1
        logging.info(message + append_text, extra=values)


def connection_to_redis_successful_inspection(**kwargs):
    log(kwargs)


def connection_to_redis_failed(**kwargs):
    log(kwargs)


def carrot_started(**kwargs):
    log(kwargs)


def carrot_logline_received_inspection(**kwargs):
    log(kwargs)


def carrot_logline_sended(**kwargs):
    log(kwargs)


def sent_to_core(**kwargs):
    log(kwargs)


def file_sent_to_amazon(**kwargs):
    log(kwargs)


def file_removed_from_disk(**kwargs):
    log(kwargs)


def file_prepared_to_send_to_amazon(**kwargs):
    log(kwargs)


def preparing_to_send_to_amazon(**kwargs):
    log(kwargs)


def update_started(**kwargs):
    log(kwargs)


def update_ended(**kwargs):
    log(kwargs)


def update_failed(**kwargs):
    log(kwargs)


def request_received(**kwargs):
    log(kwargs)


def something_failed(**kwargs):
    log(kwargs)


def response_sended(**kwargs):
    log(kwargs)


def starting_server(**kwargs):
    log(kwargs)


def map_deleted(**kwargs):
    log(kwargs)


def map_delete_error(**kwargs):
    log(kwargs)


def csgo_restore_files_started(**kwargs):
    log(kwargs)


def csgo_finish_restoring(**kwargs):
    log(kwargs)


def csgo_restore_error(**kwargs):
    log(kwargs)


def looking_for_sourcemod(**kwargs):
    log(kwargs)


def sourcemod_found(**kwargs):
    log(kwargs)


def sourcemod_not_found_error(**kwargs):
    log(kwargs)


def config_files_replaced(**kwargs):
    log(kwargs)


def update_files_started(**kwargs):
    log(kwargs)


def update_files_ended(**kwargs):
    log(kwargs)


def update_files_ended_with_error(**kwargs):
    log(kwargs)


def obtaining_csgo_maps_from_s3(**kwargs):
    log(kwargs)


def custom_csgo_maps_obtained(**kwargs):
    log(kwargs)


def custom_csgo_maps_obtained_error(**kwargs):
    log(kwargs)


def check_redis_error(**kwargs):
    log(kwargs)


def check_celery_error(**kwargs):
    log(kwargs)


def check_system_error(**kwargs):
    log(kwargs)