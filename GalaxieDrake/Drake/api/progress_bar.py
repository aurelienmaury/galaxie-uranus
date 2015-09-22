# coding=utf-8
__author__ = 'tuxa'
import curses
import curses.ascii
import sys

class ProgressBar(object):
    def __init__(self, parent, y, x, percent, size, bg_color, fg_color, label=""):
        self.parent = parent
        self.y_parent, self.x_parent = self.parent.getbegyx()
        self.y = y
        self.x = x
        self.percent = float(percent)
        self.size = size
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.text_to_delete = "[]100.0%"
        self.label = label
        self.text_to_delete += str(self.label)
        self.size -= len(self.text_to_delete)
        if self.size + len(str(self.label)) >= len(str(self.label)) - 2:
            self.parent.addstr(
                self.y,
                self.x,
                str(self.label),
                self.bg_color | curses.A_BOLD
            )
            if not len(str(self.text_to_delete)) - len(self.label) >= self.size + 9:
                self.parent.addstr(
                    self.y,
                    self.x + len(str(label)),
                    "[",
                    self.bg_color | curses.A_BOLD
                )

                #self.parent.addstr(self.y, self.x + 1, "coucou", self.fg_color)
                self.parent.addstr(
                    self.y,
                    self.x + len(str(label)) + 1,
                    str("|" * int(self.size * self.percent / 100)),
                    self.fg_color | curses.A_BOLD
                )
                self.parent.addstr(
                    self.y,
                    self.x + len(str(label)) + self.size + 1,
                    "]",
                    self.bg_color | curses.A_BOLD
                )

            dist_x = self.x + self.size + 4 + 4
            cpu_num_color = self.bg_color
            if int(round(self.percent)) >= 0:
                    dist_x = self.x + len(str(label)) + self.size + 1 + 3
                    cpu_num_color = self.bg_color
            if int(round(self.percent)) >= 10:
                    dist_x = self.x + len(str(label)) + self.size + 1 + 2
                    cpu_num_color = self.bg_color
            if int(round(self.percent)) >= 70:
                    dist_x = self.x + len(str(label)) + self.size + 1 + 2
                    cpu_num_color = curses.color_pair(7)
            if int(round(self.percent)) >= 95:
                    dist_x = self.x + len(str(label)) + self.size + 1 + 2
                    cpu_num_color = curses.color_pair(9)
            if int(round(self.percent)) == 100:
                    dist_x = self.x + len(str(label)) + self.size + 1 + 1
                    cpu_num_color = curses.color_pair(9)

            self.parent.addstr(
                self.y,
                dist_x,
                str(str(self.percent) + "%"),
                cpu_num_color | curses.A_BOLD
            )

        #rows, columns = os.popen('stty size', 'r').read().split()
        #self.cli_progress_bar(
        #    "Scaning for " + file_pattern.upper()[2:] + ": ",
        #    int(round(100 * count / len(extension_list))),
        #    100,
        #    int(self.x_parent)
        #)
