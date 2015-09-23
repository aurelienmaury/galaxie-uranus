#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: Jérôme ORNECH alias "Tuux" <tuxa@rtnp.org> all rights reserved
__author__ = 'Tuux'

import curses

__author__ = 'tuxa'


class CursesButton(object):

    def __init__(self, window, Y, X, Label, Hotkey=0):
        self.Parent = window
        self.YParent, self.XParent = window.getbegyx()
        self.Y = Y
        self.X = X
        self.LabelButton = "[ " + Label + " ]"
        self.Label = Label
        self.Width = len(self.LabelButton) + 2
        self.Underline = 2
        self.Selected = 0
        window.refresh()

    def select(self):
        self.Parent.addstr(
            self.Y + 1,
            self.X + 1,
            self.LabelButton,
            curses.color_pair(1)
        )
        self.Parent.addstr(
            self.Y + 1,
            self.X + self.Underline + 1,
            self.LabelButton[self.Underline],
            curses.A_REVERSE | curses.color_pair(3)
        )
        self.Parent.move(
            self.Y + 1,
            self.X + self.Underline + 1
        )
        self.Selected = 1

    def unselected(self):
        self.Parent.addstr(
            self.Y + 1,
            self.X + 1,
            self.LabelButton,
            curses.color_pair(4)
        )
        self.Parent.addstr(
            self.Y + 1,
            self.X + self.Underline + 1,
            self.LabelButton[self.Underline],
            curses.A_REVERSE | curses.color_pair(3)
        )
        self.Selected = 0

    def state(self):
        if self.Selected:
            return 1
        else:
            return 0

    def key_pressed(self, char):
        if char > 255:
            return 0  # skip control-characters
        if chr(char).upper() == self.LabelButton[self.Underline]:
            return 1
        else:
            return 0

    def mouse_clicked(self, mouse_event):
        (mouse_event_id, x, y, z, event) = mouse_event
        if (self.YParent + 3) <= y <= (self.YParent + 3):
            if self.X + self.XParent <= x < (self.X + self.XParent + self.Width - 1):
                return 1
        else:
            return 0