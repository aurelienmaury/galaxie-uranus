#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: Jérôme ORNECH alias "Tuux" <tuxa@rtnp.org> all rights reserved
__author__ = 'Tuux'

import curses


class dialog_box():

    def __init__(self, model, parent, y, x, label, color):

        self.model = model
        self.parent = parent
        self.y_parent, self.x_parent = self.parent.getbegyx()
        self.y_max_parent, self.x_max_parent = self.parent.getmaxyx()
        self.y = y
        self.x = x
        self.label = str(label)
        self.label = str(" "+label+" ")
        self.width = len(str(label))
        self.color = color

        # Calcul for history window size it depend of the history list
        if len(self.model.window_source_history_dir_list)+2 < self.y_max_parent:
            dialog_box_y = len(self.model.window_source_history_dir_list) + 2

        else:
            dialog_box_y = self.y_max_parent - 1

        if len(self.model.window_source_history_dir_list) > 0:
            dialog_box_x = len(max(self.model.window_source_history_dir_list, key=len)) + 2
            if dialog_box_x > self.x_max_parent - 1:
                dialog_box_x = self.x_max_parent
        else:
            dialog_box_x = len(self.label) + 2

        dialog_box = self.parent.subwin(
            dialog_box_y,
            dialog_box_x,
            2,
            0
        )

        # Inside the history menu
        dialog_box.bkgdset(ord(' '), self.color)
        dialog_box.bkgd(ord(' '), self.color)
        dialog_box_num_lines, dialog_box_num_cols = dialog_box.getmaxyx()
        max_cols_to_display = dialog_box_num_cols - 2
        max_lines_to_display = 1

        for I in range(0, dialog_box_num_lines-2):
            dialog_box.addstr(I+1,
                               1,
                               str(" " * int(dialog_box_num_cols-2)),
                               self.color
                               )
            max_lines_to_display += 1
        self.model.history_menu_can_be_display = max_lines_to_display


        dialog_box.box()
        dialog_box.addstr(
            0,
            (dialog_box_num_cols / 2) - (len(self.label) / 2),
            self.label,
            curses.color_pair(5)
        )

    def mouse_clicked(self, mouse_event):
        (event_id, x, y, z, event) = mouse_event
        if self.y_parent <= y <= self.y_parent + 1:
            if self.x + self.x_parent <= x < self.x + self.x_parent + self.width:
                return 1
        else:
            return 0
