__author__ = 'tuxa www.rtnp.org'

import curses

class creat_history_box():

    def __init__(self, model, parent, y, x, label, color):

        self.model = model
        self.parent = parent
        self.y_parent, self.x_parent = self.parent.getbegyx()
        self.y_max_parent, self.x_max_parent = self.parent.getmaxyx()
        self.y = y
        self.x = x
        self.label = str(label)
        self.label = str(" "+label+" ")
        self.Width = len(str(label))
        self.color = color

        # Calcul for history window size it depend of the history list
        if len(self.model.window_source_history_dir_list)+2 < self.y_max_parent:
            history_y = len(self.model.window_source_history_dir_list) + 2

        else:
            history_y = self.y_max_parent - 1

        if len(self.model.window_source_history_dir_list) > 0:
            history_x = len(max(self.model.window_source_history_dir_list, key=len)) + 2
            if history_x > self.x_max_parent - 1:
                history_x = self.x_max_parent
        else:
            history_x = len(self.label) + 2

        history_box = self.parent.subwin(
            history_y,
            history_x,
            2,
            0
        )

        # Inside the history menu
        history_box.bkgdset(ord(' '), self.color)
        history_box.bkgd(ord(' '), self.color)
        history_box_num_lines, history_box_num_cols = history_box.getmaxyx()
        max_cols_to_display = history_box_num_cols - 2
        max_lines_to_display = 1

        for I in range(0, history_box_num_lines-2):
            history_box.addstr(I+1,
                               1,
                               str(" " * int(history_box_num_cols-2)),
                               self.color
                               )
            max_lines_to_display += 1
        self.model.history_menu_can_be_display = max_lines_to_display

        for I in range(0+self.model.history_menu_item_list_scroll, self.model.history_menu_can_be_display):
            if I < len(self.model.window_source_history_dir_list):
                if self.model.history_menu_selected_item == I:
                    self.model.history_menu_selected_item_value = self.model.window_source_history_dir_list[I]
                    if len(str(self.model.window_source_history_dir_list[I])) >= max_cols_to_display:
                        history_box.addstr(
                            I+1,
                            1,
                            str(self.model.window_source_history_dir_list[I][:max_cols_to_display]),
                            curses.color_pair(1)
                        )
                    else:
                        history_box.addstr(
                            I+1,
                            1,
                            str(self.model.window_source_history_dir_list[I]),
                            curses.color_pair(1)
                        )
                        history_box.insstr(
                            I+1,
                           len(str(self.model.window_source_history_dir_list[I])) + 1,
                           str(" " * int(history_box_num_cols-2-len(str(self.model.window_source_history_dir_list[I])))),
                           curses.color_pair(1)
                        )
                else:
                    if len(str(self.model.window_source_history_dir_list[I])) >= max_cols_to_display:
                        history_box.addstr(
                            I+1,
                            1,
                            str(self.model.window_source_history_dir_list[I][:max_cols_to_display]),
                            self.color
                        )
                    else:
                        history_box.addstr(
                            I+1,
                            1,
                            str(self.model.window_source_history_dir_list[I]),
                            self.color
                        )
        history_box.box()
        history_box.addstr(
            0,
            (history_box_num_cols / 2) - (len(self.label) / 2),
            self.label,
            curses.color_pair(5)
        )

    def mouse_clicked(self, mouse_event):
        (event_id, x, y, z, event) = mouse_event
        if self.y_parent <= y <= self.y_parent + 1:
            if self.x + self.x_parent <= x < self.x + self.x_parent + self.Width:
                return 1
        else:
            return 0
