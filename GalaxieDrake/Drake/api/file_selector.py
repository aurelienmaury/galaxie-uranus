#!/usr/bin/python

'''
Created on 4 avr. 2015

@author: tuxa
'''

import curses
import os
from os.path import expanduser
from operator import itemgetter

from Drake.api.clickable_text import clickable_sort_by_text
from Drake.history import creat_history_box
from Drake.utility import disk_usage
from Drake.utility import get_file_info_list
from Drake.utility import resize_text


class FileSelect(object):
    def __init__(self, window, y, x, model):
        self.model = model
        self.name_text = self.model.window_source_name_text
        self.size_text = self.model.window_source_size_text
        self.mtime_text = self.model.window_source_mtime_text

        self.Parent = window
        self.YParent, self.XParent = window.getbegyx()
        self.YParentMax, self.XParentMax = window.getmaxyx()
        self.Y = y
        self.X = x
        self.Width = self.XParentMax

        # Creat a Tuple with Upper Lower and Title extension
        # Exemple: .mkv -> ('.mkv','.Mkv','MKV')
        video_file_extensions_temp = list()
        # Lower -> .mkv
        for I in list(self.model.video_file_extensions):
            video_file_extensions_temp.append(I.lower())
        # Title -> Mkv
        for I in list(self.model.video_file_extensions):
            video_file_extensions_temp.append(I.title())
        # Upper -> .MKV
        for I in list(self.model.video_file_extensions):
            video_file_extensions_temp.append(I.upper())
        video_file_extensions = tuple(video_file_extensions_temp)

        # We consider to be on the local directory
        self.dir_name = "."
        self.file_list = os.listdir(self.dir_name)
        self.file_list.sort()
        self.list_item_info = list()

        # Prepare the super list with all informations to display
        for I in self.file_list:
            self.list_item_info.append(get_file_info_list(I, self.model))

        # Prepare list by sort
        # Sort by name
        if self.model.window_source_sort_by_name == 1:
            list_file = list()
            list_dir = list()
            if self.model.window_source_sort_name_order == 1:
                for tmp in self.file_list:
                    if os.path.isfile(tmp):
                        list_file.append(tmp)
                    else:
                        list_dir.append(tmp)
                list_file.sort()
                list_dir.sort()
            else:
                for tmp in reversed(self.file_list):
                    if os.path.isfile(tmp):
                        list_file.append(tmp)
                    else:
                        list_dir.append(tmp)
            self.file_list = list_dir + list_file

        # Sort by size
        elif self.model.window_source_sort_by_size == 1:
            self.list_item_info.sort(key=itemgetter(4))
            tmp_file = list()
            if self.model.window_source_sort_size_order == 1:
                for tmp in self.list_item_info:
                    tmp_file.append(tmp[0])
            else:
                for tmp in reversed(self.list_item_info):
                    tmp_file.append(tmp[0])
            self.file_list = tmp_file

        # Sort by Time
        elif self.model.window_source_sort_by_mtime == 1:
            self.list_item_info.sort(key=itemgetter(5))
            tmp_file = list()
            if self.model.window_source_sort_mtime_order == 0:
                for tmp in self.list_item_info:
                    tmp_file.append(tmp[0])
            else:
                for tmp in reversed(self.list_item_info):
                    tmp_file.append(tmp[0])
            self.file_list = tmp_file
        self.file_list.insert(0, "..")

        # it_can_be_display
        line = 0
        for _ in range(self.Y + 2, self.YParentMax - 3):
            line += 1
        self.model.window_source_item_it_can_be_display = line - 1
        self.model.window_source_ls_dir_item_number = len(self.file_list)

        #Put the Background color Blue
        self.Parent.bkgd(ord(' '), curses.color_pair(3))

        # Path Management
        label_dir = " " + os.getcwd() + " "
        label_dir = label_dir.replace(expanduser("~"), "~")
        if not self.XParentMax - 10 >= len(label_dir):
            label_dir = str(" ..." + label_dir[-int(self.XParentMax - 14):])
        self.Parent.addstr(
            0,
            self.X + 3,
            str(label_dir),
            curses.color_pair(4)
        )

        #Size / Position calculation
        x_pos_line_start = self.X + 1
        y_pos_titles = self.Y + 1
        size_collumn_width = 8
        mtime_collumn_width = 19
        name_collumn_width = self.XParentMax - (size_collumn_width + mtime_collumn_width + 2)

        #History arrow for navigate inside historty directory list
        self.model.window_source_history_dir_list_prev_object = clickable_sort_by_text(
            self.Parent,
            0,
            x_pos_line_start,
            "<",
            curses.color_pair(3)
        )
        self.model.window_source_history_dir_list_object = clickable_sort_by_text(
            self.Parent,
            0,
            self.XParentMax - 6,
            ".[^]",
            curses.color_pair(3)
        )
        self.model.window_source_history_dir_list_next_object = clickable_sort_by_text(
            self.Parent,
            0,
            self.XParentMax - 2,
           ">",
           curses.color_pair(3)
        )

        #Verify which short type is selected and display ('n) (,n) ('s) (,s) ('m) (,m)
        #Check if it have to display ('n) (,n)
        if self.model.window_source_sort_by_name == 1:
            if self.model.window_source_sort_name_order == 1:
                self.Parent.addstr(
                    y_pos_titles,
                    x_pos_line_start,
                    "'",
                    curses.color_pair(7) | curses.A_BOLD
                )
            else:
                self.Parent.addstr(
                    y_pos_titles,
                    x_pos_line_start,
                    ",",
                    curses.color_pair(7) | curses.A_BOLD
                )
            self.Parent.addstr(
                y_pos_titles,
                self.X + 2,
                str(self.model.window_source_sort_name_letter),
                curses.color_pair(7) | curses.A_BOLD
            )
        #Check if it have to display ('s) (,s)
        elif self.model.window_source_sort_by_size == 1:
            if self.model.window_source_sort_size_order == 1:
                self.Parent.addstr(
                    y_pos_titles,
                    x_pos_line_start,
                    "'",
                    curses.color_pair(7) | curses.A_BOLD
                )
            else:
                self.Parent.addstr(
                    y_pos_titles,
                    x_pos_line_start,
                    ",",
                    curses.color_pair(7) | curses.A_BOLD
                )
            self.Parent.addstr(
                y_pos_titles,
                self.X + 2,
                str(self.model.window_source_sort_size_letter),
                curses.color_pair(7) | curses.A_BOLD
            )
        #Check if it have to display ('m) (,m)
        elif self.model.window_source_sort_by_mtime == 1:
            if self.model.window_source_sort_mtime_order == 0:
                self.Parent.addstr(
                    y_pos_titles,
                    x_pos_line_start,
                    "'",
                    curses.color_pair(7) | curses.A_BOLD
                )
            else:
                self.Parent.addstr(
                    y_pos_titles,
                    x_pos_line_start,
                    ",",
                    curses.color_pair(7) | curses.A_BOLD
                )
            self.Parent.addstr(
                y_pos_titles,
                self.X + 2,
                str(self.model.window_source_sort_mtime_letter),
                curses.color_pair(7) | curses.A_BOLD
            )

        #Creat 3 clickable elements for "Name", "Size", "Modify Time"
        self.model.window_source_name_text_object = clickable_sort_by_text(
            self.Parent,
            y_pos_titles,
            ((self.XParentMax - mtime_collumn_width - size_collumn_width) / 2) - (len(self.name_text) / 2),
            self.name_text,
            curses.color_pair(7) | curses.A_BOLD
        )
        self.model.window_source_size_text_object = clickable_sort_by_text(
            self.Parent,
            y_pos_titles,
            ((self.XParentMax - mtime_collumn_width - size_collumn_width) + 1) + ((len(self.size_text) - 1) / 2),
            self.size_text,
            curses.color_pair(7) | curses.A_BOLD
        )
        self.model.window_source_mtime_text_object = clickable_sort_by_text(
            self.Parent,
            y_pos_titles,
            (self.XParentMax - mtime_collumn_width + 1) + ((len(str(self.mtime_text)) - 1) / 2) - 4,
            self.mtime_text,
            curses.color_pair(7) | curses.A_BOLD
            )
        #Creat 2 Vertical Lines for creat collumns for Name, Size and Modify Time

        self.Parent.vline(
            y_pos_titles,
            self.XParentMax - mtime_collumn_width,
            curses.ACS_VLINE,
            self.YParentMax - 3
        )
        self.Parent.vline(
            y_pos_titles,
            self.XParentMax - mtime_collumn_width - size_collumn_width,
            curses.ACS_VLINE,
            self.YParentMax - 3
        )
        count = 0
        # FOR qui occupe toute la fenetre avec des listes de fichiers
        for I in range(self.Y + 2, self.YParentMax - 3):

            if count < len(self.file_list):
                try:
                    file_info_list = get_file_info_list(
                        os.path.join(
                            self.dirname,
                            self.file_list[count + self.model.window_source_item_list_scroll],
                            self.model
                        )
                    )
                except:
                    file_info_list = get_file_info_list(
                        self.file_list[count + self.model.window_source_item_list_scroll],
                        self.model
                    )

                # Force the selected high color line to stay on the aviable box size
                if self.model.window_source_selected_item > self.model.window_source_item_it_can_be_display:
                    self.model.window_source_selected_item -= 1

                # Import Datas
                item_name_text = str(file_info_list[0])
                item_path_sys = str(file_info_list[1])
                item_size_text = str(file_info_list[2])
                item_time_text = str(file_info_list[3])

                # Special case of item_name_text text size , it have to be resize
                item_name_text = resize_text(item_name_text, name_collumn_width)

                # Draw the selected Line
                if self.model.window_source_selected_item == count:
                    # Paint the entire line with a hight light color
                    self.Parent.addstr(
                        I,
                        x_pos_line_start,
                        str(" " * int(self.XParentMax - 2)),
                        curses.color_pair(1)
                    )
                    # If that a file add a space character
                    self.model.window_source_selected_item_list_value = file_info_list
                    if os.path.isfile(item_path_sys):
                        self.Parent.addstr(
                            I,
                            x_pos_line_start,
                            str(" " + item_name_text),
                            curses.color_pair(1)
                        )
                    # If that a directory add a / character
                    else:
                        self.Parent.addstr(
                            I,
                            x_pos_line_start,
                            str("/" + item_name_text),
                            curses.color_pair(1)
                        )
                    # Draw the Size
                    self.Parent.addstr(
                        I,
                        (self.XParentMax - mtime_collumn_width - len(item_size_text)),
                        item_size_text,
                        curses.color_pair(1)
                    )
                    # Draw the Date
                    self.Parent.addstr(
                        I,
                        self.XParentMax - mtime_collumn_width + 1,
                        item_time_text,
                        curses.color_pair(1)
                    )
                    # Draw the 2 vertical lines with high light color
                    self.Parent.vline(
                        I,
                        self.XParentMax - mtime_collumn_width,
                        curses.ACS_VLINE,
                        1,
                        curses.color_pair(1)
                    )
                    self.Parent.vline(
                        I,
                        self.XParentMax - mtime_collumn_width - size_collumn_width,
                        curses.ACS_VLINE,
                        1,
                        curses.color_pair(1)
                    )
                # That is not the selected line
                else:
                    if os.path.isfile(item_path_sys):
                        # Give color to video file type
                        if item_path_sys.endswith(video_file_extensions):
                            self.Parent.addstr(
                                I,
                                x_pos_line_start,
                                str(" " + item_name_text),
                                curses.color_pair(8)
                            )
                            self.Parent.addstr(
                                I,
                                (self.XParentMax - mtime_collumn_width - len(item_size_text)),
                                item_size_text,
                                curses.color_pair(8)
                            )
                            self.Parent.addstr(
                                I,
                                self.XParentMax - mtime_collumn_width + 1,
                                item_time_text,
                                curses.color_pair(8)
                            )
                        # Else Give normal color
                        else:
                            self.Parent.addstr(
                                I,
                                x_pos_line_start,
                                str(" " + item_name_text),
                                curses.color_pair(3)
                            )
                            self.Parent.addstr(
                                I,
                                (self.XParentMax - mtime_collumn_width - len(item_size_text)),
                                item_size_text,
                                curses.color_pair(3)
                            )
                            self.Parent.addstr(
                                I,
                                self.XParentMax - mtime_collumn_width+ 1,
                                item_time_text,
                                curses.color_pair(3)
                            )
                    # It's a Directory, give BOLD attribute
                    else:
                        self.Parent.addstr(
                            I,
                            x_pos_line_start,
                            str("/" + item_name_text),
                            curses.color_pair(3) | curses.A_BOLD
                        )
                        self.Parent.addstr(
                            I,
                            (self.XParentMax - mtime_collumn_width - len(item_size_text)),
                            item_size_text,
                            curses.color_pair(3) | curses.A_BOLD
                        )
                        self.Parent.addstr(
                            I,
                            self.XParentMax - mtime_collumn_width + 1,
                            item_time_text,
                            curses.color_pair(3) | curses.A_BOLD
                            )
            count += 1

        self.Parent.hline(
            self.YParentMax - 3,
            x_pos_line_start,
            curses.ACS_HLINE,
            self.XParentMax - 2
        )
        # If the item value is '..' it use Directory setting
        if self.model.window_source_selected_item_list_value[0] == "..":
            self.Parent.addstr(
                self.YParentMax - 2,
                x_pos_line_start,
                self.model.window_source_rep_sup_text,
                curses.color_pair(3)
            )
        else:
            self.Parent.addstr(
                self.YParentMax - 2,
                x_pos_line_start,
                resize_text(self.model.window_source_selected_item_list_value[0], self.XParentMax-2),
                curses.color_pair(3)
            )
        # Add Disk usage
        disk_space_line = disk_usage(os.getcwd())
        self.Parent.addstr(
            self.YParentMax - 1,
            self.XParentMax - 2 - len(disk_space_line),
            disk_space_line,
            curses.color_pair(3)
        )
        #Test if the history widget should be display
        if self.model.display_history_menu:
            self.model.history_dialog_box = creat_history_box(
                self.model,
                self.Parent,
                0,
                self.XParentMax - 6,
                self.model.display_history_text,
                curses.color_pair(4)
            )
