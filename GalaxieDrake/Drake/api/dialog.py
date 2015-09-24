#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: Jérôme ORNECH alias "Tuux" <tuxa@rtnp.org> all rights reserved
__author__ = 'Tuux'

import curses
from ..plugins.scanning_dialog import ScanningDialog


class DialogBox(object):

    def __init__(self, model, viewer, parent, label, color, dialog_type=None):

        self.model = model
        self.viewer = viewer
        self.parent = parent
        self.y_parent, self.x_parent = self.parent.getbegyx()
        self.y_max_parent, self.x_max_parent = self.parent.getmaxyx()
        self.label = str(label)
        self.label = str(" "+label+" ")
        self.width = len(str(label))
        self.color = color
        self.type = dialog_type

        # Dialog window size it depend of parent size
        dialog_box_y_spacing = self.y_max_parent / 3
        if self.y_max_parent > (dialog_box_y_spacing * 2) + 4:
            dialog_box_y = self.y_max_parent - (dialog_box_y_spacing * 2)
        else:
            dialog_box_y = self.y_max_parent - 3
        dialog_box_x_spacing = self.x_max_parent / 6
        dialog_box_x = self.x_max_parent - dialog_box_x_spacing

        self.model.dialog_box = self.parent.subwin(
            dialog_box_y,
            dialog_box_x,
            dialog_box_y_spacing,
            (dialog_box_x_spacing / 2) + 2
        )

        dialog_box_num_lines, dialog_box_num_cols = self.model.dialog_box.getmaxyx()
        dialog_box_y, dialog_box_x = self.model.dialog_box.getbegyx()

        if self.type == 'scan':
            # Set Color and Load a plugin it have the size of the parent
            if curses.has_colors():
                self.model.dialog_box.bkgdset(ord(' '), curses.color_pair(4))
                self.model.dialog_box.bkgd(ord(' '), curses.color_pair(4))
                for I in range(0, dialog_box_num_lines):
                    self.model.dialog_box.addstr(I, 0, str(' ' * int(dialog_box_num_cols - 1)), curses.color_pair(4))
                    self.model.dialog_box.insstr(I, int(dialog_box_num_cols - 1), str(' '), curses.color_pair(4))

            self.model.scanning_dialog_sub_box = ScanningDialog(
                self.model,
                self.viewer,
                self.parent,
                dialog_box_num_lines - 2,
                dialog_box_num_cols - 2,
                dialog_box_y + 1,
                dialog_box_x + 1
            )

    def mouse_clicked(self, mouse_event):
        (event_id, x, y, z, event) = mouse_event
        if self.y_parent <= y <= self.y_parent + 1:
            if x + self.x_parent <= x < x + self.x_parent + self.width:
                return 1
        else:
            return 0
