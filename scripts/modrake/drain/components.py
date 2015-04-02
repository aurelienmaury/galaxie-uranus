import curses

class Panel(object):
    def __init__(self, title, activation_key):
        self.title = title
        self.activation_key = activation_key

    def display_on(self, screen):
        num_lines, num_cols = screen.getmaxyx()
        # Creat a sub window
        full_box = screen.subwin(num_lines - 3, 0, 1, 0)
        self_num_lines, selft_num_cols = full_box.getmaxyx()
        # Put the Background color
        if curses.has_colors():
            for I in range(1, self_num_lines - 1):
                full_box.addstr(I, 1, str(" " * int(selft_num_cols - 2)), curses.color_pair(3))
            full_box.bkgdset(ord(' '), curses.color_pair(3))
        full_box.box()
        full_box.addstr(0, 1, self.title)
        full_box.refresh()

    def handle_event(self, event):
        return False

    
class YesNoDialog(Panel):
    def __init__(self, parent, title, text, activation_key):
        super(YesNoDialog, self).__init__(title, activation_key)
        self.yes_highlighted = False
        self.text = text
        self.parent = parent

    def display_on(self, screen):
        title_text = " " + self.title + " "
        message_text = self.text
        yes_text = "Yes"
        no_text = "No"

        num_lines, num_cols = screen.getmaxyx()
        quit_box = screen.subwin(num_lines - 3, 0, 1, 0)
        quit_box_num_lines, quit_box_num_cols = quit_box.getmaxyx()

        if curses.has_colors():
            for I in range(1, quit_box_num_lines):
                quit_box.addstr(I, 0, str(" " * int(quit_box_num_cols - 1)), curses.color_pair(3))

            quit_box.bkgdset(ord(' '), curses.color_pair(3))

        quit_box.box()
        quit_box.addstr(0, 1, "Quit")

        if quit_box_num_lines > 9 and quit_box_num_cols > len(message_text) + 10:
            quit_sub_box = screen.subwin(7, len(message_text) + 8, (quit_box_num_lines / 3),
                                         (((quit_box_num_cols) - (len(message_text) + 6)) / 2))
            quit_sub_box_num_lines, quit_sub_box_num_cols = quit_sub_box.getmaxyx()
            if curses.has_colors():
                for I in range(0, quit_sub_box_num_lines):
                    quit_sub_box.addstr(I, 0, str(" " * int(quit_sub_box_num_cols - 1)), curses.color_pair(4))

            quit_sub_box.bkgdset(ord(' '), curses.color_pair(4))
            quit_sub_box_frame = quit_sub_box.derwin(5, len(message_text) + 5, 1, 1)
            quit_sub_box_frame_num_lines, quit_sub_box_frame_num_cols = quit_sub_box_frame.getmaxyx()
            quit_sub_box_frame.box()

            quit_sub_box_frame.addstr(0, (quit_sub_box_frame_num_cols / 2) - (len(title_text) / 2), title_text,
                                      curses.color_pair(5))
            quit_sub_box_frame.addstr(1, 2, message_text, curses.color_pair(4))


            YesButton = Button(quit_sub_box_frame, 2,
                               (quit_sub_box_frame_num_cols / 2) - ((len(yes_text) + 4)) - 3,
                               yes_text)
            NoButton = Button(quit_sub_box_frame, 2, (quit_sub_box_frame_num_cols / 2) - 1, no_text)

            if self.yes_highlighted:
                YesButton.Select()
                NoButton.UnSelect()
            else:
                NoButton.Select()
                YesButton.UnSelect()

            quit_sub_box_frame.refresh()
            quit_sub_box.refresh()

        quit_box.refresh()

    def payload(self):
        self.parent.shutdown()

    def handle_event(self, event):

        if event.value == curses.KEY_LEFT or event.value == curses.KEY_RIGHT:

            self.yes_highlighted = not self.yes_highlighted
            return True

        if (event.value == curses.KEY_ENTER or event.value == ord("\n")) and self.yes_highlighted:

            self.payload()
            self.parent.finish_dialog()
            return True

        return False


class Button:
    def __init__(self, Window, Y, X, Label, Hotkey=0):
        self.Parent = Window
        self.YParent, self.XParent = Window.getbegyx()
        self.Y = Y
        self.X = X
        self.LabelButton = "[ " + Label + " ]"
        self.Label = Label
        self.Width = len(self.LabelButton) + 2  # label, plus lines on side
        self.Underline = 2
        Window.refresh()

    def Select(self):
        self.Underline = 2
        self.Parent.addstr(self.Y + 1, self.X + 1, self.LabelButton, curses.color_pair(1))
        self.Parent.addstr(self.Y + 1, self.X + self.Underline + 1, self.LabelButton[self.Underline],
                           curses.A_REVERSE | curses.color_pair(3))
        self.Parent.move(self.Y + 1, self.X + self.Underline + 1)
        self.Selected = 1

    def UnSelect(self):
        self.Underline = 1
        self.Parent.addstr(self.Y + 1, self.X + 1, self.LabelButton, curses.color_pair(4))
        self.Parent.addstr(self.Y + 1, self.X + self.Underline + 1, self.LabelButton[self.Underline],
                           curses.A_REVERSE | curses.color_pair(3))
        self.Selected = 0

    def SelectedState(self):
        # display_message(str(self.Selected))
        if self.Selected == 1:
            return 1
        else:
            return 0

    def KeyPressed(self, Char):

        if (Char > 255): return 0  # skip control-characters
        if chr(Char).upper() == self.LabelButton[self.Underline]:
            return 1
        else:
            return 0

    def MouseClicked(self, MouseEvent):
        (id, x, y, z, event) = MouseEvent
        if (self.YParent + 3 <= y <= self.YParent + 3) and (
                            self.X + self.XParent <= x < self.X + self.XParent + self.Width - 1):
            return 1
        else:
            return 0

