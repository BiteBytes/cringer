#!/usr/bin/env python
# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser


class TagFinder(HTMLParser):
    def __init__(self, _id=None, _class=None):
        HTMLParser.__init__(self)
        self.tagId = _id
        self.className = _class
        self.tags = []

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if self.tagId is not None and attr[0] == u'id' and attr[1] == self.tagId:
                self.tags.append((tag, {at[0]: at[1] for at in attrs}))
            if self.className is not None and attr[0] == u'class' and self.className in attr[1]:
                self.tags.append((tag, {at[0]: at[1] for at in attrs}))


"""
r = requests.get('http://www.sourcemod.net/downloads.php?branch=stable')
assert r.status_code == 200
parser = TagFinder(_class=u'quick-download')
parser.feed(r.text)
linux_results = [r[1]['href'] for r in parser.tags if r[0] == 'a' and 'linux' in r[1]['href']]
assert len(linux_results) == 1
print linux_results[0]
"""
