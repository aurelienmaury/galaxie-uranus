#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: Jérôme ORNECH alias "Tuux" <tuxa@rtnp.org> all rights reserved
__author__ = 'Tuux'

import traceback
import Drake
from Drake.core.model import model_class
from Drake.core.viewer import ViewerClass
import curses
import os
import sys

#######################################
######DEFINE SOME BASIC VARIABLES######
#######################################
script_name = os.path.basename(sys.argv[0])
script_name_title = os.path.basename(os.path.splitext(sys.argv[0])[0])
script_name_title = script_name_title.title()
version = '0.3'

# Add ./Drake directory on PATH env var user space
os.environ["PATH"] += os.pathsep + os.path.join(os.path.dirname(os.path.realpath(__file__)), './Drake')


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


def check_transcoder():
    if not which("transcoder.py"):
        print "Error: Transcoder is require, for enable transcoding queue"
        print "Error: Please install 'transcoder.py' or verify it is aviable on your $PATH env var"
        print "Error: " + script_name_title + " will abort ..."
        sys.exit(1)
    else:
        return which("transcoder.py")


def check_taskspooler():
    if not which("tsp"):
        print "Error: Task Spooler is require, for enable transcoding queue"
        print "Error: Please install 'task-spooler' or verify it is available on your $PATH env var"
        print "Error: " + script_name_title + " will abort ..."
        sys.exit(1)
    else:
        return which("tsp")


def check_nice():
    if not which("nice"):
        print "Warning: Nice is require, for fix low process priority"
        print "Warning: " + script_name_title + " will continue without ..."
        return None
    else:
        return which("nice")


def check_tail():
    if not which("tail"):
        print "Warning: 'tail' is require, for take look on file's"
        print "Error: Please install 'tail' or verify it is available on your $PATH env var"
        print "Error: " + script_name_title + " will abort ..."
        sys.exit(1)
    else:
        return which("tail")


def check_df():
    if not which("df"):
        print "Warning: 'df' (DiskFree) is require, for have disk's stats"
        print "Error: Please install 'df' or verify it is available on your $PATH env var"
        print "Error: " + script_name_title + " will abort ..."
        sys.exit(1)
    else:
        return which("df")


def main(screen):

    viewer = ViewerClass([
        "Help",
        "Source",
        "Summary",
        "Video",
        "Audio",
        "Subtitles",
        "Chapter",
        "Tags",
        "Encode",
        "Quit"
    ], screen, model)
    Drake.controler_class(screen, viewer, model)

if __name__ == '__main__':
    # Before init NCurse Check for Apps dependency and store it in model
    model = model_class()
    model.taskspooler_path = check_taskspooler()
    model.nice_path = check_nice()
    model.transcoder_path = check_transcoder()
    model.tail_path = check_tail()
    model.df_path = check_df()
    model.app_version = version
    model.app_name = script_name_title
    if not os.access(model.transcoder_path, os.R_OK):
        print "Error: " + model.transcoder_path + " can't be read"
        print "Error: \"transcoder.py is require \""
        print "Error: " + script_name_title + " will abort ..."
        sys.exit(1)
    elif not os.access(model.transcoder_path, os.X_OK):
        print "Error: " + model.transcoder_path + " haven't executable permission"
        sys.exit(1)

    try:
        curses.wrapper(main)
    except:
        traceback.print_exc()