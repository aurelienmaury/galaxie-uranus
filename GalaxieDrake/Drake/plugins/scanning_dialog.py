#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: Jérôme ORNECH alias "Tuux" <tuxa@rtnp.org> all rights reserved
__author__ = 'Tuux'

import curses
from ..utility import resize_text
from ..api.progress_bar import ProgressBar
from ..core.controler_actions import ScanDir

class ScanningDialog(object):
    def __init__(self, model, viewer, parent, y, x, max_y, max_x):
        self.model = model
        self.viewer = viewer
        self.parent = parent
        self.y_parent = y
        self.x_parent = x
        self.y_max_parent = max_y
        self.x_max_parent = max_x
        self.title_text = self.model.display_scanning_text
        self.title_text = str(' ' + self.model.display_scanning_text + ' ')

        # Check if it have space to display it
        if self.y_max_parent > 1:
            self.model.scanning_dialog_sub_box = self.parent.subwin(
                self.y_parent,
                self.x_parent,
                self.y_max_parent,
                self.x_max_parent
            )
            self.model.scanning_dialog_sub_box.bkgdset(ord(' '), curses.color_pair(4))
            self.model.scanning_dialog_sub_box.bkgd(ord(' '), curses.color_pair(4))

            sub_box_y, sub_box_x = self.model.scanning_dialog_sub_box.getbegyx()
            sub_box_y_max, sub_box_x_max = self.model.scanning_dialog_sub_box.getmaxyx()

            # Title
            line_mum = 0
            x_pos = 1
            if sub_box_y_max - 1 > line_mum:
                self.model.scanning_dialog_sub_box.box()
                self.model.scanning_dialog_sub_box.addstr(
                    line_mum,
                    (sub_box_x_max / 2) - (len(self.title_text) / 2),
                    str(self.title_text),
                    curses.color_pair(5)
                )

            line_mum += 1
            if sub_box_y_max - 1 > line_mum:
                self.model.scanning_dialog_sub_box.addstr(
                    line_mum,
                    x_pos,
                    resize_text(self.model.scanning_source_directory_label_text, sub_box_x_max - 2),
                    curses.color_pair(4)
                )

            line_mum += 1
            if sub_box_y_max - 1 > line_mum:
                self.model.scanning_dialog_sub_box.addstr(
                    line_mum,
                    x_pos,
                    resize_text(' ' + self.model.scanning_directory + '/', sub_box_x_max - 2),
                    curses.color_pair(4)
                )

            line_mum += 1
            if sub_box_y_max - 1 > line_mum:
                self.model.scanning_dialog_sub_box.addstr(
                    line_mum,
                    x_pos,
                    resize_text(self.model.scanning_searching_for_label_text, sub_box_x_max - 2),
                    curses.color_pair(4)
                )

            line_mum += 1
            if sub_box_y_max - 1 > line_mum:
                self.model.scanning_dialog_sub_box.addstr(
                    line_mum,
                    x_pos,
                    resize_text(' ' + self.model.searching_extension_list_label_text, sub_box_x_max - 2),
                    curses.color_pair(4)
                )

            line_mum += 1
            if sub_box_y_max - 1 > line_mum:
                self.model.scanning_dialog_sub_box.addstr(
                    line_mum,
                    x_pos,
                    resize_text(self.model.scanning_exception_pattern_label_text, sub_box_x_max - 2),
                    curses.color_pair(4)
                )

            line_mum += 1
            if sub_box_y_max - 1 > line_mum:
                self.model.scanning_dialog_sub_box.addstr(
                    line_mum,
                    x_pos,
                    resize_text(' ' + self.model.searching_file_pattern_exception, sub_box_x_max - 2),
                    curses.color_pair(4)
                )

            line_mum += 1
            if sub_box_y_max - 1 > line_mum:
                self.model.scanning_dialog_sub_box.addstr(
                    line_mum,
                    x_pos,
                    resize_text(self.model.scanning_scanning_for_label_text +
                                ' ' + self.model.scanning_file_pattern, sub_box_x_max - 2),
                    curses.color_pair(4)
                )

            line_mum += 1
            if sub_box_y_max - 1 > line_mum:
                ProgressBar(
                    self.model.scanning_dialog_sub_box,
                    line_mum,
                    x_pos + 2,
                    self.model.scanning_percent,
                    sub_box_x_max - 6,
                    curses.color_pair(4),
                    curses.color_pair(2),
                    '',
                    char=' ',
                    bold=None
                )
        # Inside the history menu
        # sub_box.bkgdset(ord(' '), self.color)
        # sub_box.bkgd(ord(' '), self.color)
        # sub_box_num_lines, sub_box_num_cols = sub_box.getmaxyx()
        # max_cols_to_display = dialog_box_num_cols - 2

        # max_lines_to_display = 1
        # for I in range(0, sub_box_num_lines-2):
        #     sub_box.addstr(
        #         I+1,
        #         1,
        #         str(" " * int(sub_box_num_cols-2)),
        #         self.color
        #     )
        #     max_lines_to_display += 1
        #
        # sub_box.addstr(
        #     0,
        #     (sub_box_num_cols / 2) - (len(self.label) / 2),
        #     self.label,
        #     curses.color_pair(5)
        # )
                ScanDir(
                    self.model,
                    self.viewer
                )

    def refresh(self):
        self.parent.refresh()

