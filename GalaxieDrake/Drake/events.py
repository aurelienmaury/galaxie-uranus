#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: Jérôme ORNECH alias "Tuux" <tuxa@rtnp.org> all rights reserved
__author__ = 'Tuux'

import collections


class Event:
    def __init__(self, value):
        self.value = value


class EventQueue:
    def __init__(self):
        self.internal_queue = collections.deque()

    def pop(self):
        return self.internal_queue.popleft()

    def push(self, event):
        self.internal_queue.append(event)

    def has_events(self):
        return len(self.internal_queue) != 0