#!/usr/bin/python

__author__ = 'tuxa'

import os
import math
import time


def disk_usage(path):
    st = os.statvfs(path)
    total = (st.f_blocks * st.f_frsize)
    used = (st.f_bsize * st.f_bavail)

    try:
        percent = ret = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    line = str(sizeof(used) + "/" + sizeof(total) + " (" + str(int(percent)) + "%)")
    line = " " + line + " "
    return line


def sizeof(num):
    suffix = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']
    i = 0 if num < 1 else int(math.log(num, 1024)) + 1
    v = num / math.pow(1024, i)
    v, i = (v, i) if v > 0.5 else (v * 1024, (i - 1 if i else 0))
    return str(str(int(round(v, 0))) + suffix[i])


def resize_text(text, max_width, separator='~'):
    if max_width < len(text):
        return text[:(max_width / 2) - 1] + separator + text[-max_width / 2:]
    else:
        return text


def secs_to_human_read(secs):
    if secs:
        x = int(float(secs))
        seconds = x % 60
        x /= 60
        minutes = x % 60
        x /= 60
        hours = x % 24
        x /= 24
        days = x
        # convert days to hours
        days_hours = days * 24
        text_to_return = str("")
        if days:
            hours += days_hours
        else:
            text_to_return += str(str('{0:02d}'.format(hours)) + ":")
            text_to_return += str(str('{0:02d}'.format(minutes)) + ":")
            text_to_return += str(str('{0:02d}'.format(seconds)) + "")
        if text_to_return:
            return str(text_to_return)
        else:
            return ''
    else:
        return ''


def get_file_info_list(filename, model):
    file_info_list = list()
    # 0 Name to Display
    file_info_list.append(os.path.basename(filename))
    # 1 Full Path
    file_info_list.append(filename)
    # 2 Size to Display
    if not os.path.basename(filename) == "..":
        if os.path.isfile(filename):
            st = os.stat(filename)
            size = sizeof(st.st_size)
            file_info_list.append(size)
        else:
            x = os.statvfs(filename)
            file_info_list.append(x.f_bsize)
    else:
        file_info_list.append(model.window_source_rep_sup_text)
    # 3 Time to Display
    st = os.stat(filename)

    # file_info_list.append(time.strftime("%e %b %H:%M", time.localtime(st.st_mtime)))
    file_info_list.append(time.strftime("%d/%m/%Y  %H:%M", time.localtime(st.st_mtime)))
    # 4 Size value used by the shorted process
    file_info_list.append(st.st_size)
    # 5 Mtime value used by the shorted process
    file_info_list.append(st.st_mtime)
    # Yes it return somathing, it's a live !
    return file_info_list


def display_up_time():
    try:
        f = open("/proc/uptime")
        contents = f.read().split()
        f.close()
    except:
        return "Cannot open uptime file: /proc/uptime"

    total_seconds = float(contents[0])

    # Helper vars:
    MINUTE  = 60
    HOUR    = MINUTE * 60
    DAY     = HOUR * 24

    # Get the days, hours, etc:
    days    = int( total_seconds / DAY )
    hours   = int( ( total_seconds % DAY ) / HOUR )
    minutes = int( ( total_seconds % HOUR ) / MINUTE )
    seconds = int( total_seconds % MINUTE )

    # Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
    text_to_return = "Uptime: "
    if days:
        text_to_return += str(days) + " " + (days == 1 and "day" or "days") + ", "
        text_to_return += str(str('{0:02d}'.format(hours)) + ":")
        text_to_return += str(str('{0:02d}'.format(minutes)) + ":")
        text_to_return += str(str('{0:02d}'.format(seconds)) + "")
    else:
        text_to_return += str(str('{0:02d}'.format(hours)) + ":")
        text_to_return += str(str('{0:02d}'.format(minutes)) + ":")
        text_to_return += str(str('{0:02d}'.format(seconds)) + "")
    return text_to_return
