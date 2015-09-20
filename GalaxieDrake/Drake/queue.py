#!/usr/bin/python
# -*- coding: utf-8 -*-
# Write by Tuxa <tuxa galaxie.eu.org>
# It script it publish on GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html

__author__ = 'tuxa www.rtnp.org'
import curses

from Drake.api.clickable_text import clickable_sort_by_text
from .utility import resize_text
from .utility import secs_to_human_read
from Drake.plugins.task_spooler_summary import TaskSpoolerSummary


class Queue(object):
    def __init__(self, window, y, x, model):
        # Import Class arguments
        self.parent = window
        self.y = y
        self.x = x
        self.model = model

        # Import Variables value from The Model
        self.id_text = self.model.window_queue_id_text
        self.state_text = self.model.window_queue_state_text
        self.output_text = self.model.window_queue_output_text
        self.e_level_text = self.model.window_queue_e_level_text
        self.times_text = self.model.window_queue_times_text
        self.command_text = self.model.window_queue_command_text

        # Get Ncurse Parent dimensions
        self.y_parent, self.x_parent = window.getbegyx()
        self.y_parent_max, self.x_parent_max = window.getmaxyx()
        self.width = self.x_parent_max

        # It_can_be_display use by the scrolling
        line = 0
        for _ in range(self.y + 2, self.y_parent_max - 1):
            line += 1
        self.model.window_queue_item_it_can_be_display = line - 2
        self.model.window_queue_item_number = len(self.model.window_queue_tasks_list)

        self.parent.bkgd(ord(' '), curses.color_pair(3))

        # Calculate Element position
        self.texts_len = 0
        self.texts_len += len(self.id_text)
        self.texts_len += len(self.state_text)
        self.texts_len += len(self.output_text)
        self.texts_len += len(self.e_level_text)
        self.texts_len += len(self.times_text)
        self.texts_len += len(self.command_text)

        if (self.texts_len + 5) >= self.x_parent_max - 2:
            self.x_pos_spacing = 1
        else:
            self.x_pos_spacing = 2

        # Calculation of position for each element
        # It make the maximum of calc here for save CPU time
        # ID Positions
        self.x_pos_id_text = self.x_pos_spacing
        self.x_pos_id_line = self.x_pos_id_text + len(str(self.id_text)) + 1
        self.max_width_of_state_item = int(self.x_pos_spacing - self.x_pos_id_line - self.x_pos_spacing - 1)
        # State Positions
        self.x_pos_state_text = self.x_pos_id_line + self.x_pos_spacing
        self.x_pos_state_line = self.x_pos_state_text + 9
        self.max_width_of_state_item = int(self.x_pos_state_line - self.x_pos_id_line - self.x_pos_spacing - 1)
        # Output Positions
        self.x_pos_output_text = self.x_pos_state_line + self.x_pos_spacing
        self.x_pos_output_line = self.x_pos_output_text + 17 + self.x_pos_spacing
        self.max_width_of_output_item = int(self.x_pos_output_line - self.x_pos_state_line - self.x_pos_spacing - 1)
        # E-Level Positions
        self.x_pos_e_level_text = self.x_pos_output_line + 1
        self.x_pos_e_level_line = self.x_pos_e_level_text + len(str(self.e_level_text))
        self.max_width_of_e_level_item = int(self.x_pos_output_line - self.x_pos_state_line - self.x_pos_spacing - 1)
        # Times Positions
        self.x_pos_times_text = self.x_pos_e_level_line + 1
        self.x_pos_times_line = self.x_pos_times_text + len(str(self.times_text))
        self.max_width_of_times_item = int(self.x_pos_times_line - self.x_pos_e_level_line - self.x_pos_spacing - 1)
        # Command Positions
        self.x_pos_command_text = self.x_pos_times_line + self.x_pos_spacing
        self.max_width_of_command_item = int(self.x_parent_max - self.x_pos_spacing - self.x_pos_times_line - 1)
        # Titles Line  Positions
        self.y_pos_titles_line = int(self.y + 1)
        # Selected line
        self.left_selected_line = self.x + 1

        # First Line

        # Create the 6 Titles with Mouse control for shorting capability
        # ID
        self.model.window_queue_state_object = clickable_sort_by_text(
            self.parent,
            self.y_pos_titles_line,
            self.x_pos_id_text,
            self.id_text,
            curses.color_pair(7) | curses.A_BOLD
        )
        self.parent.vline(
            self.y_pos_titles_line,
            self.x_pos_id_line,
            curses.ACS_VLINE,
            self.y_parent_max - 4
        )
        # State
        self.model.window_queue_output_object = clickable_sort_by_text(
            self.parent,
            self.y_pos_titles_line,
            (((self.x_pos_state_line + self.x_pos_id_line) / 2) - (len(self.state_text) / 2)),
            self.state_text,
            curses.color_pair(7) | curses.A_BOLD
        )
        self.parent.vline(
            self.y_pos_titles_line,
            self.x_pos_state_line,
            curses.ACS_VLINE,
            self.y_parent_max - 4
        )
        # Output
        self.model.window_queue_e_level_object = clickable_sort_by_text(
            self.parent,
            self.y_pos_titles_line,
            (((self.x_pos_output_line + self.x_pos_state_line) / 2) - (len(self.output_text) / 2)),
            self.output_text,
            curses.color_pair(7) | curses.A_BOLD
        )
        self.parent.vline(
            self.y_pos_titles_line,
            self.x_pos_output_line,
            curses.ACS_VLINE,
            self.y_parent_max - 4
        )
        # E-Level
        self.model.window_queue_times_object = clickable_sort_by_text(
            self.parent,
            self.y_pos_titles_line,
            self.x_pos_e_level_text,
            self.e_level_text,
            curses.color_pair(7) | curses.A_BOLD
        )
        self.parent.vline(
            self.y_pos_titles_line,
            self.x_pos_e_level_line,
            curses.ACS_VLINE,
            self.y_parent_max - 4
        )
        # Times
        self.model.window_queue_command_object = clickable_sort_by_text(
            self.parent,
            self.y_pos_titles_line,
            self.x_pos_times_text,
            self.times_text,
            curses.color_pair(7) | curses.A_BOLD
        )
        self.parent.vline(
            self.y_pos_titles_line,
            self.x_pos_times_line,
            curses.ACS_VLINE,
            self.y_parent_max - 4
        )
        # Command:
        self.model.window_queue_command_object = clickable_sort_by_text(
            self.parent,
            self.y_pos_titles_line,
            (((self.x_parent_max + self.x_pos_times_line) / 2) - (len(self.command_text) / 2)),
            self.command_text,
            curses.color_pair(7) | curses.A_BOLD
        )

        # Scrolling control before everything
        # The scrolling is done via a List position it change via the controller Touch Key
        for I in range(0, self.model.window_queue_item_it_can_be_display):
            # actual_line_pos is use by the entire page where "2" is the start
            actual_line_pos = I + 2
            if I < self.model.window_queue_item_number:
                # Try to set the self.model.history_menu_selected_item_value
                # In case it fail consider that a scrolling trouble
                try:
                    # That Section import the job information
                    # That here the scrolling is apply, the 2 "if" correspond to a AND
                    if (self.model.window_queue_item_list_scroll + I) <= self.model.window_queue_item_number:
                        self.model.window_queue_selected_item_list_value = self.model.window_queue_tasks_list[
                            self.model.window_queue_item_list_scroll + I]
                except:
                    # We consider that a scrolling trouble then don't care about values
                    # The only trouble found is where a line have to re-appair from the top
                    self.model.window_queue_selected_item_list_value = ['', '', '', '', '', '']
                    self.model.window_queue_item_list_scroll -= 1
                    self.model.window_queue_selected_item += 1

                # Force the selected high color line to stay on the aviable box size
                if self.model.window_queue_selected_item > self.model.window_queue_item_it_can_be_display - 1:
                    self.model.window_queue_selected_item -= 1

                # Import value from a list store in model, it correspond to one job information
                # The list have 0 to 5 entrys : [ID, State, Output, E-Level, Times, Command]
                # report to "TaskSpooler" manual "man tsp"
                # ID
                job_id_text = self.model.window_queue_selected_item_list_value[0]
                # STATE
                state_text = self.model.window_queue_selected_item_list_value[1]
                # OUTPUT
                output_text = self.model.window_queue_selected_item_list_value[2]
                # EXIT LEVEL
                # have a special text replacement
                e_level_text = self.model.window_queue_selected_item_list_value[3]
                # It consiter like a shell all is not output with exit(0) have make a error
                if not state_text == "running" and not state_text == "queued":
                    if not str(e_level_text) == "0":
                        line_color = curses.color_pair(10)
                        e_level_text = "Error"
                    else:
                        e_level_text = "Ok"
                        line_color = curses.color_pair(3)
                # TIMES
                # have special conversion
                if self.model.window_queue_selected_item_list_value[4]:
                    times_text = secs_to_human_read(self.model.window_queue_selected_item_list_value[4].split('/')[0])
                else:
                    times_text = self.model.window_queue_selected_item_list_value[4]
                # COMMAND
                command_text = self.model.window_queue_selected_item_list_value[5]

                # Resize text
                times_text = str(resize_text(times_text, self.max_width_of_times_item))
                command_text = str(resize_text(command_text, self.max_width_of_command_item))

                actual_times_pos = (
                    self.x_pos_times_text + ((self.x_pos_times_line - self.x_pos_times_text) / 2) - (
                    len(times_text) / 2)
                )

                # Draw the selected Line
                if self.model.window_queue_selected_item == I:
                    self.model.window_queue_selected_item_list_value
                    # Magic line it put with a color the entire line before write something
                    self.parent.addstr(
                        actual_line_pos,
                        self.left_selected_line,
                        str(' ' * int(self.x_parent_max - 2)),
                        curses.color_pair(1)
                    )
                    self.parent.addstr(
                        actual_line_pos,
                        self.x_pos_id_text,
                        str(job_id_text),
                        curses.color_pair(1)
                    )
                    # Special thing where the Runing job is put in evidence
                    if state_text == "running":
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_state_text,
                            str(state_text),
                            curses.color_pair(1) | curses.A_BOLD
                        )
                    else:
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_state_text,
                            str(state_text),
                            curses.color_pair(1)
                        )
                    self.parent.addstr(
                        actual_line_pos,
                        self.x_pos_output_text,
                        str(output_text),
                        curses.color_pair(1)
                    )
                    self.parent.addstr(
                        actual_line_pos,
                        (self.x_pos_e_level_text + ((self.x_pos_e_level_line - self.x_pos_e_level_text) / 2) - (
                        len(e_level_text) / 2)),
                        str(e_level_text),
                        curses.color_pair(1)
                    )
                    self.parent.addstr(
                        actual_line_pos,
                        actual_times_pos,
                        times_text,
                        curses.color_pair(1)
                    )
                    self.parent.addstr(
                        actual_line_pos,
                        self.x_pos_times_line + 2,
                        command_text,
                        curses.color_pair(1)
                    )

                    self.parent.vline(
                        actual_line_pos,
                        self.x_pos_id_line,
                        curses.ACS_VLINE,
                        1,
                        curses.color_pair(1)
                    )
                    self.parent.vline(
                        actual_line_pos,
                        self.x_pos_state_line,
                        curses.ACS_VLINE,
                        1,
                        curses.color_pair(1)
                    )
                    self.parent.vline(
                        actual_line_pos,
                        self.x_pos_output_line,
                        curses.ACS_VLINE,
                        1,
                        curses.color_pair(1)
                    )
                    self.parent.vline(
                        actual_line_pos,
                        self.x_pos_e_level_line,
                        curses.ACS_VLINE,
                        1,
                        curses.color_pair(1)
                    )
                    self.parent.vline(
                        actual_line_pos,
                        self.x_pos_times_line,
                        curses.ACS_VLINE,
                        1,
                        curses.color_pair(1)
                    )

                else:
                    # We are sure to no write the selected line
                    # We start by check the status
                    # "running" apply a color a apply bold
                    if state_text == "running":
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_id_text,
                            str(job_id_text),
                            curses.color_pair(8) | curses.A_BOLD
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_state_text,
                            str(state_text),
                            curses.color_pair(8) | curses.A_BOLD
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_output_text,
                            str(output_text),
                            curses.color_pair(8) | curses.A_BOLD
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_e_level_text + (self.x_pos_e_level_line - self.x_pos_e_level_text) / 2,
                            str(e_level_text),
                            curses.color_pair(8) | curses.A_BOLD
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            actual_times_pos,
                            times_text,
                            curses.color_pair(8) | curses.A_BOLD
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_times_line + 2,
                            command_text,
                            curses.color_pair(8) | curses.A_BOLD
                        )
                    # "queued" apply a color a apply bold
                    elif state_text == "queued":
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_id_text,
                            str(job_id_text),
                            curses.color_pair(3) | curses.A_BOLD
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_state_text,
                            str(state_text),
                            curses.color_pair(3) | curses.A_BOLD
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_output_text,
                            str(output_text),
                            curses.color_pair(3) | curses.A_BOLD
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_e_level_text + (self.x_pos_e_level_line - self.x_pos_e_level_text) / 2,
                            str(e_level_text),
                            curses.color_pair(3) | curses.A_BOLD
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            actual_times_pos,
                            times_text,
                            curses.color_pair(3) | curses.A_BOLD
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_times_line + 2,
                            command_text,
                            curses.color_pair(3) | curses.A_BOLD
                        )
                    # It have only running and queud status to search all the rest be display now
                    else:
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_id_text,
                            str(job_id_text),
                            line_color
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_state_text,
                            str(state_text),
                            line_color
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_output_text,
                            str(output_text),
                            line_color
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            (self.x_pos_e_level_text + ((self.x_pos_e_level_line - self.x_pos_e_level_text) / 2) - (
                            len(e_level_text) / 2)),
                            str(e_level_text),
                            line_color
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            actual_times_pos,
                            times_text,
                            line_color
                        )
                        self.parent.addstr(
                            actual_line_pos,
                            self.x_pos_times_line + 2,
                            command_text,
                            line_color
                        )
        line_number = self.y_parent_max  - 2
        x_pos = 1
        TaskSpoolerSummary(
            self.parent,
            line_number,
            x_pos,
            self.x_parent_max - 3,
            self.model
        )
        self.parent.hline(
            line_number - 1,
            x_pos,
            curses.ACS_HLINE,
            self.x_parent_max - 2
        )
    def refresh(self):
        self.parent.refresh()
