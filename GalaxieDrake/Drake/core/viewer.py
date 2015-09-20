#!/usr/bin/python

'''
Created on 4 avr. 2015

@author: tuxa
'''
import curses

from Drake.queue import Queue
from Drake.main_panel import MainPanel
from Drake.api.button import CursesButton
from Drake.api.file_selector import FileSelect

class ViewerClass(object):
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
            0: lambda: self.display_main_panel(self.screen, self.model),
            1: lambda: self.display_full_box("Help"),
            2: lambda: self.display_source_panel("Select a source file to encode:"),
            3: lambda: self.display_summary_box("Summary"),
            4: lambda: self.display_queue_box("Queue"),
            5: lambda: self.display_full_box("Audio"),
            #8: lambda: self.display_tags_box("Tags"),
        }
        self.display_top_menu()
        self.display_method_by_window[self.model.active_window]()
        self.display_bottom_button()

        #screen.refresh()

    def init_curses(self):
        curses.curs_set(0)
        #self.screen.nodelay(1)
        curses.mousemask(-1)

    def init_colors(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(10, curses.COLOR_CYAN, curses.COLOR_BLUE)
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

    def display_top_menu(self):
        app_info_label = str("  " + self.model.app_name + "-" + self.model.app_version)
        top_menu_box = self.screen.subwin(0, 0, 0, 0)
        _, top_menu_box_num_cols = top_menu_box.getmaxyx()
        if curses.has_colors():
            top_menu_box.addstr(0, 0, str(" " * int(top_menu_box_num_cols)), curses.color_pair(1))
            top_menu_box.bkgdset(ord(' '), curses.color_pair(1))
        #top_menu_box.addstr(0, 0, "*")
        #top_menu_box.addstr(0, 0, "  File     Queue     View     Help")
        top_menu_box.addstr(
            0,
            (top_menu_box_num_cols - 1) - len(app_info_label[:-1]),
            app_info_label[:-1],
            curses.color_pair(1)
        )
        top_menu_box.insstr(
            0,
            top_menu_box_num_cols - 1,
            app_info_label[-1:],
            curses.color_pair(1)
        )

    def display_message(self, message):
        self.model.last_message = message
        message = " " + message
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
        display_info_sub_win = self.screen.subwin(1, screen_num_cols, screen_num_lines - 3, 0)
        _, display_info_sub_win_num_cols = display_info_sub_win.getmaxyx()
        if curses.has_colors():
            display_info_sub_win.insstr(0, 0, str(" " * int(display_info_sub_win_num_cols)), curses.color_pair(2))
            if len(message) >= display_info_sub_win_num_cols - 1:
                start, end = message[:display_info_sub_win_num_cols - 1], message[display_info_sub_win_num_cols - 1:]
                display_info_sub_win.addstr(0, 0, str(start))
                display_info_sub_win.insstr(0, display_info_sub_win_num_cols - 1, str(end[:1]))
            else:
                display_info_sub_win.addstr(0, 0, str(message))
        display_info_sub_win.refresh()

    def display_bottom_button(self):
        item_list = self.model.bottom_button_list
        labels_end_coord = ['', '', '', '', '', '', '', '', '', '', '', '']
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
                cumul += len(str(item_list[U]))
            if bottom_menu_box_num_cols - 1 > cumul + int((3 * max_can_be_display) - 0):
                max_can_be_display += 1

        bottom_menu_box.addstr(0, 0, str(" " * int(bottom_menu_box_num_cols)), curses.color_pair(1))
        bottom_menu_box.insstr(0, bottom_menu_box_num_cols - 1, " ", curses.color_pair(1))
        bottom_menu_box.addstr(0, 0, "")

        count = 0
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
        #bottom_menu_box.refresh()

    def display_summary_box(self, window_name):
        num_lines, _ = self.screen.getmaxyx()
        summary_box = self.screen.subwin(num_lines - 4, 0, 1, 0)
        summary_box_num_lines, summary_box_num_cols = summary_box.getmaxyx()

        #Start to draw the summary contener
        if curses.has_colors():
            for I in range(1, summary_box_num_lines):
                summary_box.addstr(I, 0, str(" " * int(summary_box_num_cols - 1)), curses.color_pair(3))
            summary_box.bkgdset(ord(' '), curses.color_pair(3))
        #Creat a box and add the name of the windows like a king, who trust that !!!
        summary_box.box()
        summary_box.addstr(0, 1, window_name)

        if not self.model.transcoder == -1:
            #Request the self.model.transcoder for import informations
            input_file = self.model.transcoder.input_file
            output_file = self.model.transcoder.output_file
            video_title = self.model.transcoder.file_title
            duration = self.model.transcoder.scan_result[2]
            size = self.model.transcoder.scan_result[3]
            pixel_aspect = self.model.transcoder.scan_result[4]
            display_aspect = self.model.transcoder.scan_result[5]
            display_aspect_infos = self.model.transcoder.get_display_aspect_info(str(display_aspect))
            fps = self.model.transcoder.scan_result[6]
            fps_infos = self.model.transcoder.get_fps_info(fps)
            fps_target_infos = self.model.transcoder.get_fps_info(fps)
            autocrop = self.model.transcoder.scan_result[7]
            audio_track_list = self.model.transcoder.scan_result[8]
            audio_info_list = self.model.transcoder.scan_result[11]
            subtitle_track_list = self.model.transcoder.scan_result[10]
            subtitle_track_list_shorted = self.model.transcoder.scan_result[12]
            vcodec = self.model.transcoder.vcodec
            width = self.model.transcoder.video_width
            height = self.model.transcoder.video_height
            res_txt = self.model.transcoder.video_res_txt
            bit_rate = self.model.transcoder.video_bitrate
            x264_preset = self.model.transcoder.x264_preset
            h264_profile = self.model.transcoder.h264_profile
            h264_level = self.model.transcoder.h264_level
            bpf = ("%.3f" % float(self.model.transcoder.bpf))

            #Creation of the summary_box_lines_list it will store all information to display line file , one entry by line
            summary_box_lines_list = list()
            summary_box_lines_list.append(str("Title           : " + "\"" + str(video_title) + "\"" + ", Duration: " + str(duration)))
            summary_box_lines_list.append(str(" Source         : " + str(input_file)))
            summary_box_lines_list.append(str(" Dimensions     : " + str(size)))
            summary_box_lines_list.append(str(" Video Codec    : " + str(vcodec.title())))
            summary_box_lines_list.append(str(" Autocrop       : " + str(autocrop)))
            summary_box_lines_list.append(str(" Pixel Aspect   : " + str(pixel_aspect)))
            summary_box_lines_list.append(str(" Display Aspect : " + str(display_aspect) + ":1 " + str(display_aspect_infos)))
            summary_box_lines_list.append(str(" Frame Rate     : " + str(fps_infos)))

            #Make a loop if Audios tracks have been detected and print each one.
            if self.model.transcoder.detected_audio:
                if len(audio_track_list) == 1:
                    summary_box_lines_list.append(str(" Audio Track    : "))
                else:
                    summary_box_lines_list.append(str(" Audio Tracks   : "))
                count = 0
                for track_info in audio_track_list:
                    if len(track_info) == 7:
                        summary_box_lines_list.append(str("  " + str(track_info[0]) + ", " + str(track_info[1]) + ", " + str(track_info[2]) + ", " + str(track_info[3]) + ", " + str(track_info[4]) + ", " + str(track_info[5]) + ", " + str(track_info[6])))
                    elif len(track_info) == 6:
                        summary_box_lines_list.append(str("  " + str(track_info[0]) + ", " + str(track_info[1]) + ", " + str(track_info[2]) + ", " + str(track_info[3]) + ", " + str(track_info[4]) + ", " + str(track_info[5])))
                    elif len(track_info) == 5:
                        summary_box_lines_list.append(str("  " + str(track_info[0]) + ", " + str(track_info[1]) + ", " + str(track_info[2]) + ", " + str(track_info[3]) + ", " + str(track_info[4])))
                    count += 1

            #Make a loop for SubTitle it have been detected and print each one.
            if self.model.transcoder.detected_subtitle:
                if len(subtitle_track_list) == 1:
                    summary_box_lines_list.append(str(" SubTitle Track : "))
                else:
                    summary_box_lines_list.append(str(" SubTitle Tracks: "))
                count = 0
                for track_info in subtitle_track_list:
                    summary_box_lines_list.append(str("  " + str(track_info[0]) + ", " + str(track_info[1]) + ", " + str(track_info[2]) + ", " + str(track_info[3]) + ", " + str(track_info[4])))
                    count += 1

            #A Small Empty line for the form
            summary_box_lines_list.append(str(""))
            #Start to print destination informations
            summary_box_lines_list.append(str(" Destination    : " + str(output_file)))
            summary_box_lines_list.append(str(" Dimensions     : " + str(width)+"x"+str(height)+" "+res_txt))
            summary_box_lines_list.append(str(" Bitrate        : " + str(bit_rate)+" kbps  BPF: "+str(bpf)))
            summary_box_lines_list.append(str(" x264 Preset    : " + str(x264_preset.title())))
            summary_box_lines_list.append(str(" H.264 Profile  : " + str(h264_profile.title())))
            summary_box_lines_list.append(str(" H.264 Level    : " + str(h264_level)))
            summary_box_lines_list.append(str(" Display Aspect : " + str(display_aspect) + ":1 " + str(display_aspect_infos)))
            summary_box_lines_list.append(str(" Frame Rate     : " + str(fps_target_infos)))

            #Make a loop for print a list about what will be do.
            #All that part is just a for make Humain view that because the transcoder use 5 Variables

            # Display detected Audio track and list them
            if self.model.transcoder.detected_audio:
                if len(audio_info_list) == 1:
                    summary_box_lines_list.append(str(" Audio Track    : "))
                else:
                    summary_box_lines_list.append(str(" Audio Tracks   : "))
                count = 1
                for track_info in audio_info_list:
                    #Ok that not so clean and that mechanical but it make no error (That Just a Display)
                    track_info_length = len(track_info)

                    if track_info_length in [7, 6, 5]:
                        line = self.build_final_summary_audio_list_str(count, track_info)

                        summary_box_lines_list.append(line)

                    #Count for can print the actual audio piste number
                    count += 1
            #Display detected SubTitle(s)
            if self.model.transcoder.detected_subtitle:
                if len(subtitle_track_list_shorted) == 1:
                    summary_box_lines_list.append(str(" SubTitle Track : "))
                else:
                    summary_box_lines_list.append(str(" SubTitle Tracks: "))
                count = 1
                for track_info in subtitle_track_list_shorted:
                    summary_box_lines_list.append(str("  " + str(count) + "->" + str(track_info[0]) + ", " + str(track_info[1]) + ", " + str(track_info[2]) + ", " + str(track_info[3]) + ", " + str(track_info[4])))
                    count += 1

            #All that have to be display
            #Here the list is supposate to complet and will be parse for display thing
            #Then add all list entrys as lines and control max line/cols size
            spacing = 1
            if summary_box_num_lines - 2 <= len(summary_box_lines_list):
                spacing = 0
            for I in range(0, len(summary_box_lines_list)):
                if I + 1 + spacing < summary_box_num_lines - 1:
                    if len(str(summary_box_lines_list[I])) >= summary_box_num_cols - 3 - spacing:
                        summary_box.addstr(I + 1 + spacing, 1 + spacing,str(summary_box_lines_list[I][:summary_box_num_cols - 3 - spacing]))
                    else:
                        summary_box.addstr(I + 1 + spacing, 1 + spacing, str(summary_box_lines_list[I]))

    def build_final_summary_audio_list_str(self, count, track_info):

        track_info_length = len(track_info)

        audio_codec = ["AAC", "AC3", "DTS", "DTSHD", "MP3"]
        if track_info[2].uppper() in audio_codec:

            if track_info_length == 7:
                passthrough = " pass-through"
            else:
                passthrough = ""

            line = "  " + str(count) + "->" + str(track_info[0]) + ", " + str(track_info[1]) + ", " + str(
                track_info[2]) + passthrough + ", " + str(track_info[3]) + ", " + str(track_info[4])

            if track_info_length != 5:
                line += + ", " + str(track_info[5]) + ", " + str(track_info[6])
        else:

            track_channel_is_five_one = (track_info[3].strip() == "5.1ch")

            if track_channel_is_five_one:
                bit_rate_audio = "384kps"
            else:
                bit_rate_audio = "128kps"

            if (track_info_length == 7):
                seventh = ", " + str(track_info[6])
            else:
                seventh = ""

            line = "  " + str(count) + "->" + str(track_info[0]) + ", " + str(
                track_info[1]) + ", " + "AAC-LC converting" + ", " + str(
                track_info[3]) + ", " + bit_rate_audio + ", " + str(track_info[4])

            if track_info_length != 5:
                line += ", " + str(track_info[5]) + seventh

        return line


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

        #tags_box.refresh()

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
            quit_sub_box = self.screen.subwin(7,
                                              len(message_text) + 8,
                                              ((num_lines / 3) - 2),
                                              (((quit_box_num_cols) - (len(message_text) + 6)) / 2)
                                              )
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

            YesButton = CursesButton(quit_sub_box_frame,
                                     2,
                                     (quit_sub_box_frame_num_cols / 2) - ((len(yes_text) + 4)) - 3,
                                     yes_text
                                     )
            NoButton = CursesButton(quit_sub_box_frame,
                                    2,
                                    (quit_sub_box_frame_num_cols / 2) - 1,
                                    no_text
                                    )
            self.model.window_quit_NoButton = NoButton
            self.model.window_quit_YesButton = YesButton
            if self.model.window_quit_yesno == 1:
                YesButton.select()
                NoButton.unselected()
            else:
                YesButton.unselected()
                NoButton.select()

    def display_main_panel(self, parent, model):
        self.model.bottom_button_list = self.model.main_panel_button_list
        #Creat the contener
        parent_max_lines, parent_max_cols = parent.getmaxyx()
        panel_subwin = self.screen.subwin(parent_max_lines - 4, 0, 1, 0)
        panel_max_lines, max_cols = panel_subwin.getmaxyx()
        if curses.has_colors():
            for I in range(1, panel_max_lines - 1):
                panel_subwin.addstr(
                    I,
                    1,
                    str(" " * int(max_cols - 2)),
                    curses.color_pair(3)
                )
            panel_subwin.bkgdset(ord(' '), curses.color_pair(3))
        panel_subwin.box()
        self.model.main_panel_sub_win = panel_subwin
        self.model.main_panel = MainPanel(
            self.model.main_panel_sub_win,
            0,
            0,
            model
        )

    def display_source_panel(self, window_name):
        self.model.bottom_button_list = self.model.file_selector_button_list
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
        self.model.window_source_file_selector = FileSelect(display_source_box, 0, 0, self.model)

    def display_queue_box(self, window_name):
        self.model.bottom_button_list = self.model.taskspooler_button_list
        #Creat the contener
        num_lines, _ = self.screen.getmaxyx()
        display_queue_box = self.screen.subwin(num_lines - 4, 0, 1, 0)
        display_queue_box_num_lines, display_queue_box_num_cols = display_queue_box.getmaxyx()
        if curses.has_colors():
            for I in range(1, display_queue_box_num_lines - 1):
                display_queue_box.addstr(
                    I,
                    1,
                    str(" " * int(display_queue_box_num_cols - 2)),
                    curses.color_pair(3)
                )
            display_queue_box.bkgdset(ord(' '), curses.color_pair(3))
        display_queue_box.box()
        display_queue_box.addstr(0, 1, window_name)
        self.model.window_queue_sub_win = display_queue_box
        self.model.window_queue_manager = Queue(
            display_queue_box,
            0,
            0,
            self.model
        )

