#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SourceLib import SourceRcon


threads = []


def enable_tv(_rcon, *_):
    cmds = ['mp_spectators_max 0',
        'tv_delaymapchange 1',
        'tv_enable 1',
        'tv_delay 120',
        'tv_snapshotrate 32',
        'tv_name "BeSports GOTV"',
        'tv_title "BeSports GOTV"',
        'tv_maxclients 64',
        'tv_timeout 20',
        'tv_transmitall 1']
    for cmd in cmds:
        print _rcon.rcon(cmd)
    return




    print _rcon.rcon('tv_advertise_watchable 1')
    print _rcon.rcon('tv_deltacache 2')
    print _rcon.rcon('tv_delay 3')
    # print rcon.rcon('tv_password "tv"')
    print _rcon.rcon('tv_port ' + str(args.port + 1000))
    print _rcon.rcon('tv_enable 1')
    print _rcon.rcon('mp_spectators_max 10')
    print _rcon.rcon('tv_delaymapchange 1')
    print _rcon.rcon('tv_snapshotrate 32')
    print _rcon.rcon('tv_name "BeSports GOTV"')
    print _rcon.rcon('tv_title "BeSports GOTV"')
    print _rcon.rcon('tv_maxclients 64')
    print _rcon.rcon('tv_timeout 20')
    print _rcon.rcon('tv_transmitall 1')


def vote(_rcon, *_):
    print _rcon.rcon('es_vote "Esto es una prueba" "CT" "T"')


def fire(*_):
    from threading import Thread
    import traceback
    import time

    def _fire():
        n = 0
        while True:
            _rcon = SourceRcon.SourceRcon(args.ip, args.port, 'nocr1p')
            try:
                n += 1
                print _rcon.rcon('radar_enable 0')
                time.sleep(0)
            except Exception as e:
                print 'Failed at', n
                traceback.print_exc()
                break

    for _ in xrange(15):
        t = Thread(target=_fire)
        threads.append(t)
        t.start()

    for t in threads:
        print t.name, t.is_alive()


def allow(_rcon, _, line):
    ids = {
        'alfred': 'STEAM_1:1:57161168',
        'jordi': 'STEAM_1:0:149688811',
        'mike': 'STEAM_1:0:90194590'
    }
    values = line.split()
    name = ids.get(values[1], values[1])
    print _rcon.rcon('sm_whitelist_add "{}"'.format(name))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Start a server')

    parser.add_argument('-s', help='Server IP', dest='ip', required=True)
    parser.add_argument('-sp', help='Server port', dest='port', type=int, default=27500)

    args = parser.parse_args()
    right_v = 0

    commands = {
        'enable_tv': enable_tv,
        'vote': vote,
        'fire': fire,
        'allow': allow
    }

    while True:
        try:
            rcon = SourceRcon.SourceRcon(args.ip, args.port, 'nocr1p')
            cmd = raw_input('rcon > ')
            c1 = cmd.split()[0]
            if cmd in commands.keys():
                commands[cmd](rcon, args, cmd)
            elif c1 in commands.keys():
                commands[c1](rcon, args, cmd)
            else:
                print rcon.rcon(cmd)
            right_v += 1
        except Exception as e:
            print 'error', e
