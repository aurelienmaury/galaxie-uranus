'''
Created on 4 avr. 2015

@author: tuxa
'''
import curses
from .components import CursesButton
from .components import FileSelect


class viewer_class():
    def __init__(self, bottom_menu, screen, model):
        self.screen = screen
        self.model = model
        self.init_curses()
        self.init_colors()
        self.screen.keypad(1)
        self.screen.clear()

        self.max_button_number = 10
        self.bottom_menu = bottom_menu
        self.display_method_by_window = {
            1: lambda: self.display_full_box("Help"),
            2: lambda: self.display_source_box("Select a source file to encode:"),
            3: lambda: self.display_full_box("Summary"),
            4: lambda: self.display_full_box("Video"),
            5: lambda: self.display_full_box("Audio"),
            8: lambda: self.display_tags_box("Tags"),
        }
        self.display_top_menu()
        self.display_method_by_window[self.model.active_window]()
        self.display_bottom_button()

        screen.refresh()

    def init_curses(self):
        curses.curs_set(0)
        curses.mousemask(-1)

    def init_colors(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
        # Dialog Windows Buttons
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_CYAN)
        # Dialog File Selection
        curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLUE)
        curses.init_pair(8, curses.COLOR_GREEN, curses.COLOR_BLUE)
        curses.init_pair(9, curses.COLOR_RED, curses.COLOR_BLUE)

    def display_full_box(self, title):
        num_lines, _ = self.screen.getmaxyx()
        # Creat a sub window
        full_box = self.screen.subwin(num_lines - 4, 0, 1, 0)
        self_num_lines, selft_num_cols = full_box.getmaxyx()
        # Put the Background color
        if curses.has_colors():
            for I in range(1, self_num_lines - 1):
                full_box.addstr(I, 1, str(" " * int(selft_num_cols - 2)), curses.color_pair(3))
            full_box.bkgdset(ord(' '), curses.color_pair(3))
        full_box.box()
        full_box.addstr(0, 1, title)
        full_box.refresh()


    def refresh_screen(self, active_window_to_display):
        self.display_top_menu()

        if active_window_to_display in self.display_method_by_window:
            self.display_method_by_window[active_window_to_display]()
        elif active_window_to_display == 10:
            self.display_quit_box(self.model.window_quit_yesno)
        self.display_info(str(self.model.last_info))
        self.display_message(str(self.model.last_message))

        self.display_bottom_button()

        self.screen.refresh()

    def display_top_menu(self):
        app_info_label = str("  " + self.model.app_name + "-" + self.model.app_version)
        top_menu_box = self.screen.subwin(0, 0, 0, 0)
        _, top_menu_box_num_cols = top_menu_box.getmaxyx()
        if curses.has_colors():
            top_menu_box.addstr(0, 0, str(" " * int(top_menu_box_num_cols)), curses.color_pair(1))
            top_menu_box.bkgdset(ord(' '), curses.color_pair(1))

        top_menu_box.addstr(0, 0, "  File     Queue     View     Help")
        top_menu_box.addstr(0, (top_menu_box_num_cols - 1) - len(app_info_label[:-1]), app_info_label[:-1], curses.color_pair(1))
        top_menu_box.insstr(0, top_menu_box_num_cols - 1, app_info_label[-1:], curses.color_pair(1))
        top_menu_box.refresh()

    def display_message(self, message):
        self.model.last_message = message
        screen_num_lines, screen_num_cols = self.screen.getmaxyx()
        display_message_subwin = self.screen.subwin(1, screen_num_cols - 1, screen_num_lines - 2, 0)
        _, display_message_subwin_num_cols = display_message_subwin.getmaxyx()
        if curses.has_colors():
            display_message_subwin.insstr(0, 0, str(" " * int(display_message_subwin_num_cols)), curses.color_pair(2))
            if len(message) >= display_message_subwin_num_cols - 1:
                start, end = message[:display_message_subwin_num_cols - 1], message[display_message_subwin_num_cols - 1:]
                display_message_subwin.addstr(0, 0, str(start))
                display_message_subwin.insstr(0, display_message_subwin_num_cols - 1, str(end[:1]))
            else:
                display_message_subwin.addstr(0, 0, str(message))
        display_message_subwin.refresh()

    def display_info(self, message):
        self.model.last_info = message
        screen_num_lines, screen_num_cols = self.screen.getmaxyx()
        display_info_subwin = self.screen.subwin(1, screen_num_cols, screen_num_lines - 3, 0)
        _, display_info_subwin_num_cols = display_info_subwin.getmaxyx()
        if curses.has_colors():
            display_info_subwin.insstr(0, 0, str(" " * int(display_info_subwin_num_cols)), curses.color_pair(2))
            if len(message) >= display_info_subwin_num_cols - 1:
                start, end = message[:display_info_subwin_num_cols - 1], message[display_info_subwin_num_cols - 1:]
                display_info_subwin.addstr(0, 0, str(start))
                display_info_subwin.insstr(0, display_info_subwin_num_cols - 1, str(end[:1]))
            else:
                display_info_subwin.addstr(0, 0, str(message))
        display_info_subwin.refresh()

    def display_bottom_button(self):
        item_list = self.model.bottom_button_list
        labels_end_coord = ['','','','','','','','','','','','']
        screen_num_lines, _ = self.screen.getmaxyx()
        bottom_menu_box = self.screen.subwin(0, 0, screen_num_lines - 1, 0)
        _, bottom_menu_box_num_cols = bottom_menu_box.getmaxyx()
        bottom_menu_box_num_cols -= 1
        req_button_number = len(item_list) + 1


        pos = 0
        if bottom_menu_box_num_cols < req_button_number * 7:
            for i in range(0, req_button_number):
                if pos + 7 <= bottom_menu_box_num_cols:
                    pos += 7
                labels_end_coord[i] = pos
        else:
            dv = bottom_menu_box_num_cols / req_button_number + 1
            md = bottom_menu_box_num_cols % req_button_number + 1
            i = 0
            for i in range(0, req_button_number / 2):
                pos += dv
                if req_button_number / 2 - 1 - i < md / 2:
                    pos += 1
                labels_end_coord[i] = pos
            for i in range(i+1, req_button_number):
                pos += dv
                if req_button_number - 1 - i < (md + 1) / 2:
                    pos += 1
                labels_end_coord[i] = pos

        if req_button_number > self.max_button_number:
            req_button_number = self.max_button_number

        aviable_per_item = int(bottom_menu_box_num_cols - 1 / req_button_number)

        # Size Bug it crash about display size, by reduse the number of button it can be display
        max_can_be_display = 1
        for I in range(1, req_button_number + 1):
            cumul = 0
            for U in range(0, max_can_be_display):
                cumul = cumul + len(str(item_list[U]))
            if bottom_menu_box_num_cols - 1 > cumul + int((3 * max_can_be_display) - 0):
                max_can_be_display = max_can_be_display + 1

        count = 0

        bottom_menu_box.addstr(0, 0, str(" " * int(bottom_menu_box_num_cols)), curses.color_pair(1))
        bottom_menu_box.insstr(0, bottom_menu_box_num_cols - 1, " ", curses.color_pair(1))
        bottom_menu_box.addstr(0, 0, "")
        for num in range(0, max_can_be_display-1):
            if count == 0:
                bottom_menu_box.addstr(0, 0, "")
                bottom_menu_box.addstr(0, 0, " ", curses.COLOR_WHITE | curses.COLOR_BLACK)
                bottom_menu_box.addstr(str(count+1), curses.COLOR_WHITE | curses.COLOR_BLACK)
                bottom_menu_box.addstr(str(item_list[count]), curses.color_pair(1))

            elif 1 <= count < 9:
                bottom_menu_box.addstr(0, (labels_end_coord[count-1] + 0), " ", curses.COLOR_WHITE | curses.COLOR_BLACK)
                bottom_menu_box.addstr(str(count+1), curses.COLOR_WHITE | curses.COLOR_BLACK)
                bottom_menu_box.addstr(str(item_list[count]), curses.color_pair(1))
            elif count >= 9:
                a=1
                bottom_menu_box.addstr(0, (labels_end_coord[count-1] + 1), str(count + 1),
                                       curses.COLOR_WHITE | curses.COLOR_BLACK)
                bottom_menu_box.addstr(item_list[count], curses.color_pair(1))
            count += 1
        bottom_menu_box.refresh()



    def display_tags_box(self, window_name):
        title_label = self.model.window_tags_title_label
        actors_label = self.model.window_tags_actors_label
        director_label = self.model.window_tags_director_label
        release_date_label = self.model.window_tags_release_label
        comment_label = self.model.window_tags_comment_label
        genre_label = self.model.window_tags_genre_label
        description_label = self.model.window_tags_description_label
        plot_label = self.model.window_tags_plot_label

        title_value = self.model.window_tags_title_value
        actors_value = self.model.window_tags_actors_value
        director_value = self.model.window_tags_director_value
        release_date_value = self.model.window_tags_release_date_value
        comment_value = self.model.window_tags_comment_value
        genre_value = self.model.window_tags_genre_value
        description_value = self.model.window_tags_description_value
        plot_value = self.model.window_tags_plot_value

        labels_list = [
            title_label,
            actors_label,
            director_label,
            release_date_label,
            comment_label,
            genre_label,
            description_label,
            plot_label,
        ]

        num_lines, _ = self.screen.getmaxyx()
        tags_box = self.screen.subwin(num_lines - 4, 0, 1, 0)
        tags_box_num_lines, tags_box_num_cols = tags_box.getmaxyx()

        if curses.has_colors():
            for I in range(1, tags_box_num_lines):
                tags_box.addstr(I, 0, str(" " * int(tags_box_num_cols - 1)), curses.color_pair(3))

            tags_box.bkgdset(ord(' '), curses.color_pair(3))

        label_max_len = 0
        for label in labels_list:
            if len(label) > label_max_len:
                label_max_len = len(label)

        tags_box.box()
        tags_box.addstr(0, 1, window_name)
        tags_box.addstr(2, (label_max_len - (len(str(title_label))) + 1), str(title_label + " " + title_value))
        tags_box.addstr(3, (label_max_len - (len(str(actors_label))) + 1), str(actors_label + " " + actors_value))
        tags_box.addstr(4, (label_max_len - (len(str(director_label))) + 1), str(director_label + " " + director_value))
        tags_box.addstr(5, (label_max_len - (len(str(release_date_label))) + 1),
                        str(release_date_label + " " + release_date_value))
        tags_box.addstr(6, (label_max_len - (len(str(comment_label))) + 1), str(comment_label + " " + comment_value))
        tags_box.addstr(7, (label_max_len - (len(str(genre_label))) + 1), str(genre_label + " " + genre_value))
        tags_box.addstr(8, (label_max_len - (len(str(description_label))) + 1),
                        str(description_label + " " + description_value))
        tags_box.addstr(9, (label_max_len - (len(str(plot_label))) + 1), str(plot_label + " " + plot_value))

        tags_box.refresh()

    def display_quit_box(self, window_quit_yesno):
        title_text = self.model.window_quit_title_text
        title_text = " " + title_text + " "
        message_text = self.model.window_quit_message_text
        yes_text = self.model.window_quit_yes_text
        no_text = self.model.window_quit_no_text

        num_lines, _ = self.screen.getmaxyx()
        quit_box = self.screen.subwin(num_lines - 4, 0, 1, 0)
        quit_box_num_lines, quit_box_num_cols = quit_box.getmaxyx()
        # Display the Last box on the background
        self.display_method_by_window[self.model.last_window]()

        # Check Quit box size
        if quit_box_num_lines > 9 and quit_box_num_cols > len(message_text) + 10:
            quit_sub_box = self.screen.subwin(7, len(message_text) + 8, ((num_lines / 3) - 2),
                                              (((quit_box_num_cols) - (len(message_text) + 6)) / 2))
            quit_sub_box_num_lines, quit_sub_box_num_cols = quit_sub_box.getmaxyx()
            if curses.has_colors():
                for I in range(0, quit_sub_box_num_lines):
                    quit_sub_box.addstr(I, 0, str(" " * int(quit_sub_box_num_cols - 1)), curses.color_pair(4))

            quit_sub_box.bkgdset(ord(' '), curses.color_pair(4))
            quit_sub_box_frame = quit_sub_box.derwin(5, len(message_text) + 5, 1, 1)
            _, quit_sub_box_frame_num_cols = quit_sub_box_frame.getmaxyx()
            quit_sub_box_frame.box()

            quit_sub_box_frame.addstr(0, (quit_sub_box_frame_num_cols / 2) - (len(title_text) / 2), title_text,
                                      curses.color_pair(5))
            quit_sub_box_frame.addstr(1, 2, message_text, curses.color_pair(4))

            YesButton = CursesButton(quit_sub_box_frame, 2,
                                     (quit_sub_box_frame_num_cols / 2) - ((len(yes_text) + 4)) - 3, yes_text)
            NoButton = CursesButton(quit_sub_box_frame, 2, (quit_sub_box_frame_num_cols / 2) - 1, no_text)
            self.model.window_quit_NoButton = NoButton
            self.model.window_quit_YesButton = YesButton
            if self.model.window_quit_yesno == 1:
                YesButton.Select()
                NoButton.UnSelect()
            else:
                YesButton.UnSelect()
                NoButton.Select()

                #quit_sub_box_frame.refresh()
                #quit_sub_box.refresh()
        quit_box.refresh()

    def display_source_box(self, window_name):
        self.name_text = self.model.window_source_name_text
        self.size_text = self.model.window_source_size_text
        self.mtime_text = self.model.window_source_mtime_text

        num_lines, _ = self.screen.getmaxyx()
        # Creat a sub window
        display_source_box = self.screen.subwin(num_lines - 4, 0, 1, 0)
        display_source_box_num_lines, display_source_box_num_cols = display_source_box.getmaxyx()
        # Put the Background color
        if curses.has_colors():
            for I in range(1, display_source_box_num_lines - 1):
                display_source_box.addstr(I, 1, str(" " * int(display_source_box_num_cols - 2)), curses.color_pair(3))
            display_source_box.bkgdset(ord(' '), curses.color_pair(3))

        display_source_box.addstr(0, 1, window_name)
        display_source_box.box()
        self.model.window_source_file_selector = FileSelect(display_source_box, 0, 0, self.name_text, self.size_text, self.mtime_text,
                                   self.model)

        # display_source_box.addstr(3, 1, self.model.file_selector)
        #display_source_box.refresh()
