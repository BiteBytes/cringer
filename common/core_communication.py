#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cringer import config
from celery import Celery
import logengine

app = Celery('cringer')
app.config_from_object('cringer.config')


def send_to_core(message, task_name):
    app.send_task(
        task_name,
        (message,),
        exchange=config.CORE_QUEUE,
        queue=config.CORE_QUEUE,
    )
    logengine.sent_to_core(task_name=task_name, _msg=message)

