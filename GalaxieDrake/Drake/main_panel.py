__author__ = 'tuxa'

import curses
import platform

from Drake.api.progress_bar import ProgressBar
from Drake.plugins.task_spooler_summary import TaskSpoolerSummary


class MainPanel(object):
    def __init__(self, parent, y, x, model):
        # Import Class arguments
        self.parent = parent
        self.y = y
        self.x = x
        self.model = model

        # Get Parent dimensions
        self.y_parent, self.x_parent = self.parent.getbegyx()
        self.y_parent_max, self.x_parent_max = self.parent.getmaxyx()
        self.width = self.x_parent_max

        # Import Data's
        self.u_name_list = platform.uname()
        self.sys_name_text = self.u_name_list[0]
        self.node_name_text = self.u_name_list[1]
        self.release_text = self.u_name_list[2]
        self.version_text = self.u_name_list[3]
        self.machine_text = self.u_name_list[4]
        self.processor_text = self.u_name_list[5]
        self.architecture_text = platform.architecture()[0]
        self.distribution_name_text = platform.dist()[0]
        self.distribution_version_text = platform.dist()[1]

        # Prepare the tile
        # uranus (debian 8.1 64bit / Linux 3.16.0-4-amd64)
        self.system_information_text = ""
        self.system_information_text += "("
        self.system_information_text += self.distribution_name_text
        self.system_information_text += " "
        self.system_information_text += self.distribution_version_text
        self.system_information_text += " "
        self.system_information_text += self.architecture_text
        self.system_information_text += " / "
        self.system_information_text += self.sys_name_text
        self.system_information_text += " "
        self.system_information_text += str(self.release_text)
        self.system_information_text += ")"

        self.cpu_number = len(self.model.cpu_percent_list)
        self.cpu_label_text = self.model.cpu_label_text
        if self.cpu_number <= 1:
            self.by_cpu_size_allowed = self.x_parent_max - 2
        else:
            self.by_cpu_size_allowed = (self.x_parent_max - 2) / self.cpu_number

        self.mem_swap_size_allowed = (self.x_parent_max - 1) / 2

        # Position and calculation
        x_pos_up_time = (self.x_parent_max - len(str(self.model.up_time)) - 1)
        x_pos_system_information = 1 + len(self.node_name_text)

        system_information_size = len(self.system_information_text)
        system_information_size_available = x_pos_up_time - x_pos_system_information

        up_time_information_size = len(self.model.up_time)
        up_time_information_size_available = self.x_parent_max - 1

        # It_can_be_display use by the scrolling
        self.model.main_panel_item_it_can_be_display = 0

        for _ in range(self.y, self.y_parent_max - 1):
            self.model.main_panel_item_it_can_be_display += 1

        # Titles Line  Positions
        self.y_pos_titles_line = int(self.y + 2)

        # Set the entire background with the same color
        self.parent.bkgd(ord(' '), curses.color_pair(3))

        # Scrolling control before everything
        # The scrolling is done via a List position it change via the controller Touch Key

        for I in range(self.y + 1, self.model.main_panel_item_it_can_be_display):
            # actual_line_pos is use by the entire page where "2" is the start
            # actual_line_pos = I
            if I < self.y_parent_max:

                line_number = 1
                # Display the hostname in bold
                self.parent.addstr(
                    line_number,
                    1,
                    self.node_name_text,
                    curses.color_pair(3) | curses.A_BOLD
                )
                # If the size is available the system_information is display
                if system_information_size_available > system_information_size:
                    self.parent.addstr(
                        line_number,
                        x_pos_system_information,
                        str(" " + self.system_information_text),
                        curses.color_pair(3)
                    )
                # Up_time is attache to the right position of the screen
                if (up_time_information_size_available - 1) > up_time_information_size:
                    self.parent.addstr(
                        line_number,
                        x_pos_up_time,
                        str(self.model.up_time),
                        curses.color_pair(3)
                    )

                line_number = 2
                # Use for have a center visual during dev
                self.parent.addstr(
                    line_number,
                    (self.x_parent_max - 1) / 2,
                    str("|"),
                    curses.color_pair(3) | curses.A_BOLD
                )

                # CPU Displays
                line_number = 3
                for cpu_num in range(0, len(self.model.cpu_percent_list)):
                    cpu_num_percent = self.model.cpu_percent_list[cpu_num]
                    cpu_num_text = self.cpu_label_text + str(int(cpu_num + 1)) + ""
                    if cpu_num == 0:
                        x_pos = 1
                    else:
                        x_pos = ((self.by_cpu_size_allowed - 2) * cpu_num) + (3 * cpu_num)

                    ProgressBar(
                        self.parent,
                        line_number,
                        x_pos,
                        cpu_num_percent,
                        self.by_cpu_size_allowed - 2,
                        curses.color_pair(3),
                        curses.color_pair(10),
                        cpu_num_text
                    )

                line_number = 5
                x_pos = 1
                ProgressBar(
                    self.parent,
                    line_number,
                    x_pos,
                    50.0,
                    self.mem_swap_size_allowed,
                    curses.color_pair(3),
                    curses.color_pair(1),
                    "Mem "
                )
                ProgressBar(
                    self.parent,
                    line_number,
                    x_pos + self.mem_swap_size_allowed,
                    50.0,
                    self.mem_swap_size_allowed + 1,
                    curses.color_pair(3),
                    curses.color_pair(1),
                    "Swap"
                )

                line_number = 7
                x_pos = 1
                TaskSpoolerSummary(
                    self.parent,
                    line_number,
                    x_pos,
                    self.x_parent_max - 2,
                    self.model
                )
                # line_number = 9
                # self.parent.addstr(
                #     line_number,
                #     self.x + 1,
                #     str("(" + str(taskspooler_pos_end) + ") < (" + str(self.x_parent_max - 2) + ")"),
                #     curses.color_pair(3)
                # )
