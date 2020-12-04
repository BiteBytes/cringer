#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


def generate_random_string(size=6):
    import random
    import string
    return ''.join(random.choice(string.letters) for _ in xrange(size))


def get_new_file(path, mode='w', size=6, prefix='', sufix=''):
    exists = True
    tpath = ''
    while exists:
        fname = prefix + generate_random_string(size) + sufix
        tpath = os.path.join(path, fname)
        exists = os.path.exists(tpath)
    return open(tpath, mode)


def prepare_path(path, fname=None):
    if not os.path.exists(path):
        os.makedirs(path)
    if fname:
        return os.path.join(path, fname)
    return path


def write_file(fpath, content, mode='w'):
    with open(fpath, mode) as f:
        f.write(content)
