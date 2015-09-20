#!/usr/bin/python
# -*- coding: utf-8 -*-

import traceback
import Drake
import curses

def main(screen):
    model = Drake.model_class()
    viewer = Drake.ViewerClass([
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