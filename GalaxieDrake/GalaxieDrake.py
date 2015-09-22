#!/usr/bin/python
# -*- coding: utf-8 -*-

import traceback
import Drake
from Drake.core.model import model_class
from Drake.core.viewer import ViewerClass
import curses

def main(screen):
    model = model_class()
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

    Drake.controler_class(screen, viewer,model)

if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except:
        traceback.print_exc()