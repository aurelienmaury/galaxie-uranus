#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: Jérôme ORNECH alias "Tuux" <tuxa@rtnp.org> all rights reserved
__author__ = 'Tuux'

import curses


class clickable_sort_by_text():
    def __init__(self, window, Y, X, label, color):
        self.Parent = window
        self.YParent, self.XParent = window.getbegyx()
        self.Y = Y
        self.X = X
        self.label = str(label)
        self.Width = len(str(label))
        self.color = color
        self.Parent.addstr(self.Y, self.X, self.label, self.color)

    def mouse_clicked(self, MouseEvent):
        (id, x, y, z, event) = MouseEvent
        if (self.YParent - 1 <= y <= self.YParent + 1) and (
                            self.X + self.XParent <= x < self.X + self.XParent + self.Width):
            return 1
        else:
            return 0
