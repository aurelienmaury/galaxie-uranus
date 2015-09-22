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

        # Prepare the title
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

        self.cpu_number = len(self.model.psutil_cpu_percent_list)
        self.cpu_label_text = self.model.cpu_label_text

        self.mem_label_text = self.model.mem_label_text
        self.swap_label_text = self.model.swap_label_text
        self.progress_bar_size_allowed = self.x_parent_max - 2
        # Remove the text len of memory
        self.progress_bar_size_allowed -= 22

        # Position and calculation
        x_pos_up_time = (self.x_parent_max - len(str(self.model.up_time)) - 1)
        x_pos_system_information = 1 + len(self.node_name_text)

        system_information_size = len(self.system_information_text)
        system_information_size_available = x_pos_up_time - x_pos_system_information

        up_time_information_size = len(self.model.up_time)
        up_time_information_size_available = self.x_parent_max - 1

        column_lenght = 6
        spacing = 1
        column_1_start = self.progress_bar_size_allowed + spacing + 1
        column_1_end = column_1_start + column_lenght + 1
        column_2_start = column_1_end + 1
        column_2_end = column_2_start + column_lenght
        column_3_start = column_2_end + 1
        column_3_end = column_3_start + column_lenght


        # It_can_be_display use by the scrolling
        self.model.main_panel_item_it_can_be_display = 0

        for _ in range(self.y, self.y_parent_max - 1):
            self.model.main_panel_item_it_can_be_display += 1

        # Titles Line  Positions
        self.y_pos_titles_line = int(self.y + 2)

        # Set the entire background with the same color
        self.parent.bkgd(ord(' '), curses.color_pair(3))

        x_pos = 1

        line_number = 1
        if self.y_parent_max - 1 > line_number:
            # Display the hostname in bold
            self.parent.addstr(
                line_number,
                x_pos,
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

        line_number += 1
        if self.y_parent_max - 1 > line_number:
            # Use for have a center visual during dev
            self.parent.addstr(
                line_number,
                (self.x_parent_max - 1) / 2,
                str(""),
                curses.color_pair(3) | curses.A_BOLD
            )

        # Pocessor Informations
        line_number += 1

        x_pos_iowait_value = self.x_parent_max - 1
        x_pos_iowait_value -= len(str(str(self.model.psutil_cpu_times_percent_list.iowait) + '%'))
        x_pos_iowait_label = x_pos_iowait_value - 1
        x_pos_iowait_label -= len(self.model.iowait_label_text)

        x_pos_idle_value = x_pos_iowait_label - 2
        x_pos_idle_value -= len(str(str(self.model.psutil_cpu_times_percent_list.idle) + '%'))
        x_pos_idle_label = x_pos_idle_value - 1
        x_pos_idle_label -= len(self.model.idle_label_text)

        x_pos_system_value = x_pos_idle_label - 2
        x_pos_system_value -= len(str(str(self.model.psutil_cpu_times_percent_list.system) + '%'))
        x_pos_system_label = x_pos_system_value - 1
        x_pos_system_label -= len(self.model.system_label_text)

        x_pos_nice_value = x_pos_system_label - 2
        x_pos_nice_value -= len(str(str(self.model.psutil_cpu_times_percent_list.nice) + '%'))
        x_pos_nice_label = x_pos_nice_value - 1
        x_pos_nice_label -= len(self.model.nice_label_text)

        x_pos_user_value = x_pos_nice_label - 2
        x_pos_user_value -= len(str(str(self.model.psutil_cpu_times_percent_list.user) + '%'))
        x_pos_user_label = x_pos_user_value - 1
        x_pos_user_label -= len(self.model.user_label_text)

        if self.y_parent_max - 1 > line_number:
            if len(self.model.processor_summary_text) + 2 <= x_pos_user_label:
                self.parent.addstr(
                    line_number,
                    x_pos,
                    str(self.model.processor_summary_text),
                    curses.color_pair(3)
                )
            # user 1.5%, nice 0.0%, system 0.5%, idle 96.5%, iowait 1.5%
            if not x_pos_user_label + 2 <= 2:
                self.parent.addstr(
                    line_number,
                    x_pos_user_label,
                    str(self.model.user_label_text),
                    curses.color_pair(3)
                )
                self.parent.addstr(
                    line_number,
                    x_pos_user_value,
                    str(str(self.model.psutil_cpu_times_percent_list.user) + '%'),
                    curses.color_pair(3) | curses.A_BOLD
                )
            if not x_pos_nice_label + 2 <= 2:
                self.parent.addstr(
                    line_number,
                    x_pos_nice_label,
                    str(self.model.nice_label_text),
                    curses.color_pair(3)
                )
                self.parent.addstr(
                    line_number,
                    x_pos_nice_value,
                    str(str(self.model.psutil_cpu_times_percent_list.nice) + '%'),
                    curses.color_pair(3) | curses.A_BOLD
                )
            if not x_pos_system_label + 2 <= 2:
                self.parent.addstr(
                    line_number,
                    x_pos_system_label,
                    str(self.model.system_label_text),
                    curses.color_pair(3)
                )
                self.parent.addstr(
                    line_number,
                    x_pos_system_value,
                    str(str(self.model.psutil_cpu_times_percent_list.system) + '%'),
                    curses.color_pair(3) | curses.A_BOLD
                )
            if not x_pos_idle_label + 2 <= 2:
                self.parent.addstr(
                    line_number,
                    x_pos_idle_label,
                    str(self.model.idle_label_text),
                    curses.color_pair(3)
                )
                self.parent.addstr(
                    line_number,
                    x_pos_idle_value,
                    str(str(self.model.psutil_cpu_times_percent_list.idle) + '%'),
                    curses.color_pair(3) | curses.A_BOLD
                )
            if not x_pos_iowait_label + 2 <= 2:
                self.parent.addstr(
                    line_number,
                    x_pos_iowait_label,
                    str(self.model.iowait_label_text),
                    curses.color_pair(3)
                )
                self.parent.addstr(
                    line_number,
                    x_pos_iowait_value,
                    str(str(self.model.psutil_cpu_times_percent_list.iowait) + '%'),
                    curses.color_pair(3) | curses.A_BOLD
                )


        # CPU Displays
        line_number += 1
        for cpu_num in range(0, len(self.model.psutil_cpu_percent_list)):
            cpu_num_percent = self.model.psutil_cpu_percent_list[cpu_num]
            cpu_num_text = self.cpu_label_text + str(int(cpu_num + 1)) + " "
            if self.y_parent_max - 1 > line_number:
                ProgressBar(
                    self.parent,
                    line_number,
                    x_pos,
                    cpu_num_percent,
                    self.x_parent_max - 2,
                    curses.color_pair(3),
                    curses.color_pair(10),
                    cpu_num_text
                )

            line_number += 1
        # Title Total Free Used
        line_number += 1
        if self.y_parent_max - 1 > line_number:
            if not column_1_start + 1 <= len(str(self.model.memory_title_text)):
                self.parent.addstr(
                    line_number,
                    x_pos,
                    str(self.model.memory_title_text),
                    curses.color_pair(3)
                )
            if not column_1_start + 1 <= x_pos:
                self.parent.addstr(
                    line_number,
                    column_1_start + 1,
                    str(self.model.total_label_text),
                    curses.color_pair(7) | curses.A_BOLD
                )
            if not column_2_start + 1 <= x_pos:
                self.parent.addstr(
                    line_number,
                    column_2_start + 1,
                    str(self.model.used_label_text),
                    curses.color_pair(7) | curses.A_BOLD
                )
            if not column_3_start + 1 <= x_pos:
                self.parent.addstr(
                    line_number,
                    column_3_start + 1,
                    str(self.model.free_label_text),
                    curses.color_pair(7) | curses.A_BOLD
                )
        # MEM
        line_number += 1
        if self.y_parent_max - 1 > line_number:
            ProgressBar(
                self.parent,
                line_number,
                x_pos,
                self.model.psutil_virtual_memory.percent,
                self.progress_bar_size_allowed,
                curses.color_pair(3),
                curses.color_pair(10),
                self.mem_label_text
            )
            if not column_1_start + 1 <= x_pos:
                self.parent.vline(
                    line_number,
                    column_1_start,
                    curses.ACS_VLINE,
                    1
                )
                self.parent.addstr(
                    line_number,
                    column_1_end - len(self.model.memory_total),
                    str(self.model.memory_total),
                    curses.color_pair(3)
                )
            if not column_2_start + 1 <= x_pos:
                self.parent.vline(
                    line_number,
                    column_1_end,
                    curses.ACS_VLINE,
                    1
                )
                self.parent.addstr(
                    line_number,
                    column_2_end - len(self.model.memory_used),
                    str(self.model.memory_used),
                    curses.color_pair(3)
                )
            if not column_3_start + 1 <= x_pos:
                self.parent.vline(
                    line_number,
                    column_2_end,
                    curses.ACS_VLINE,
                    1
                )
                self.parent.addstr(
                    line_number,
                    column_3_end - len(self.model.memory_free),
                    str(self.model.memory_free),
                    curses.color_pair(3)
                )
        # SWAP
        line_number += 1
        if self.y_parent_max - 1 > line_number:
            ProgressBar(
                self.parent,
                line_number,
                x_pos,
                self.model.psutil_swap_memory.percent,
                self.progress_bar_size_allowed,
                curses.color_pair(3),
                curses.color_pair(10),
                self.swap_label_text
            )
            if not column_1_start + 1 <= x_pos:
                self.parent.vline(
                    line_number,
                    column_1_start,
                    curses.ACS_VLINE,
                    1
                )
                self.parent.addstr(
                    line_number,
                    column_1_end - len(self.model.swap_total),
                    str(self.model.swap_total),
                    curses.color_pair(3)
                )
            if not column_2_start + 1 <= x_pos:
                self.parent.vline(
                    line_number,
                    column_1_end,
                    curses.ACS_VLINE,
                    1
                )
                self.parent.addstr(
                    line_number,
                    column_2_end - len(self.model.swap_used),
                    str(self.model.swap_used),
                    curses.color_pair(3)
                )
            if not column_3_start + 1 <= x_pos:
                self.parent.vline(
                    line_number,
                    column_2_end,
                    curses.ACS_VLINE,
                    1
                )
                self.parent.addstr(
                    line_number,
                    column_3_end - len(self.model.swap_free),
                    str(self.model.swap_free),
                    curses.color_pair(3)
                )
        # Title Total Free Used
        line_number += 2
        if self.y_parent_max - 1 > line_number:
            if not column_1_start + 1 <= len(str(self.model.disks_title_text)):
                self.parent.addstr(
                    line_number,
                    x_pos,
                    str(self.model.disks_title_text),
                    curses.color_pair(3)
                )
            if not column_1_start + 1 <= x_pos:
                self.parent.addstr(
                    line_number,
                    column_1_start + 1,
                    str(self.model.total_label_text),
                    curses.color_pair(7) | curses.A_BOLD
                )
            if not column_2_start + 1 <= x_pos:
                self.parent.addstr(
                    line_number,
                    column_2_start + 1,
                    str(self.model.used_label_text),
                    curses.color_pair(7) | curses.A_BOLD
                )
            if not column_3_start + 1 <= x_pos:
                self.parent.addstr(
                    line_number,
                    column_3_start + 1,
                    str(self.model.free_label_text),
                    curses.color_pair(7) | curses.A_BOLD
                )

        # Mount Point
        for mount_point in self.model.disk_partition_list:
            line_number += 1
            if self.y_parent_max - 1 > line_number:
                ProgressBar(
                    self.parent,
                    line_number,
                    x_pos,
                    mount_point[4],
                    self.progress_bar_size_allowed,
                    curses.color_pair(3),
                    curses.color_pair(10),
                    mount_point[5] + " "
                )
                if not column_1_start + 1 <= x_pos:
                    self.parent.vline(
                        line_number,
                        column_1_start,
                        curses.ACS_VLINE,
                        1
                    )
                    self.parent.addstr(
                        line_number,
                        column_1_end - len(str(mount_point[1])),
                        str(mount_point[1]),
                        curses.color_pair(3)
                    )
                if not column_2_start + 1 <= x_pos:
                    self.parent.vline(
                        line_number,
                        column_1_end,
                        curses.ACS_VLINE,
                        1
                    )
                    self.parent.addstr(
                        line_number,
                        column_2_end - len(str(mount_point[2])),
                        str(mount_point[2]),
                        curses.color_pair(3)
                    )
                if not column_3_start + 1 <= x_pos:
                    self.parent.vline(
                        line_number,
                        column_2_end,
                        curses.ACS_VLINE,
                        1
                    )
                    self.parent.addstr(
                        line_number,
                        column_3_end - len(str(mount_point[3])),
                        str(mount_point[3]),
                        curses.color_pair(3)
                    )

        # Task SPoller Summary
        line_number += 2
        if self.y_parent_max - 1 > line_number:
            x_pos = 1
            TaskSpoolerSummary(
                self.parent,
                line_number,
                x_pos,
                self.x_parent_max - 2,
                self.model
            )

        # DEBUG
        # line_number += 1
        # self.parent.addstr(
        #     line_number,
        #     self.x + 1,
        #     str(self.model.processor_summary_text),
        #     curses.color_pair(3)
        # )
