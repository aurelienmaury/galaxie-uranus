'''
Created on 4 avr. 2015

@author: tuxa
'''

#######################
###    THE MODEL    ###
#######################
class model_class():
    def __init__(self):
        self.app_name = "GalaxieDrake"
        self.app_version = "0.2"
        
        self.last_message = ""
        self.last_info = ""

        self.active_window = 3
        self.last_window = 3
        
        self.bottom_button_list = [
            'Help',
            'Source',
            'Summary',
            'Video',
            'Audio',
            'Subtitles',
            'Chapter',
            'Tags',
            'Encode',
            'Quit'
        ]
        
        self.windows_button_underline = 2
        self.window_quit_yesno = 1
        self.window_quit_title_text = "The Galaxie Drake"
        self.window_quit_message_text = "Do you really want to quit the Galaxie Drake?"
        self.window_quit_yes_text = "Yes"
        self.window_quit_no_text = "No "
        self.window_quit_YesButton = ""
        self.window_quit_NoButton = ""

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
        
        self.window_source_name_text = "Name"
        self.window_source_size_text = "Size"
        self.window_source_mtime_text = "Modify time"
        
        self.window_source_selected_item = 0
        self.window_source_selected_item_list_value = []
        self.window_source_lsdir_item_number = 0
        self.window_source_item_it_can_be_display = 0
        self.window_source_item_list_scroll = 0
        self.window_source_pwd = "."

        self.window_source_file_selector = ""
        self.window_source_sort_by_name = 1
        self.window_source_sort_by_size = 0
        self.window_source_sort_by_time = 0
        self.window_source_sort_name_order = 1
        self.window_source_sort_size_order = 1
        self.window_source_sort_time_order = 1
        
        
    

    

