#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SourceLib import SourceRcon


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Start a server')

    parser.add_argument('-s', help='Server IP', dest='ip', required=True)
    parser.add_argument('-sp', help='Server port', dest='port', type=int, default=27500)
    parser.add_argument('-n', dest='num', type=int, default=1)

    args = parser.parse_args()
    right_v = 0

    for n in xrange(args.num):
        print 'Port', args.port + n
        try:
            rcon = SourceRcon.SourceRcon(args.ip, args.port + n, 'nocr1p')
            print rcon.rcon('status')
            right_v += 1
        except Exception:
            print 'error'

    print '================'
    print 'Right servers:', right_v
    print 'Wrong servers:', args.num - right_v
