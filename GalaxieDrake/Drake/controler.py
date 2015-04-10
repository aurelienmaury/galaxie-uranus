'''
Created on 4 avr. 2015

@author: Tuxa - www.rtnp.org
'''
import curses
import os


class controler_class():
    def __init__(self, screen, viewer, model):
        self.model = model
        self.viewer = viewer
        self.screen = screen
        self.message_events = {
            ord("\t"): lambda: self.on_message("The User Pressed TAB"),
            ord("q"): lambda: self.on_message("The User Pressed Q"),
            curses.KEY_UP: lambda: self.on_message("The User Pressed UP"),
            curses.KEY_DOWN: lambda: self.on_message("The User Pressed DOWN"),
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

        while True:
            event = self.screen.getch()

            # Control of Source Box
            if self.model.active_window == 2:
                if event == curses.KEY_UP:
                    if not self.model.window_source_selected_item == 0:
                        self.model.window_source_selected_item -= 1
                    else:
                        if not self.model.window_source_item_list_scroll == 0:
                            self.model.window_source_item_list_scroll -= 1
                elif event == curses.KEY_DOWN:
                    if not self.model.window_source_item_it_can_be_display == self.model.window_source_selected_item:
                        if not self.model.window_source_selected_item == self.model.window_source_lsdir_item_number - 1:
                            self.model.window_source_selected_item += 1
                    else:
                        if self.model.window_source_item_list_scroll + self.model.window_source_item_it_can_be_display + 1 < self.model.window_source_lsdir_item_number <= self.model.window_source_lsdir_item_number:
                            self.model.window_source_item_list_scroll += 1

                elif event == curses.KEY_ENTER or event == ord("\n"):
                    if os.path.isdir(self.model.window_source_selected_item_list_value[0]):
                        os.chdir(self.model.window_source_selected_item_list_value[0])
                        self.model.window_source_pwd = os.getcwd()
                        self.model.window_source_selected_item = 0
                        self.model.window_source_item_list_scroll = 0
                    else:
                        filename = os.path.join(os.getcwd(), self.model.window_source_selected_item_list_value[0])
                        self.viewer.display_message(filename)
                elif event == ord("n"):
                        self.model.window_source_sort_by_name = 1
                        self.model.window_source_sort_by_size = 0
                        self.model.window_source_sort_by_time = 0
                        self.model.window_source_sort_name_order = not self.model.window_source_sort_name_order
                elif event == ord("s"):
                        self.model.window_source_sort_by_name = 0
                        self.model.window_source_sort_by_size = 1
                        self.model.window_source_sort_by_time = 0
                        self.model.window_source_sort_size_order = not self.model.window_source_sort_size_order
                elif event == ord("t"):
                        self.model.window_source_sort_by_name = 0
                        self.model.window_source_sort_by_size = 0
                        self.model.window_source_sort_by_time = 1
                        self.model.window_source_sort_time_order = not self.model.window_source_sort_time_order
                elif event == curses.KEY_MOUSE:
                    #mouse_state = curses.getmouse()[4]
                    mouse_state = curses.getmouse()
                    if self.model.window_source_file_selector.MouseClicked(mouse_state):
                            #action = Button.Label
                            self.viewer.display_message("action")
                    if mouse_state[4] & curses.BUTTON4_PRESSED:
                        if not self.model.window_source_selected_item == 0:
                            self.model.window_source_selected_item -= 1
                        else:
                            if not self.model.window_source_item_list_scroll == 0:
                                self.model.window_source_item_list_scroll -= 1
                    if mouse_state[4] & curses.BUTTON2_PRESSED:
                        if not self.model.window_source_item_it_can_be_display == self.model.window_source_selected_item:
                            if not self.model.window_source_selected_item == self.model.window_source_lsdir_item_number - 1:
                                self.model.window_source_selected_item += 1
                        else:
                            if self.model.window_source_item_list_scroll + self.model.window_source_item_it_can_be_display + 1 < self.model.window_source_lsdir_item_number <= self.model.window_source_lsdir_item_number:
                                self.model.window_source_item_list_scroll += 1

            # Control of Quit Box
            action = ""
            if self.model.active_window == 10:
                for Button in [self.model.window_quit_YesButton, self.model.window_quit_NoButton]:
                    if Button.KeyPressed(event):
                        action = Button.Label
                        self.viewer.display_message(action)
                # Handle mouse-events:
                if event == curses.KEY_MOUSE:
                    mouseevent = curses.getmouse()
                    for Button in [self.model.window_quit_YesButton, self.model.window_quit_NoButton]:
                        if Button.MouseClicked(mouseevent):
                            action = Button.Label
                            self.viewer.display_message(action)
                elif event == curses.KEY_RIGHT or event == curses.KEY_LEFT:
                    self.model.window_quit_yesno = not self.model.window_quit_yesno
                elif event == curses.KEY_ENTER or event == ord("\n"):
                    if self.model.window_quit_yesno == 1:
                        action = "Yes"
                    if not self.model.window_quit_yesno == 1:
                        action = "No"
                elif event == 27:
                    self.screen.nodelay(1)
                    n = screen.getch()
                    if n == -1:
                        # Escape was pressed
                        action = "No"
                    self.screen.nodelay(0)
            if event in self.message_events:
                self.message_events[event]()
            elif event in self.window_change_events:
                self.window_change_events[event]()
            elif event == curses.KEY_F10:
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