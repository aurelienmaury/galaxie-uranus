#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 4 avr. 2015

@author: tuxa
'''

import curses
import os
import math
import time
from os.path import expanduser
from operator import itemgetter


class CursesButton():
    def __init__(self, window, Y, X, Label, Hotkey=0):
        self.Parent = window
        self.YParent, self.XParent = window.getbegyx()
        self.Y = Y
        self.X = X
        self.LabelButton = "[ " + Label + " ]"
        self.Label = Label
        self.Width = len(self.LabelButton) + 2
        self.Underline = 2
        window.refresh()

    def Select(self):
        self.Parent.addstr(self.Y + 1, self.X + 1, self.LabelButton, curses.color_pair(1))
        self.Parent.addstr(self.Y + 1, self.X + self.Underline + 1, self.LabelButton[self.Underline],
                           curses.A_REVERSE | curses.color_pair(3))
        self.Parent.move(self.Y + 1, self.X + self.Underline + 1)
        self.Selected = 1

    def UnSelect(self):
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


class FileSelect():
    def __init__(self, Window, Y, X, name_text, size_text, mtime_text, model):
        self.model = model
        self.Parent = Window
        self.YParent, self.XParent = Window.getbegyx()
        self.YParentMax, self.XParentMax = Window.getmaxyx()
        self.Y = Y
        self.X = X
        self.Width = self.XParentMax
        video_file_extensions = (
            '.264', '.3g2', '.3gp', '.3gp2', '.3gpp', '.3gpp2', '.3mm', '.3p2', '.60d', '.787', '.89', '.aaf', '.aec',
            '.aep', '.aepx',
            '.aet', '.aetx', '.ajp', '.ale', '.am', '.amc', '.amv', '.amx', '.anim', '.aqt', '.arcut', '.arf', '.asf',
            '.asx', '.avb',
            '.avc', '.avd', '.avi', '.avp', '.avs', '.avs', '.avv', '.axm', '.bdm', '.bdmv', '.bdt2', '.bdt3', '.bik',
            '.bin', '.bix',
            '.bmk', '.bnp', '.box', '.bs4', '.bsf', '.bvr', '.byu', '.camproj', '.camrec', '.camv', '.ced', '.cel',
            '.cine', '.cip',
            '.clpi', '.cmmp', '.cmmtpl', '.cmproj', '.cmrec', '.cpi', '.cst', '.cvc', '.cx3', '.d2v', '.d3v', '.dat',
            '.dav', '.dce',
            '.dck', '.dcr', '.dcr', '.ddat', '.dif', '.dir', '.divx', '.dlx', '.dmb', '.dmsd', '.dmsd3d', '.dmsm',
            '.dmsm3d', '.dmss',
            '.dmx', '.dnc', '.dpa', '.dpg', '.dream', '.dsy', '.dv', '.dv-avi', '.dv4', '.dvdmedia', '.dvr', '.dvr-ms',
            '.dvx', '.dxr',
            '.dzm', '.dzp', '.dzt', '.edl', '.evo', '.eye', '.ezt', '.f4p', '.f4v', '.fbr', '.fbr', '.fbz', '.fcp',
            '.fcproject',
            '.ffd', '.flc', '.flh', '.fli', '.flv', '.flx', '.gfp', '.gl', '.gom', '.grasp', '.gts', '.gvi', '.gvp',
            '.h264', '.hdmov',
            '.hkm', '.ifo', '.imovieproj', '.imovieproject', '.ircp', '.irf', '.ism', '.ismc', '.ismv', '.iva', '.ivf',
            '.ivr', '.ivs',
            '.izz', '.izzy', '.jss', '.jts', '.jtv', '.k3g', '.kmv', '.ktn', '.lrec', '.lsf', '.lsx', '.m15', '.m1pg',
            '.m1v', '.m21',
            '.m21', '.m2a', '.m2p', '.m2t', '.m2ts', '.m2v', '.m4e', '.m4u', '.m4v', '.m75', '.mani', '.meta', '.mgv',
            '.mj2', '.mjp',
            '.mjpg', '.mk3d', '.mkv', '.mmv', '.mnv', '.mob', '.mod', '.modd', '.moff', '.moi', '.moov', '.mov',
            '.movie', '.mp21',
            '.mp21', '.mp2v', '.mp4', '.mp4v', '.mpe', '.mpeg', '.mpeg1', '.mpeg4', '.mpf', '.mpg', '.mpg2',
            '.mpgindex', '.mpl',
            '.mpl', '.mpls', '.mpsub', '.mpv', '.mpv2', '.mqv', '.msdvd', '.mse', '.msh', '.mswmm', '.mts', '.mtv',
            '.mvb', '.mvc',
            '.mvd', '.mve', '.mvex', '.mvp', '.mvp', '.mvy', '.mxf', '.mxv', '.mys', '.ncor', '.nsv', '.nut', '.nuv',
            '.nvc', '.ogm',
            '.ogv', '.ogx', '.osp', '.otrkey', '.pac', '.par', '.pds', '.pgi', '.photoshow', '.piv', '.pjs',
            '.playlist', '.plproj',
            '.pmf', '.pmv', '.pns', '.ppj', '.prel', '.pro', '.prproj', '.prtl', '.psb', '.psh', '.pssd', '.pva',
            '.pvr', '.pxv',
            '.qt', '.qtch', '.qtindex', '.qtl', '.qtm', '.qtz', '.r3d', '.rcd', '.rcproject', '.rdb', '.rec', '.rm',
            '.rmd', '.rmd',
            '.rmp', '.rms', '.rmv', '.rmvb', '.roq', '.rp', '.rsx', '.rts', '.rts', '.rum', '.rv', '.rvid', '.rvl',
            '.sbk', '.sbt',
            '.scc', '.scm', '.scm', '.scn', '.screenflow', '.sec', '.sedprj', '.seq', '.sfd', '.sfvidcap', '.siv',
            '.smi', '.smi',
            '.smil', '.smk', '.sml', '.smv', '.spl', '.sqz', '.srt', '.ssf', '.ssm', '.stl', '.str', '.stx', '.svi',
            '.swf', '.swi',
            '.swt', '.tda3mt', '.tdx', '.thp', '.tivo', '.tix', '.tod', '.tp', '.tp0', '.tpd', '.tpr', '.trp', '.ts',
            '.tsp', '.ttxt',
            '.tvs', '.usf', '.usm', '.vc1', '.vcpf', '.vcr', '.vcv', '.vdo', '.vdr', '.vdx', '.veg', '.vem', '.vep',
            '.vf', '.vft',
            '.vfw', '.vfz', '.vgz', '.vid', '.video', '.viewlet', '.viv', '.vivo', '.vlab', '.vob', '.vp3', '.vp6',
            '.vp7', '.vpj',
            '.vro', '.vs4', '.vse', '.vsp', '.w32', '.wcp', '.webm', '.wlmp', '.wm', '.wmd', '.wmmp', '.wmv', '.wmx',
            '.wot', '.wp3',
            '.wpl', '.wtv', '.wve', '.wvx', '.xej', '.xel', '.xesc', '.xfl', '.xlmv', '.xmv', '.xvid', '.y4m', '.yog',
            '.yuv', '.zeg',
            '.zm1', '.zm2', '.zm3', '.zmv')

        count = 0

        self.dirname = "."
        self.file_list = os.listdir(self.dirname)
        self.file_list.sort()
        self.list_item_info = []
        for I in self.file_list:
            self.list_item_info.append(self.get_file_info(I))
        if self.model.window_source_sort_by_name == 1:
            list_file = []
            list_dir = []
            if self.model.window_source_sort_name_order == 1:
                for TMP in self.file_list:
                    if os.path.isfile(TMP):
                        list_file.append(TMP)
                    else:
                        list_dir.append(TMP)

                list_file.sort()
                list_dir.sort()
            else:
                for TMP in reversed(self.file_list):
                    if os.path.isfile(TMP):
                        list_file.append(TMP)
                    else:
                        list_dir.append(TMP)

            self.file_list = list_dir + list_file

        elif self.model.window_source_sort_by_size == 1:
            self.list_item_info.sort(key=itemgetter(4))
            tmp_file = []
            if self.model.window_source_sort_size_order == 1:
                for TMP in self.list_item_info:
                    tmp_file.append(TMP[0])
            else:
                for TMP in reversed(self.list_item_info):
                    tmp_file.append(TMP[0])
            self.file_list = tmp_file
        elif self.model.window_source_sort_by_time == 1:
            self.list_item_info.sort(key=itemgetter(5))
            tmp_file = []
            if self.model.window_source_sort_time_order == 0:
                for TMP in self.list_item_info:
                    tmp_file.append(TMP[0])
            else:
                for TMP in reversed(self.list_item_info):
                    tmp_file.append(TMP[0])
            self.file_list = tmp_file
        self.file_list.insert(0, "..")
        self.model.window_source_lsdir_item_number = len(self.file_list)

        # it_can_be_display
        line = 0
        for _ in range(self.Y + 2, self.YParentMax - 3):
            line = line + 1
        self.model.window_source_item_it_can_be_display = line - 1

        Label_dirname = " " + os.getcwd() + " "
        Label_dirname = Label_dirname.replace(expanduser("~"), "~")

        self.Parent.addstr(0, self.X + 1, "<", curses.color_pair(3))
        self.Parent.addstr(0, self.X + 3, str(Label_dirname), curses.color_pair(4))
        self.Parent.addstr(0, self.XParentMax - 2, ">", curses.color_pair(3))
        self.Parent.addstr(0, self.XParentMax - 6, ".[^]", curses.color_pair(3))

        self.Parent.addstr(self.Y + 1, ((self.XParentMax - 14 - 7) / 2 ) - (len(name_text) / 2), name_text,
                           curses.color_pair(7) | curses.A_BOLD)
        self.Parent.addstr(self.Y + 1, self.XParentMax - 14 - 6, size_text, curses.color_pair(7) | curses.A_BOLD)
        self.Parent.addstr(self.Y + 1, self.XParentMax - 13, mtime_text, curses.color_pair(7) | curses.A_BOLD)
        #self.Parent.addch(self.YParentMax -3 ,self.X+1,curses.ACS_HLINE)
        self.Parent.vline(self.Y + 1, self.XParentMax - 14, curses.ACS_VLINE, self.YParentMax - 3)
        self.Parent.vline(self.Y + 1, self.XParentMax - 14 - 8, curses.ACS_VLINE, self.YParentMax - 3)


        #for name in names:
        #    file_list.append((not os.path.isdir(name), name))




        #FOR qui occupe toute la fenetre avec des liste de fichiers
        for I in range(self.Y + 2, self.YParentMax - 3):
            #self.Parent.addstr(I, self.X + 1, str(" " * int(self.XParentMax-2)), curses.color_pair(3))
            if count < len(self.file_list):
                try:
                    file_info_list = self.get_file_info(
                        os.path.join(self.dirname, self.file_list[count + self.model.window_source_item_list_scroll]))
                except:
                    file_info_list = self.get_file_info(
                        self.file_list[count + self.model.window_source_item_list_scroll])

                self.Parent.addstr(I, self.X + 1, file_info_list[0], curses.color_pair(3))
                self.Parent.addstr(I, (self.XParentMax - 14 - len(str(file_info_list[2]))), str(file_info_list[2]),
                                   curses.color_pair(3))
                self.Parent.addstr(I, self.XParentMax - 13, file_info_list[3], curses.color_pair(3))

                #Selected Line
                if self.model.window_source_selected_item == count:
                    self.Parent.addstr(I, self.X + 1, str(" " * int(self.XParentMax - 2)), curses.color_pair(1))
                    self.model.window_source_selected_item_list_value = file_info_list
                    if os.path.isfile(file_info_list[1]):
                        self.Parent.addstr(I, self.X + 1, str(" " + file_info_list[0]), curses.color_pair(1))
                    else:
                        self.Parent.addstr(I, self.X + 1, str("/" + file_info_list[0]), curses.color_pair(1))

                    self.Parent.addstr(I, (self.XParentMax - 14 - len(str(file_info_list[2]))), str(file_info_list[2]),
                                       curses.color_pair(1))
                    self.Parent.addstr(I, self.XParentMax - 13, file_info_list[3], curses.color_pair(1))

                    self.Parent.vline(I, self.XParentMax - 14, curses.ACS_VLINE, 1, curses.color_pair(1))
                    self.Parent.vline(I, self.XParentMax - 14 - 8, curses.ACS_VLINE, 1, curses.color_pair(1))
                else:

                    if os.path.isfile(file_info_list[1]):
                        #Give color to video file type
                        if file_info_list[1].endswith(video_file_extensions):
                            self.Parent.addstr(I, self.X + 1, str(" " + file_info_list[0]), curses.color_pair(8))
                            self.Parent.addstr(I, (self.XParentMax - 14 - len(str(file_info_list[2]))),
                                               str(file_info_list[2]), curses.color_pair(8))
                            self.Parent.addstr(I, self.XParentMax - 13, file_info_list[3], curses.color_pair(8))
                        else:
                            self.Parent.addstr(I, self.X + 1, str(" " + file_info_list[0]), curses.color_pair(3))
                            self.Parent.addstr(I, (self.XParentMax - 14 - len(str(file_info_list[2]))),
                                               str(file_info_list[2]), curses.color_pair(3))
                            self.Parent.addstr(I, self.XParentMax - 13, file_info_list[3], curses.color_pair(3))
                    else:
                        self.Parent.addstr(I, self.X + 1, str("/" + file_info_list[0]),
                                           curses.color_pair(3) | curses.A_BOLD)
                        self.Parent.addstr(I, (self.XParentMax - 14 - len(str(file_info_list[2]))),
                                           str(file_info_list[2]), curses.color_pair(3) | curses.A_BOLD)
                        self.Parent.addstr(I, self.XParentMax - 13, file_info_list[3],
                                           curses.color_pair(3) | curses.A_BOLD)
            count = count + 1

        self.Parent.hline(self.YParentMax - 3, self.X + 1, curses.ACS_HLINE, self.XParentMax - 2)
        self.Parent.addstr(self.YParentMax - 2, self.X + 1, self.model.window_source_selected_item_list_value[0],
                           curses.color_pair(3))
        #Window.refresh()

    def MouseClicked(self, MouseEvent):
        (id, x, y, z, event) = MouseEvent
        if (self.YParent + 3 <= y <= self.YParent + 3) and (
                            self.X + self.XParent <= x < self.X + self.XParent + self.Width - 1):
            return 1
        else:
            return 0

    def get_file_info(self, filename):
        file_info_list = []

        #0 Display Name
        file_info_list.append(os.path.basename(filename))
        #1 Full Path
        file_info_list.append(filename)
        #2 Display Size
        if not os.path.basename(filename) == "..":
            if os.path.isfile(filename):
                st = os.stat(filename)
                size = "{0:.0S}".format(self.size(st.st_size))
                file_info_list.append(size)
            else:
                x = os.statvfs(filename)
                file_info_list.append(x.f_bsize)
        else:
            file_info_list.append("UP--DIR")


        #3 Display Mtime
        st = os.stat(filename)
        file_info_list.append(time.strftime("%e %h %H:%M", time.localtime(st.st_mtime)))

        #Data for short
        #4 Size
        file_info_list.append(st.st_size)
        #5 mtime
        file_info_list.append(st.st_mtime)

        return file_info_list

    class size(long):
        """ define a size class to allow custom formatting
            Implements a format specifier of S for the size class - which displays a human readable in b, kb, Mb etc 
        """

        def __format__(self, fmt):
            if fmt == "" or fmt[-1] != "S":
                if fmt[-1].tolower() in ['b', 'c', 'd', 'o', 'x', 'n', 'e', 'f', 'g', '%']:
                    # Numeric format.
                    return long(self).__format__(fmt)
                else:
                    return str(self).__format__(fmt)

            val, s = float(self), ["", "K", "M", "G", "T", "P"]
            if val < 1:
                # Can't take log(0) in any base.
                i, v = 0, 0
            else:
                i = int(math.log(val, 1024)) + 1
                v = val / math.pow(1024, i)
                v, i = (v, i) if v > 0.5 else (v * 1024, i - 1)
            return ("{0:{1}f}" + s[i]).format(v, fmt[:-1])

    def MouseClicked(self, MouseEvent):
        (id, x, y, z, event) = MouseEvent
        if (self.YParent + 3 <= y <= self.YParent + 3) and (
                            self.X + self.XParent <= x < self.X + self.XParent + self.Width - 1):
            return 1
        else:
            return 0