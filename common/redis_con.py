#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis as _redis
import jsonpickle
import logengine

POOL = None


def redis():
    return _redis.StrictRedis(connection_pool=POOL)


def redis_connect(redis_url='', redis_password='', redis_db=0):
    global POOL

    args = {
        'host': redis_url,
        'port': 6379,
        'db': redis_db,
        'password': redis_password
    }

    POOL = _redis.ConnectionPool(**args)
    if not redis().ping():
        logengine.connection_to_redis_failed(append='{host} {port} {db} {password}'.format(**args))
        raise Exception('Invalid Redis connection')
    logengine.connection_to_redis_successful_inspection(
        redis_address={'host': redis_url, 'port': 6379, 'db': redis_db},
        append='{host} {port} {db} {password}'.format(**args)
    )


def redis_save(key, value):
    p = jsonpickle.encode(value)
    redis().set(key, p)
    #logger.info(p)


def redis_load(key):
    serialized_obj = redis().get(key)
    if serialized_obj is None:
        return None
    return jsonpickle.decode(serialized_obj)


def redis_del(key):
    redis().delete(key)


def redis_list_append(list_name, value):
    v = jsonpickle.encode(value)
    redis().rpush(list_name, v)


def redis_list(list_name):
    lst = redis().lrange(list_name, 0, -1)
    if lst is None:
        return None
    return [jsonpickle.decode(v) for v in lst]


def redis_list_remove(list_name, value):
    v = jsonpickle.encode(value)
    redis().lrem(list_name, 0, v)


def redis_list_clear(list_name):
    redis_del(list_name)


def redis_set_timeout(key, secs_timeout):
    redis().expire(key, secs_timeout)


def redis_clear():
    redis().flushdb()
    redis().flushall()


def redis_set(key, value):
    redis().set(key, value)


def redis_get(key):
    return redis().get(key)


def redis_incr(key):
    return redis().incr(key)


def redis_queue_push(key, value):
    redis().rpush(key, value)


def redis_queue_pop(key):
    redis().lpop(key)


def delete(key):
    redis().delete(key)


def reset_flag(key):
    redis().set(key, 0)


def take_flag(key):
    cmd = "if redis.call('get', '%s') == '1' then return 0 end redis.call('set', '%s', 1) return 1" % (key, key)
    return redis().eval(cmd, 0) == 1


def redis_ping():
    try:
        if redis().ping():
            return True
    except:
        return False

"""
r.set(key, jsonpickle.encode(value))
return jsonpickle.decode(serialized_obj)
r.set(key, pickle.dumps(value))
return pickle.loads(serialized_obj)
"""