#!/usr/bin/python

'''
Created on 4 avr. 2015

@author: Tuxa - www.rtnp.org
'''
import curses
import os
import random
import threading
import time
import psutil


compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
from Drake.transcoder import HandBrake
from Drake.events import *
from Drake.taskspooler import TaskSpooler
from Drake.utility import display_up_time

class controler_class():
    def __init__(self, screen, viewer, model):
        self.model = model
        self.viewer = viewer
        self.screen = screen
        self.event_queue = EventQueue()

        # Creat a TaskSpooler objec tfor dialog with "tsp"
        self.model.tsp = TaskSpooler()
        # Init the list queue for the frist time
        self.model.window_queue_tasks_list = self.model.tsp.get_list()
        #Frist init for the Main_Panel
        self.model.cpu_percent_list = psutil.cpu_percent(interval=1, percpu=True)
        self.model.taskspooler_summary_list = self.model.tsp.get_summary_info()

        # Enable TaskSpooler check
        timer_thread_get_taskspooler_tasks_list = threading.Thread(target=self.refresh_data)
        timer_thread_get_taskspooler_tasks_list.daemon = True
        timer_thread_get_taskspooler_tasks_list.start()

        # Enable Hint Splash
        #timer_thread_splash_hints = threading.Thread(target=self.splash_hints)
        #timer_thread_splash_hints.daemon = True
        #timer_thread_splash_hints.start()

        self.message_events = {
            ord("\t"): lambda: self.on_message("The User Pressed TAB"),
            ord("q"): lambda: self.on_message("The User Pressed Q"),
            curses.KEY_UP: lambda: self.on_message("The User Pressed UP"),
            #curses.KEY_DOWN: lambda: self.on_message("The User Pressed DOWN"),
            curses.KEY_LEFT: lambda: self.on_message("The User Pressed LEFT"),
            curses.KEY_RIGHT: lambda: self.on_message("The User Pressed RIGHT"),
            curses.KEY_ENTER: lambda: self.on_message("The User Pressed ENTER"),
            curses.KEY_IC: lambda: self.on_message("The User Pressed IC"),
        }
        self.window_change_events = {
            curses.KEY_F1: lambda: self.on_window_change(1, "The User Pressed F1"),
            curses.KEY_F2: lambda: self.on_window_change(2, "The User Pressed F2"),
            curses.KEY_F3: lambda: self.on_window_change(3, "The User Pressed F3"),
            curses.KEY_F4: lambda: self.on_window_change(4, "The User Pressed F4"),
            curses.KEY_F5: lambda: self.on_window_change(5, "The User Pressed F5"),
            curses.KEY_F6: lambda: self.on_window_change(6, "The User Pressed F6"),
            curses.KEY_F7: lambda: self.on_window_change(7, "The User Pressed F7"),
            curses.KEY_F8: lambda: self.on_window_change(8, "The User Pressed F8"),
            curses.KEY_F9: lambda: self.on_window_change(9, "The User Pressed F9")
        }

        # input_event = ""
        while True:
            # self.screen.nodelay(1)

            # if self.event_queue.has_events():
            #    new_event = self.event_queue.pop()
            #    input_event = new_event.value
            # else:
            #    input_event = self.screen.getch()
            #    if input_event != -1:
            #        self.event_queue.push(Event(input_event))
            # self.screen.nodelay(0)

            input_event = self.screen.getch()
            if self.model.active_window == 0:
                a = None
            # Help
            if self.model.active_window == 1:
                if input_event == 27:
                    self.control_echap(input_event)
                elif input_event == curses.KEY_F10:
                    input_event = None
                    self.model.active_window = self.model.last_window

            # Control of Source Box
            if self.model.active_window == 2 and not self.model.display_history_menu == 1:
                if input_event == 27:
                    self.control_echap(input_event)
                elif input_event == curses.KEY_F10:
                    input_event = None
                    self.model.active_window = self.model.last_window
                elif input_event == curses.KEY_UP:
                    if not self.model.window_source_selected_item == 0:
                        self.model.window_source_selected_item -= 1
                    else:
                        if not self.model.window_source_item_list_scroll == 0:
                            self.model.window_source_item_list_scroll -= 1
                elif input_event == curses.KEY_DOWN:
                    if not self.model.window_source_item_it_can_be_display == self.model.window_source_selected_item:
                        if not self.model.window_source_selected_item == self.model.window_source_ls_dir_item_number - 1:
                            self.model.window_source_selected_item += 1
                    else:
                        if self.model.window_source_item_list_scroll + self.model.window_source_item_it_can_be_display + 1 < self.model.window_source_ls_dir_item_number <= self.model.window_source_ls_dir_item_number:
                            self.model.window_source_item_list_scroll += 1

                elif input_event == curses.KEY_ENTER or input_event == ord("\n"):

                    if os.path.isdir(self.model.window_source_selected_item_list_value[0]):
                        os.chdir(self.model.window_source_selected_item_list_value[0])
                        self.model.window_source_pwd = os.getcwd()
                        self.model.window_source_selected_item = 0
                        self.model.window_source_item_list_scroll = 0

                        found = 0
                        for I in model.window_source_history_dir_list:
                            if I == os.getcwd():
                                found = 1
                        if not found == 1:
                            self.model.window_source_history_dir_list.append(os.getcwd())

                    else:
                        filename = os.path.join(os.getcwd(), self.model.window_source_selected_item_list_value[0])
                        if filename.endswith(self.model.video_file_extensions):
                            self.viewer.display_message("Scaning ... ")
                            self.model.transcoder = HandBrake(filename, max_height=720, enable_multi_language=0,
                                                              lang1='fra', lang2='eng')
                            self.model.active_window = 3
                            self.viewer.display_message("")
                        else:
                            self.viewer.display_message("Filename is not a video file ...")

                elif input_event == ord("n"):
                    self.model.window_source_sort_by_name = 1
                    self.model.window_source_sort_by_size = 0
                    self.model.window_source_sort_by_mtime = 0
                    self.model.window_source_sort_name_order = not self.model.window_source_sort_name_order
                elif input_event == ord("s"):
                    self.model.window_source_sort_by_name = 0
                    self.model.window_source_sort_by_size = 1
                    self.model.window_source_sort_by_mtime = 0
                    self.model.window_source_sort_size_order = not self.model.window_source_sort_size_order
                elif input_event == ord("t"):
                    self.model.window_source_sort_by_name = 0
                    self.model.window_source_sort_by_size = 0
                    self.model.window_source_sort_by_mtime = 1
                    self.model.window_source_sort_mtime_order = not self.model.window_source_sort_mtime_order
                elif input_event == ord("h"):
                    self.on_message("The User selected history list")
                    self.model.display_history_menu = not self.model.display_history_menu
                elif input_event == curses.KEY_MOUSE:
                    mouse_state = curses.getmouse()
                    if self.model.window_source_history_dir_list_prev_object.mouse_clicked(mouse_state):
                        if not self.model.history_menu_selected_item == 0:
                            self.model.history_menu_selected_item -= 1

                        if os.path.isdir(
                                self.model.window_source_history_dir_list[self.model.history_menu_selected_item]):
                            os.chdir(self.model.window_source_history_dir_list[self.model.history_menu_selected_item])
                            self.model.window_source_pwd = os.getcwd()
                            self.model.window_source_selected_item = 0
                            self.model.window_source_item_list_scroll = 0
                        self.on_message("History prev")
                    if self.model.window_source_history_dir_list_next_object.mouse_clicked(mouse_state):
                        if len(self.model.window_source_history_dir_list) > self.model.history_menu_selected_item + 1:
                            self.model.history_menu_selected_item += 1
                            if os.path.isdir(
                                    self.model.window_source_history_dir_list[self.model.history_menu_selected_item]):
                                os.chdir(
                                    self.model.window_source_history_dir_list[self.model.history_menu_selected_item])
                                self.model.window_source_pwd = os.getcwd()
                                self.model.window_source_selected_item = 0
                                self.model.window_source_item_list_scroll = 0

                        self.on_message("History next")
                    if self.model.window_source_history_dir_list_object.mouse_clicked(mouse_state):
                        self.on_message("The User selected history list")
                        self.model.display_history_menu = not self.model.display_history_menu
                    if self.model.window_source_name_text_object.mouse_clicked(mouse_state):
                        self.model.window_source_sort_by_name = 1
                        self.model.window_source_sort_by_size = 0
                        self.model.window_source_sort_by_mtime = 0
                        self.model.window_source_sort_name_order = not self.model.window_source_sort_name_order
                    if self.model.window_source_size_text_object.mouse_clicked(mouse_state):
                        self.model.window_source_sort_by_name = 0
                        self.model.window_source_sort_by_size = 1
                        self.model.window_source_sort_by_mtime = 0
                        self.model.window_source_sort_size_order = not self.model.window_source_sort_size_order
                    if self.model.window_source_mtime_text_object.mouse_clicked(mouse_state):
                        self.model.window_source_sort_by_name = 0
                        self.model.window_source_sort_by_size = 0
                        self.model.window_source_sort_by_mtime = 1
                        self.model.window_source_sort_mtime_order = not self.model.window_source_sort_mtime_order

                    if mouse_state[4] & curses.BUTTON4_PRESSED:
                        if not self.model.window_source_selected_item == 0:
                            self.model.window_source_selected_item -= 1
                        else:
                            if not self.model.window_source_item_list_scroll == 0:
                                self.model.window_source_item_list_scroll -= 1
                    if mouse_state[4] & curses.BUTTON2_PRESSED:
                        if not self.model.window_source_item_it_can_be_display == self.model.window_source_selected_item:
                            if not self.model.window_source_selected_item == self.model.window_source_ls_dir_item_number - 1:
                                self.model.window_source_selected_item += 1
                        else:
                            if self.model.window_source_item_list_scroll + self.model.window_source_item_it_can_be_display + 1 < self.model.window_source_ls_dir_item_number <= self.model.window_source_ls_dir_item_number:
                                self.model.window_source_item_list_scroll += 1
            # When history i display enable special shortcut
            elif self.model.display_history_menu == 1:
                if input_event == 27:
                    self.screen.nodelay(1)
                    n = screen.getch()
                    if n == -1:
                        # Escape was pressed
                        self.model.display_history_menu = not self.model.display_history_menu
                    self.screen.nodelay(0)
                elif input_event == curses.KEY_UP:
                    if not self.model.history_menu_selected_item == 0:
                        self.model.history_menu_selected_item -= 1
                    else:
                        if not self.model.history_menu_item_list_scroll == 0:
                            self.model.history_menu_item_list_scroll -= 1
                elif input_event == curses.KEY_DOWN:
                    if not self.model.history_menu_can_be_display == self.model.history_menu_selected_item \
                            and not self.model.history_menu_selected_item + 1 == len(
                                self.model.window_source_history_dir_list) \
                            and not len(self.model.window_source_history_dir_list) == 0:
                        self.model.history_menu_selected_item += 1
                    else:
                        if self.model.history_menu_item_list_scroll + self.model.history_menu_can_be_display < self.model.history_menu_item_number + 1:
                            self.model.history_menu_item_list_scroll += 1
                elif input_event == curses.KEY_ENTER or input_event == ord("\n"):
                    self.model.display_history_menu = not self.model.display_history_menu
                    if os.path.isdir(self.model.history_menu_selected_item_value):
                        os.chdir(self.model.history_menu_selected_item_value)
                        self.model.window_source_pwd = os.getcwd()
                        self.model.window_source_selected_item = 0
                        self.model.window_source_item_list_scroll = 0
                elif input_event == ord("h"):
                    self.on_message("The User selected history list")
                    self.model.display_history_menu = not self.model.display_history_menu

            # Summary
            if self.model.active_window == 3:
                if input_event == 27:
                    self.control_echap(input_event)
                elif input_event == curses.KEY_F10:
                    input_event = None
                    self.model.active_window = self.model.last_window
                elif input_event == curses.KEY_ENTER or input_event == ord("\n"):
                    self.model.transcoder.encode()
                    self.screen.clear()

            # Control of Queue Box Manager
            if self.model.active_window == 4:
                if input_event == 27:
                    self.control_echap(input_event)
                elif input_event == curses.KEY_F8:
                    input_event = None
                    self.model.tsp.remove_task(jobid=self.model.window_queue_selected_item_list_value[0])
                    self.viewer.refresh_screen(self.model.active_window)
                elif input_event == curses.KEY_F10:
                    input_event = None
                    self.model.active_window = self.model.last_window
                elif input_event == curses.KEY_UP:
                    if not self.model.window_queue_selected_item == 0:
                        self.model.window_queue_selected_item -= 1
                    else:
                        if not self.model.window_queue_item_list_scroll == 0:
                            self.model.window_queue_item_list_scroll -= 1
                elif input_event == curses.KEY_DOWN:
                    if not self.model.window_queue_item_it_can_be_display == self.model.window_queue_selected_item + 1\
                            and not self.model.window_queue_selected_item + 1 == len(
                                self.model.window_queue_tasks_list) \
                            and not len(self.model.window_queue_tasks_list) == 0:
                        self.model.window_queue_selected_item += 1
                    else:
                        #self.on_message("window_queue_item_it_can_be_display: " + str(self.model.window_queue_item_it_can_be_display))
                        if self.model.window_queue_item_list_scroll + self.model.window_queue_item_it_can_be_display < self.model.window_queue_item_number:
                            self.model.window_queue_item_list_scroll += 1

            # Control of Quit Box
            action = ""
            if self.model.active_window == 10:
                for Button in [self.model.window_quit_YesButton, self.model.window_quit_NoButton]:
                    if Button.key_pressed(input_event):
                        action = Button.Label
                        self.viewer.display_message(action)
                # Handle mouse-events:
                if input_event == curses.KEY_MOUSE:
                    mouse_event = curses.getmouse()
                    for Button in [self.model.window_quit_YesButton, self.model.window_quit_NoButton]:
                        if Button.mouse_clicked(mouse_event):
                            action = Button.Label
                            self.viewer.display_message(action)
                elif input_event == curses.KEY_RIGHT or input_event == curses.KEY_LEFT:
                    self.model.window_quit_yesno = not self.model.window_quit_yesno
                elif input_event == ord("\t"):
                    self.model.window_quit_yesno = not self.model.window_quit_yesno
                elif input_event == curses.KEY_ENTER or input_event == ord("\n"):
                    if self.model.window_quit_yesno == 1:
                        action = "Yes"
                    if not self.model.window_quit_yesno == 1:
                        action = "No"
                elif input_event == 27:
                    self.screen.nodelay(1)
                    n = screen.getch()
                    if n == -1:
                        # Escape was pressed
                        action = "No"
                    self.screen.nodelay(0)
            if input_event in self.message_events:
                self.message_events[input_event]()
            elif input_event in self.window_change_events:
                self.window_change_events[input_event]()
            elif input_event == curses.KEY_F10:
                if self.model.active_window == 0:
                    self.model.last_window = self.model.active_window
                    self.model.active_window = 10
            elif action[:1] == "Y":
                self.on_message("The User selected " + action)
                break
            elif action[:1] == "N":
                self.model.window_quit_yesno = 1
                self.model.active_window = self.model.last_window
                self.on_message("The User selected " + action)
            else:
                pass
            self.viewer.refresh_screen(self.model.active_window)

    def control_echap(self, input_event):
        if input_event == 27:
            self.screen.nodelay(1)
            n = self.screen.getch()
            if n == -1:
                # Escape was pressed
                if self.model.active_window == self.model.last_window:
                    self.model.active_window = 0
                else:
                    self.model.active_window = self.model.last_window
            self.screen.nodelay(0)

    def on_message(self, message):
        self.viewer.display_message(message)
        self.model.last_message = message

    def on_info(self, info):
        self.viewer.display_info(info)
        self.model.last_info = info

    def on_window_change(self, id, message):
        self.on_message(message)
        self.model.last_window = self.model.active_window
        self.model.active_window = id

    def display_a_hint(self):
        self.on_info(self.model.hint_pre_message_text + random.choice(self.model.hint_list))

    def splash_hints(self, interval=10):
        next_call = time.time()
        while True:
            next_call += interval
            time.sleep(next_call - time.time())
            self.display_a_hint()

    def refresh_data(self, interval=3):
        next_call = time.time()
        while True:
            next_call += interval
            time.sleep(next_call - time.time())
            # Main Panel importation data
            if self.model.active_window == 0:
                self.model.up_time = display_up_time()
                self.model.cpu_percent_list = psutil.cpu_percent(interval=1, percpu=True)
                self.model.taskspooler_summary_list = self.model.tsp.get_summary_info()
                self.viewer.display_method_by_window[self.model.active_window]()
                self.model.main_panel_sub_win.refresh()
            elif self.model.active_window == 4:
                if not sorted(self.model.tsp.get_list()) == sorted(self.model.window_queue_tasks_list):
                    self.model.window_queue_tasks_list = self.model.tsp.get_list()
                    self.model.taskspooler_summary_list = self.model.tsp.get_summary_info()
                    self.viewer.display_method_by_window[self.model.active_window]()
                    self.model.window_queue_sub_win.refresh()

