#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cringer import config as cconfig
from flask.ext.testing import LiveServerTestCase
from hamcrest import assert_that, equal_to, is_not
from multiprocessing import Queue
import requests
from urlparse import urljoin
import jsonpickle
import os
import shutil
import time

TEST_GAME_NAME = 'test_game'


class TestS3(LiveServerTestCase):
    def __init__(self, methodname):
        LiveServerTestCase.__init__(self, methodName=methodname)
        self.queue = Queue()
        self.file_to_clean = None

    def setUp(self):
        _config = os.environ.get('CRINGERCONF', None)
        assert _config is not None and 'test' in _config
        self.create_structure()
        self.addCleanup(self.clean_dirs)
        self.addCleanup(self.clean_s3)
        self.messages = {}

    def clean_s3(self):
        if self.file_to_clean is not None:
            from boto.s3.connection import S3Connection, Bucket, Key
            conn = S3Connection(cconfig.S3_ACCESS_KEY, cconfig.S3_SECRET_KEY)
            bucket = conn.get_bucket(cconfig.S3_BUCKET)
            k = Key(bucket)
            k.key = self.file_to_clean[1:]
            bucket.delete_key(k)

    def create_structure(self):
        self.clean_dirs()
        os.mkdir(cconfig.CSGO_PATH)
        csgo_path = os.path.join(cconfig.CSGO_PATH, 'csgo')
        os.mkdir(csgo_path)
        self.dem_file = os.path.join(csgo_path, 'things-' + TEST_GAME_NAME + '.dem')
        f = file(self.dem_file, 'w')
        f.write('test')
        f.close()

    def clean_dirs(self):
        if os.path.exists(cconfig.CSGO_PATH):
            shutil.rmtree(cconfig.CSGO_PATH)

    def send_to_core_patcher(self, message, _):
        self.queue.put(('core_msg', message))

    def monkey_patches(self):
        import common.core_communication as core
        cconfig.CSGO_PATH = os.path.join(os.path.dirname(__file__), 'tmp')
        core.send_to_core = self.send_to_core_patcher

    def create_app(self):
        self.monkey_patches()
        from ws.ws import app as app
        app.config['TESTING'] = True
        return app

    def get_core_message(self):
        while 'core_msg' not in self.messages.keys():
            msg = self.queue.get(block=True, timeout=5)
            self.messages[msg[0]] = msg[1]

    def exist_in_s3(self, fle):
        from boto.s3.connection import S3Connection
        conn = S3Connection(cconfig.S3_ACCESS_KEY, cconfig.S3_SECRET_KEY)
        bucket = conn.get_bucket(cconfig.S3_BUCKET)
        prfx = cconfig.VIDEOS_PREFIX[1:]
        rs = [k.name for k in bucket.list(prefix=prfx)]
        fname = fle[1:]
        return fname in rs

    def test_s3_config(self):
        parameters = {
            'game_type': 'csgo',
            'game_name': TEST_GAME_NAME
        }
        url = urljoin(self.get_server_url(), 'upload_demofile')
        response = requests.post(url, data=parameters)
        content = jsonpickle.decode(response.content)
        assert_that(response.status_code, equal_to(200))
        assert_that(content['result'], equal_to('ok'))
        self.get_core_message()
        assert_that(os.path.exists(self.dem_file), is_not(True))
        core_msg = self.messages['core_msg']
        cmsg = jsonpickle.decode(core_msg)
        assert_that(self.exist_in_s3(cmsg['file']), equal_to(True))
        self.file_to_clean = cmsg['file']
