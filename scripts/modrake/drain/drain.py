
import curses
from .components import *
from .events import *

class App:
    def __init__(self, app_name, screen):
        self.panels = [
            Panel("Source", curses.KEY_F1),
            Panel("Summary", curses.KEY_F2),
            YesNoDialog(self, "Exit", "So you think you can leave?", curses.KEY_F3)
        ]
        self.handlers = {}
        self.app_name = app_name
        self.event_queue = EventQueue()
        self.max_button_number = 10
        self.screen = screen
        self.active_panel = 0
        self.current_dialog = -1
        self.dialog_ongoing = False
        self.started = False
        self._init_curses()

    def _init_curses(self):
        self.screen.clear()
        self.screen.nodelay(1)
        curses.curs_set(0)

        self.screen.keypad(1)
        curses.mousemask(1)
        self._init_colors()

    def _init_colors(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_CYAN)

    def shutdown(self):
        self.started = False
        curses.endwin()

    def activate_panel(self, activation_key):
        for index, panel in enumerate(self.panels):
            if activation_key == panel.activation_key:
                if isinstance(panel, YesNoDialog):
                    self.dialog_ongoing = True
                    self.current_dialog = index
                else:
                    self.active_panel = index
                return True
        return False

    def run(self):
        self.started = True
        self.event_queue.push(Event(self.panels[0].activation_key))

        while self.started:
            if self.event_queue.has_events():
                new_event = self.event_queue.pop()
                self.display_message("KEY: "+str(new_event.value))
                handled_by_panel = self.activate_panel(new_event.value)

                if not handled_by_panel:
                    if self.dialog_ongoing:
                        self.panels[self.current_dialog].handle_event(new_event)
                    else:
                        self.panels[self.active_panel].handle_event(new_event)

                self.refresh()

            input_event = self.screen.getch()

            if input_event != -1:
                self.event_queue.push(Event(input_event))

    def finish_dialog(self):
        self.dialog_ongoing = False

    def refresh(self):
        self.display_top_menu()
        self.panels[self.active_panel].display_on(self.screen)
        if self.dialog_ongoing:
            self.panels[self.current_dialog].display_on(self.screen)
        self.display_bottom_menu()
        self.screen.refresh()

    def display_top_menu(self):
        num_lines, num_cols = self.screen.getmaxyx()
        # Creat a sub window
        top_menu_box = self.screen.subwin(0, 0, 0, 0)
        top_menu_box_num_lines, top_menu_box_num_cols = top_menu_box.getmaxyx()
        if curses.has_colors():
            top_menu_box.addstr(0, 0, str(" " * int(top_menu_box_num_cols)), curses.color_pair(1))
            top_menu_box.bkgdset(ord(' '), curses.color_pair(1))

        top_menu_box.addstr(0, 0, self.app_name)
        top_menu_box.refresh()

    def display_bottom_menu(self):
        item_list = self.panels
        req_button_number = len(item_list)

        if req_button_number > self.max_button_number:
            req_button_number = self.max_button_number

        num_lines, num_cols = self.screen.getmaxyx()

        available_per_item = int((num_cols / req_button_number) - 3)
        max_visible = 1

        for index in range(1, req_button_number + 1):
            cumul = 0
            for U in range(0, max_visible):
                cumul = cumul + len(str(item_list[U]))
            if num_cols - 1 > cumul + int((3 * max_visible) + 1):
                # Put the entire line with curses.color_pair(1))
                self.screen.addstr(num_lines - 1, 0, str(" " * int(num_cols - 1)), curses.color_pair(1))
                max_visible = max_visible + 1

        self.screen.addstr(num_lines - 1, 0, "", curses.color_pair(2))

        for count in range(0, max_visible - 1):
            if len(str(count + 1)) == 2:
                self.screen.addstr(str(count + 1), curses.color_pair(226) | curses.A_BOLD)
                self.screen.addstr(item_list[count].title, curses.color_pair(1))
                spacing = (available_per_item - len(item_list[count]) - 1)
                self.screen.addstr(str(" " * int(spacing)), curses.color_pair(1))
            elif len(str(count + 1)) == 1:
                self.screen.addstr(" ", curses.COLOR_WHITE | curses.COLOR_BLACK)
                self.screen.addstr(str(count + 1).title(), curses.color_pair(2) | curses.A_BOLD)
                self.screen.addstr(item_list[count].title, curses.color_pair(1))
                spacing = available_per_item - len(item_list[count].title)
                self.screen.addstr(str(" " * int(spacing)), curses.color_pair(1))


    def display_message(self, message):
        screen_num_lines, screen_num_cols = self.screen.getmaxyx()
        display_message_subwin = self.screen.subwin(1, screen_num_cols - 1, screen_num_lines - 2, 0)
        display_message_subwin_num_lines, display_message_subwin_num_cols = display_message_subwin.getmaxyx()
        if curses.has_colors():
            display_message_subwin.addstr(0, 0, str(" " * int(display_message_subwin_num_cols - 1)))
            display_message_subwin.insstr(0, display_message_subwin_num_cols - 1, " ")
            display_message_subwin.addstr(0, 0, str(message))
        display_message_subwin.refresh()
        self.screen.refresh()
