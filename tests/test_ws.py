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


class TestWebServices(LiveServerTestCase):
    def __init__(self, methodname):
        LiveServerTestCase.__init__(self, methodName=methodname)
        self.queue = Queue()

    def setUp(self):
        _config = os.environ.get('CRINGERCONF', None)
        assert _config is not None and 'test' in _config
        self.create_structure()
        self.addCleanup(self.clean_dirs)
        self.messages = {}

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

    def s3_patcher(self, _file, target):
        self.queue.put(('uploaded_file', _file))
        self.queue.put(('uploaded_to', target))

    def send_to_core_patcher(self, message, _):
        self.queue.put(('core_msg', message))

    def other_functions(self, *args, **kwargs):
        pass

    def monkey_patches(self):
        import ws.amazon as amazon
        import common.core_communication
        cconfig.CSGO_PATH = os.path.join(os.path.dirname(__file__), 'tmp')
        amazon.send_to_core = self.send_to_core_patcher
        amazon._upload_using_s3 = self.s3_patcher
        amazon._wait_before_upload = self.other_functions
        common.core_communication.send_to_core = self.send_to_core_patcher

    def create_app(self):
        self.monkey_patches()
        from ws.ws import app as app
        app.config['TESTING'] = True
        return app

    def get_messages(self):
        while not self.queue.empty():
            msg = self.queue.get()
            self.messages[msg[0]] = msg[1]

    def test_upload_file(self):
        parameters = {
            'game_type': 'csgo',
            'game_name': TEST_GAME_NAME
        }
        url = urljoin(self.get_server_url(), 'upload_demofile')
        response = requests.post(url, data=parameters)
        content = jsonpickle.decode(response.content)
        assert_that(response.status_code, equal_to(200))
        assert_that(content['result'], equal_to('ok'))
        time.sleep(2)
        assert_that(os.path.exists(self.dem_file), is_not(True))
        self.get_messages()
        core_msg = self.messages['core_msg']
        uploaded_file = self.messages['uploaded_file']
        assert_that(core_msg['file'], equal_to(cconfig.VIDEOS_PREFIX + TEST_GAME_NAME + '.dem'))
        assert_that(core_msg['match_id'], equal_to(TEST_GAME_NAME))
        assert_that(uploaded_file, equal_to(self.dem_file))

    def test_delete_file(self):
        parameters = {
            'game_type': 'csgo',
            'game_name': TEST_GAME_NAME
        }
        url = urljoin(self.get_server_url(), 'delete_demofile')
        response = requests.post(url, data=parameters)
        content = jsonpickle.decode(response.content)
        assert_that(response.status_code, equal_to(200))
        assert_that(content['result'], equal_to('ok'))
        time.sleep(1)
        self.get_messages()
        assert_that(os.path.exists(self.dem_file), is_not(True))
        assert_that(len(self.messages), equal_to(0))

    def test_update_error(self):
        parameters = {
            'game_type': 'csgo'
        }
        url = urljoin(self.get_server_url(), 'update')
        response = requests.post(url, data=parameters)
        content = jsonpickle.decode(response.content)
        assert_that(response.status_code, equal_to(200))
        assert_that(content['result'], equal_to('ok'))
        time.sleep(1)
        self.get_messages()
        assert_that(len(self.messages), equal_to(1))
        assert_that(self.messages['core_msg']['result'], 'ERROR')