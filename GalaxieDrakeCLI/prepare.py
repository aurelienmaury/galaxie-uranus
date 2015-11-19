#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: Jérôme ORNECH alias "Tuux" <tuxa@rtnp.org> all rights reserved
__author__ = 'Tuux'

import os
import glob
import fnmatch
import sys
import subprocess
import re

# ######################################
# #####DEFINE SOME BASIC VARIABLES######
# ######################################
scriptname = os.path.basename(sys.argv[0])
scriptname_title = os.path.basename(os.path.splitext(sys.argv[0])[0])
scriptname_title = scriptname_title.title()
version = '0.3'

# User Setting #
################

# In case of multi-resolution file like: "filename - 1080p.mkv"
# All multi-resolution files will be ignore during scan
# That because they file are not consider as transcoding source.
file_pattern_exception = '* - *p.mkv'

# Transcoding take time then be nice with the system,
# is not trivial, that permit to use the system for a other task
# See: https://en.wikipedia.org/wiki/Nice_%28Unix%29
nice_priority = '15'

# List of extension file the script will search during the scan

extension_list = [
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
# Limite the search
# extension_list = ['*.ts']

# Add path where the script is store to the environement var PATH
# It permit to search transcoder.py by exemple
os.environ["PATH"] += os.pathsep + os.path.dirname(os.path.realpath(__file__))


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


def get_dirs_list(base):
    return [x for x in glob.iglob(os.path.join(base, '*')) if os.path.isdir(x)]


def cli_progress_bar(label, val, end_val, bar_length):
    bar_length = int(bar_length - int(len(label) + 7))
    percent = float(val) / end_val
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\r" + label + "[{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


class prepare(object):
    def __init__(self, workingdir):
        global query_label
        self.taskspooler_path = self.check_taskspooler
        self.nice_path = self.check_nice
        # ######################################
        # ## Small Header just for fun #########
        # ######################################
        print ""
        if not self.nice_path:
            print scriptname_title + " v" + version + " / " + self.tsp_get_version()
        else:
            print scriptname_title + " v" + version + " / " + self.tsp_get_version() + " / " + self.nice_get_version()
        #######################################
        self.workingdir = os.path.realpath(workingdir)
        self.transcoder_path = self.check_transcoder
        # Test if the script can run without common errors
        if not os.access(self.workingdir, os.F_OK):
            print "Error: " + self.workingdir + " dont exist"
            sys.exit(1)
        elif not os.access(self.workingdir, os.R_OK):
            print "Error: " + self.workingdir + " can't be read"
            sys.exit(1)
        elif not os.access(self.transcoder_path, os.R_OK):
            print "Error: " + self.transcoder_path + " can't be read"
            print "Error: \"transcoder.py is require \""
            print "Error: " + scriptname.title() + " will abort ..."
            sys.exit(1)
        elif not os.access(self.transcoder_path, os.X_OK):
            print "Error: " + self.transcoder_path + " haven't executable permission"
            sys.exit(1)
        else:
            # Everything is test we can start to scan directory
            files_list_to_transcode = list()
            print " Transcoder Path: " + self.transcoder_path
            print " Source Directory: " + self.workingdir + "/"
            print ""
            print "Searching for: "
            for file_pattern in extension_list:
                print " " + file_pattern.upper()[2:],
            print ""
            print " Exception Pattern: \"" + file_pattern_exception + "\""

            # Counter for the Text Progress Bar
            count = 1
            # For each file patterns extension
            for file_pattern in extension_list:

                # Call Text Progress Bar
                rows, columns = os.popen('stty size', 'r').read().split()
                cli_progress_bar(
                    "Scaning for " + file_pattern.upper()[2:] + ": ",
                    int(round(100 * count / len(extension_list))),
                    100,
                    int(columns)
                )

                # Scan directory recursivlly for Lower and Upper case file extension
                files_lower = self.rglob(self.workingdir, file_pattern.lower())
                files_upper = self.rglob(self.workingdir, file_pattern.upper())

                # Add Lower case file extension to the final file list to encode
                if len(files_lower):
                    for file_lower in files_lower:
                        if not fnmatch.fnmatch(file_lower, file_pattern_exception):
                            files_list_to_transcode.append(file_lower)
                # Add Upper case file extension to the final file list to encode
                if len(files_upper):
                    for file_upper in files_upper:
                        if not fnmatch.fnmatch(file_upper, file_pattern_exception):
                            files_list_to_transcode.append(file_upper)

                # Counter for the Text Progress Bar
                count += 1

            # Clear the Text Progress Bar line
            sys.stdout.write("\x1b[2K")
            sys.stdout.write("\r")

            # Print summary of file to encode:
            if len(files_list_to_transcode):
                print ""
                if len(files_list_to_transcode) == 1:
                    print "1 File found:"
                else:
                    print str(len(files_list_to_transcode)) + " Files founds:"
                for file_to_transcode in files_list_to_transcode:
                    print " " + file_to_transcode

            # Creat one task by file to transcode and send it to taskspooler queue
            print ""
            if len(files_list_to_transcode):
                if len(files_list_to_transcode) == 1:
                    query_label = "Do you want creat transcoding task for it file ?"
                else:
                    query_label = "Do you want creat transcoding tasks for they " + str(
                        len(files_list_to_transcode)) + " files ?"
            if len(files_list_to_transcode) and query_yes_no(query_label):
                # Print a Summary about number of files to transcode
                print ""
                if len(files_list_to_transcode) == 1:
                    print "Creation of 1 task:"
                else:
                    print "Creation of " + str(len(files_list_to_transcode)) + " tasks:"
                print ""
                # Add task(s)
                count = 1
                for file_to_transcode in files_list_to_transcode:
                    sys.stdout.write("\rTask: " + str(count) + ", " + file_to_transcode + "\n")
                    sys.stdout.flush()
                    job_exist = self.tsp_check_if_job_exist(file_to_transcode)
                    if not job_exist:
                        self.add_transcode_task(file_to_transcode)
                    else:
                        print ""
                    count += 1
                    print ""
            else:
                print "Nothing to do ..."

    def add_transcode_task(self, file_to_encode):
        cmd = list()
        cmd.append(unicode(self.taskspooler_path, 'utf-8'))
        if self.nice_path:
            cmd.append(unicode(self.nice_path, 'utf-8'))
            cmd.append(unicode("-n", 'utf-8'))
            cmd.append(unicode(nice_priority, 'utf-8'))

        cmd.append(unicode(self.transcoder_path, 'utf-8'))
        cmd.append(unicode(file_to_encode, 'utf-8'))
        # output = None
        output = subprocess.check_output(cmd)
        if output:
            output = output.rstrip(os.linesep)
            print "ID: " + output + ", State: " + self.tsp_job_status(output)
            print "" + str(self.tsp_job_information(output)[0])

    def tsp_check_if_job_exist(self, file_to_transcode):
        # Constitute Searching Pattern inside the TaskSpooler
        searching_command_txt = ""
        if self.nice_path:
            searching_command_txt += str(self.nice_path)
            searching_command_txt += " "
            searching_command_txt += str("-n")
            searching_command_txt += " "
            searching_command_txt += str(nice_priority)
            searching_command_txt += " "
        searching_command_txt += str(self.transcoder_path)
        searching_command_txt += " "
        searching_command_txt += str(file_to_transcode)

        # Deal with job_list
        job_list = (self.tsp_get_job_list())
        if job_list:
            for i, element_list in enumerate(job_list):
                if element_list[3] == searching_command_txt:
                    sys.stdout.write("Task all ready in queue with ID: " + element_list[0])
                    sys.stdout.flush()
                    return 1
        return 0

        # sys.exit(0)

    def tsp_job_status(self, jobid):
        cmd = list()
        cmd.append(unicode(self.taskspooler_path, 'utf-8'))
        cmd.append(unicode("-s", 'utf-8'))
        cmd.append(unicode(jobid, 'utf-8'))
        output = subprocess.check_output(cmd)
        if output:
            output = output.rstrip(os.linesep)
            return output
        else:
            return "unknown"

    def tsp_job_information(self, jobid):
        cmd = list()
        output = list()
        cmd.append(unicode(self.taskspooler_path, 'utf-8'))
        cmd.append(unicode("-i", 'utf-8'))
        cmd.append(unicode(jobid, 'utf-8'))
        output.append(subprocess.check_output(cmd))
        if output:
            tmp_output = re.split(r'\n', output[0])
            tmp_output.pop(3)
            return tmp_output
        else:
            return None

    def tsp_get_job_list(self):
        cmd = list()
        output = list()
        tmp_job_list = list()
        clear_list = list()
        cmd.append(unicode(self.taskspooler_path, 'utf-8'))
        cmd.append(unicode("-l", 'utf-8'))
        output.append(subprocess.check_output(cmd))
        if output:
            # One job by line
            for job in output:
                tmp_job_list.append(job)
            tmp_job_list = re.split(r'\n', tmp_job_list[0])
            # One argv by TAB
            for i in tmp_job_list:
                ii = re.split(r'\s{2,}', i)
                if len(ii) == 4:
                    clear_list.append(ii)
            output = clear_list
            return output
        else:
            return None

    def tsp_get_version(self):
        cmd = list()
        output = list()
        cmd.append(unicode(self.taskspooler_path, 'utf-8'))
        cmd.append(unicode("-V", 'utf-8'))
        output.append(subprocess.check_output(cmd))
        if output:
            tmp_output = re.split(r' - ', output[0])
            return tmp_output[0]
        else:
            return "Task Spooler v(unknown)"

    def nice_get_version(self):
        cmd = list()
        output = list()
        cmd.append(unicode(self.nice_path, 'utf-8'))
        cmd.append(unicode("--version", 'utf-8'))
        output.append(subprocess.check_output(cmd))
        if output:
            tmp_output = re.split(r'\n', output[0])
            return tmp_output[0].title()
        else:
            return "Nice v(unknown)"

    def rglob(self, base, pattern):
        list_tmp = []
        list_tmp.extend(glob.glob(os.path.join(base, pattern)))
        dirs = get_dirs_list(base)
        if len(dirs):
            for d in dirs:
                list_tmp.extend(self.rglob(os.path.join(base, d), pattern))
        return list_tmp

    @property
    def check_transcoder(self):
        if not which("transcoder.py"):
            print "Error: Transcoder is require, for enable transcoding queue"
            print "Error: Please install \"transcoder.py\" or verify it is aviable on your $PATH env var"
            print "Error: " + scriptname_title + " will abort ..."
            sys.exit(1)
        else:
            return which("transcoder.py")

    @property
    def check_taskspooler(self):
        if not which("tsp"):
            print "Error: Task Spooler is require, for enable transcoding queue"
            print "Error: Please install \"task-spooler\" or verify it is aviable on your $PATH env var"
            print "Error: " + scriptname_title + " will abort ..."
            sys.exit(1)
        else:
            return which("tsp")

    @property
    def check_nice(self):
        if not which("nice"):
            print "Warning: Nice is require, for fixe low process priority"
            print "Warning: " + scriptname_title + " will continue without ..."
            return None
        else:
            return which("nice")


# #####Check if a parameter is all ready present######
# ####################################################
if len(sys.argv) < 2:
    print ""
    print scriptname_title + " v" + version
    print " Please, invoke it script with the path of a directory"
    print " It directory will be use as Movie source directory"
    print " Fews Exemples: "
    print " ./" + scriptname + " ./"
    print " ./" + scriptname + " ../a/other/directory"
    print " ./" + scriptname + " /full/path/to/the/directory"
    print " ./" + scriptname + " \"/full/path/to/the/directory/With space name/\""
    exit(1)

# #####SOURCE FILE CHECK######
# ###########################
elif not os.path.isdir(sys.argv[1]):
    print ""
    print scriptname_title + " v" + version
    print " Error: Directory not found "
    print " Maybe wrong path or missing permissions?"
    print " Please, invoke it script with the path of a valid directory"
    print " Fews Exemples: "
    print " ./" + scriptname + " ./"
    print " ./" + scriptname + " ../a/other/directory"
    print " ./" + scriptname + " /full/path/to/the/directory/"
    print " ./" + scriptname + " \"/full/path/to/the/directory/With space name\""
    exit(1)

else:
    # Take the first and unic parameter and consider it is a directory
    # APPLICATION START
    p = prepare(sys.argv[1])
