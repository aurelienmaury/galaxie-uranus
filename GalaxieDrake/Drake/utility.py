#!/usr/bin/python

__author__ = 'tuxa'

import os
import math
import time
import platform
import subprocess
import re


def get_processor_info():
    if platform.system() == "Windows":
        return platform.processor()
    elif platform.system() == "Darwin":
        import os
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        command ="sysctl -n machdep.cpu.brand_string"
        return subprocess.check_output(command).strip()
    elif platform.system() == "Linux":
        command = "cat /proc/cpuinfo"
        all_info = subprocess.check_output(command, shell=True).strip()
        for line in all_info.split("\n"):
            if "model name" in line:
                return re.sub( ".*model name.*: ", "", line,1)
    return ""

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

"""
Bytes-to-human / human-to-bytes converter.
Based on: http://goo.gl/kTQMs
Working with Python 2.x and 3.x.

Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
License: MIT
"""

SYMBOLS = {
    'customary'     : ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'),
    'customary_ext' : ('byte', 'kilo', 'mega', 'giga', 'tera', 'peta', 'exa',
                       'zetta', 'iotta'),
    'iec'           : ('Bi', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'),
    'iec_ext'       : ('byte', 'kibi', 'mebi', 'gibi', 'tebi', 'pebi', 'exbi',
                       'zebi', 'yobi'),
}

def bytes2human(n, format='%(value).1f%(symbol)s', symbols='customary'):
    """
    Convert n bytes into a human readable string based on format.
    symbols can be either "customary", "customary_ext", "iec" or "iec_ext",
    see: http://goo.gl/kTQMs

      >>> bytes2human(0)
      '0.0 B'
      >>> bytes2human(0.9)
      '0.0 B'
      >>> bytes2human(1)
      '1.0 B'
      >>> bytes2human(1.9)
      '1.0 B'
      >>> bytes2human(1024)
      '1.0 K'
      >>> bytes2human(1048576)
      '1.0 M'
      >>> bytes2human(1099511627776127398123789121)
      '909.5 Y'

      >>> bytes2human(9856, symbols="customary")
      '9.6 K'
      >>> bytes2human(9856, symbols="customary_ext")
      '9.6 kilo'
      >>> bytes2human(9856, symbols="iec")
      '9.6 Ki'
      >>> bytes2human(9856, symbols="iec_ext")
      '9.6 kibi'

      >>> bytes2human(10000, "%(value).1f %(symbol)s/sec")
      '9.8 K/sec'

      >>> # precision can be adjusted by playing with %f operator
      >>> bytes2human(10000, format="%(value).5f %(symbol)s")
      '9.76562 K'
    """
    n = int(n)
    if n < 0:
        raise ValueError("n < 0")
    symbols = SYMBOLS[symbols]
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i+1)*10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return format % locals()
    return format % dict(symbol=symbols[0], value=n)

def human2bytes(s):
    """
    Attempts to guess the string format based on default symbols
    set and return the corresponding bytes as an integer.
    When unable to recognize the format ValueError is raised.

      >>> human2bytes('0 B')
      0
      >>> human2bytes('1 K')
      1024
      >>> human2bytes('1 M')
      1048576
      >>> human2bytes('1 Gi')
      1073741824
      >>> human2bytes('1 tera')
      1099511627776

      >>> human2bytes('0.5kilo')
      512
      >>> human2bytes('0.1  byte')
      0
      >>> human2bytes('1 k')  # k is an alias for K
      1024
      >>> human2bytes('12 foo')
      Traceback (most recent call last):
          ...
      ValueError: can't interpret '12 foo'
    """
    init = s
    num = ""
    while s and s[0:1].isdigit() or s[0:1] == '.':
        num += s[0]
        s = s[1:]
    num = float(num)
    letter = s.strip()
    for name, sset in SYMBOLS.items():
        if letter in sset:
            break
    else:
        if letter == 'k':
            # treat 'k' as an alias for 'K' as per: http://goo.gl/kTQMs
            sset = SYMBOLS['customary']
            letter = letter.upper()
        else:
            raise ValueError("can't interpret %r" % init)
    prefix = {sset[0]:1}
    for i, s in enumerate(sset[1:]):
        prefix[s] = 1 << (i+1)*10
    return int(num * prefix[letter])


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


def disk_free():
    final_list = list()
    cmd = ['df', '-h']
    try:
        output = subprocess.check_output(cmd)
        if output:
            output = output.split('\n')
            for line in output:
                tmp_list = re.split(r'\s{2,}', line)
                # Clean the result of df command line
                if len(tmp_list) > 1 and not tmp_list[0] == 'udev' and not tmp_list[0] == 'tmpfs':
                    # Split again mount and percent
                    last = tmp_list[4]
                    percent, mount_point = re.split(r'\s', last)
                    tmp_list[4] = percent[:-1]
                    tmp_list.append(mount_point)
                    final_list.append(tmp_list)

            # Format mount point by add space for creat collumn
            maxi = 0
            for A in final_list:
                if len(A[5]) > maxi:
                    maxi = len(A[5])

            for A in final_list:
                A[5] += ' ' * (maxi - len(A[5]))

            return final_list
    except:
        return "Cannot open df -h"