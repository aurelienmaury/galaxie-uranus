#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: Jérôme ORNECH alias "Tuux" <tuxa@rtnp.org> all rights reserved
__author__ = 'Tuux'

import psutil
from ..utility import bytes2human
from ..utility import get_processor_info
from ..utility import disk_free
# from ..plugins.task_spooler_summary import TaskSpoolerSummary

#######################
###    THE MODEL    ###
#######################
class model_class():
    def __init__(self):
        self.app_name = "GalaxieDrake"
        self.app_version = "0.2"
        
        self.last_message = ""
        self.last_info = ""

        self.active_window = 0
        self.last_window = 0

        self.tsp = None

        self.bottom_button_list = [
            'Help',
            'Source',
            'Summary',
            'Queue',
            'Audio',
            'Subtitles',
            'Chapter',
            'Tags',
            'Encode',
            'Quit'
        ]

        self.main_panel_button_list = [
            'Help',
            'Source',
            'Summary',
            'Queue',
            'Audio',
            'Subtitles',
            'Chapter',
            'Tags',
            'Encode',
            'Quit'
        ]

        self.taskspooler_button_list = [
            'Help',
            '',
            'Voir',
            '',
            '',
            '',
            '',
            'Delete',
            '',
            'Back'
        ]

        self.file_selector_button_list = [
            'Help',
            '',
            'Scan',
            '',
            '',
            'Rename',
            'Creat Task',
            'Delete',
            '',
            'Back'
        ]

        self.video_file_extensions = (
            '.ts',
            '.mkv',
            '.3g2',
            '.3gp',
            '.asf',
            '.asx',
            '.avi',
            '.flv',
            '.m4v',
            '.mov',
            '.mp4',
            '.mpg',
            '.rm',
            '.srt',
            '.swf',
            '.vob',
            '.wmv'
        )



        self.windows_button_underline = 2
        self.window_quit_yesno = 1
        self.window_quit_title_text = "The Galaxie Drake"
        self.window_quit_message_text = "Do you really want to quit GalaxieDrake?"
        self.window_quit_yes_text = "Yes"
        self.window_quit_no_text = "No "
        self.window_quit_YesButton = None
        self.window_quit_NoButton = None

        self.window_tags_title_label = "Title:"
        self.window_tags_actors_label = "Actors:"
        self.window_tags_director_label = "Director:"
        self.window_tags_release_label = "Release Date:"
        self.window_tags_comment_label = "Comment:"
        self.window_tags_genre_label = "Genre:"
        self.window_tags_description_label = "Description:"
        self.window_tags_plot_label = "Plot:"

        self.window_tags_title_value = "The movie of the death who kill hard"
        self.window_tags_actors_value = "A Tonne of mega actors"
        self.window_tags_director_value = "They have do it alone"
        self.window_tags_release_date_value = "2099"
        self.window_tags_comment_value = "."
        self.window_tags_genre_value = ".."
        self.window_tags_description_value = "..."
        self.window_tags_plot_value = "...."

        self.window_source_rep_sup_text = "UP--DIR"

        self.display_scan_dialog = 0


        self.display_history_menu = 0
        self.window_source_history_dir_list = list()
        self.history_menu_selected_item = 0
        self.history_menu_selected_item_value = "."
        self.history_menu_item_list_scroll = 0
        self.history_menu_can_be_display = 0
        self.history_menu_item_number = 0
        self.history_dialog_box = 0
        self.window_source_history_dir_list_object = ""
        self.window_source_history_dir_list_prev_object = ""
        self.window_source_history_dir_list_next_object = ""

        self.display_history_text = "History"
        self.window_source_name_text = "Name"
        self.window_source_size_text = "Size"
        self.window_source_mtime_text = "Modify time"

        self.window_source_name_text_object = ""
        self.window_source_size_text_object = ""
        self.window_source_mtime_text_object = ""

        self.window_source_selected_item = 0
        self.window_source_selected_item_list_value = list()
        self.window_source_ls_dir_item_number = 0
        self.window_source_item_it_can_be_display = 0
        self.window_source_item_list_scroll = 0
        self.window_source_pwd = "."

        self.window_source_file_selector = ""
        self.window_source_sort_by_name = 1
        self.window_source_sort_by_size = 0
        self.window_source_sort_by_mtime = 0
        self.window_source_sort_name_order = 1
        self.window_source_sort_size_order = 1
        self.window_source_sort_mtime_order = 1
        self.window_source_sort_name_letter = self.window_source_name_text[0].lower()
        self.window_source_sort_size_letter = self.window_source_size_text[0].lower()
        self.window_source_sort_mtime_letter = self.window_source_mtime_text[0].lower()

        # Queue Manager Values and Setting
        self.window_queue_selected_item = 0
        self.window_queue_selected_item_list_value = list()
        self.window_queue_selected_for_action_value = list()
        self.window_queue_tasks_list = list()
        self.window_queue_item_number = 0
        self.window_queue_item_it_can_be_display = 0
        self.window_queue_item_list_scroll = 0

        self.window_queue_manager = ""
        self.window_queue_sub_win = ""
        self.window_queue_id_text = "ID"
        self.window_queue_state_text = "State"
        self.window_queue_output_text = "Output"
        self.window_queue_e_level_text = "E-Level"
        self.window_queue_times_text = "Time H:M:S"
        self.window_queue_command_text = "Command"

        self.window_queue_state_object = None
        self.window_queue_output_object = None
        self.window_queue_e_level_object = None
        self.window_queue_times_object = None
        self.window_queue_command_object = None

        # Main Panel
        self.up_time = ""
        self.main_panel_item_it_can_be_display = 0

        self.cpu_label_text = 'CPU'
        self.mem_label_text = 'Mem  '
        self.swap_label_text = 'Swap '
        self.used_label_text = 'Used'
        self.free_label_text = 'Free'
        self.total_label_text = 'Total'
        self.user_label_text = 'user'
        self.nice_label_text = 'nice'
        self.system_label_text = 'system'
        self.idle_label_text = 'idle'
        self.iowait_label_text = 'iowait'
        self.memory_title_text = "Virtual and Swap Memory's"
        self.disks_title_text = "Mounted File System's"

        self.psutil_cpu_percent_list = psutil.cpu_percent(interval=1, percpu=True)
        self.psutil_cpu_times_percent_list = psutil.cpu_times_percent(interval=1, percpu=False)
        self.processor_summary_text = get_processor_info()

        self.psutil_virtual_memory = psutil.virtual_memory()
        self.memory_used = self.psutil_virtual_memory.used
        self.memory_cache_plus_buffer = self.psutil_virtual_memory.cached + self.psutil_virtual_memory.buffers
        self.memory_free = self.psutil_virtual_memory.total - self.memory_used

        self.memory_used = bytes2human(self.memory_used - self.memory_cache_plus_buffer)
        self.memory_free = bytes2human(self.memory_free)
        self.memory_total = bytes2human(self.psutil_virtual_memory.total)

        self.psutil_swap_memory = psutil.swap_memory()
        self.swap_used = bytes2human(self.psutil_swap_memory.used)
        self.swap_free = bytes2human(self.psutil_swap_memory.total - self.psutil_swap_memory.used)
        self.swap_total = bytes2human(self.psutil_swap_memory.total)



        self.taskspooler_summary = ''
        self.taskspooler_summary_list = list()
        self.taskspooler_title_text = "TaskSpooler"
        self.taskspooler_job_number_text = "Task"
        self.taskspooler_running_text = "Running"
        self.taskspooler_queued_text = "Queued"
        self.taskspooler_finished_text = "Finished"
        self.taskspooler_finished_with_error_text = "Error"


        # General
        self.transcoder = -1
        self.transcoder_path = None
        self.taskspooler_path = None
        self.nice_path = None
        self.nice_priority = '15'
        self.df_path = None
        self.disk_partition_list = disk_free()

        self.dialog_box = 0
        #Scanning Dialoog Box
        self.scanning_dialog_box = ''
        self.scanning_dialog_sub_box = ''
        self.display_scanning_text = "Scanning"
        self.scanning_directory = None
        self.scanning_source_directory_label_text = 'Source Directory:'
        self.scanning_searching_for_label_text = 'Searching for:'
        self.scanning_exception_pattern_label_text = 'Exception Pattern:'
        self.scanning_scanning_for_label_text = "Scanning for:"
        self.scanning_percent = 0
        self.scanning_file_pattern = ''
        self.searching_extension_list = [
            '*.ts',
            '*.mkv',
            '*.3g2',
            '*.3gp',
            '*.asf',
            '*.asx',
            '*.avi',
            '*.flv',
            '*.m4v',
            '*.mov',
            '*.mp4',
            '*.mpg',
            '*.rm',
            '*.srt',
            '*.swf',
            '*.vob',
            '*.wmv'
        ]
        self.searching_file_pattern_exception = '* - *p.mkv'
        self.searching_extension_list_label_text = ''
        for file_pattern in self.searching_extension_list:
            self.searching_extension_list_label_text += file_pattern.upper()[2:]
            self.searching_extension_list_label_text += ' '
        self.files_list_to_transcode = list()
        self.window_summary_input_file_text = ''


        #A Hint list where it will be randomaly display
        self.hint_pre_message_text = 'Hint: '
        self.hint_list = [
            'The homepage of GalaxieDrake: http://www.galaxie.eu.org/',
            'The Summary present the Scan results and target file calculations.',
            'The Queue Manager is in fact a TaskSpooler(tsp) Ncurse Fronted.',
            'GalaxieDrake is more as a automated HandBrakeCLI Ncurse Fronted',
            'File Selector have Shorting capability with keys: n,s,t or with Mouse.'
        ]

