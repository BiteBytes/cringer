#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
from cringer import config
from common.core_communication import send_to_core
from common.constants import CORE_UPLOAD_VIDEO_FINISHED
import time
from common import logengine


THREADS = []


def clean_threads():
    global THREADS
    t_threads = []
    for t in THREADS:
        if t.is_alive():
            t_threads.append(t)
    THREADS = t_threads


def after_upload(_file, target, match_id):
    import os
    send_to_core({
        'file': target,
        'match_id': match_id
    }, CORE_UPLOAD_VIDEO_FINISHED)
    os.remove(_file)
    logengine.file_removed_from_disk(file=_file)


def _upload_using_s3(fle, target):
    from boto.s3.connection import S3Connection
    f = open(fle, 'rb')
    conn = S3Connection(config.S3_ACCESS_KEY, config.S3_SECRET_KEY)
    bucket = conn.get_bucket(config.S3_BUCKET)
    key = bucket.new_key(target)
    logengine.file_prepared_to_send_to_amazon(file=fle)
    key.set_contents_from_file(f)
    key.set_acl('public-read')


def _wait_before_upload():
    time.sleep(10)


def _upload_file(fle, target, match_id):
    _wait_before_upload()
    _upload_using_s3(fle, target)
    logengine.file_sent_to_amazon(file=fle, target=target)
    after_upload(fle, target, match_id)


def upload_file(fle, target, match_id):
    global THREADS
    clean_threads()
    t = threading.Thread(target=_upload_file, args=(fle, target, match_id))
    t.start()
    THREADS.append(t)