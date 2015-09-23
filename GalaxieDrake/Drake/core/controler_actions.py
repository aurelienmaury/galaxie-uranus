#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: Jérôme ORNECH alias "Tuux" <tuxa@rtnp.org> all rights reserved
__author__ = 'Tuux'

import os
import sys
import glob
import subprocess
import re


class ScanDir(object):
    def __init__(self, directory, model, viewer):
        self.viewer = viewer
        self.model = model

        self.taskspooler_path = self.check_taskspooler
        self.nice_path = self.check_nice
        self.working_dir = os.path.realpath(directory)
        self.transcoder_path = self.check_transcoder
        self.nice_priority = '15'

        # Test if the script can run without common errors
        if self.working_dir is not None and self.transcoder_path is not None:
            if not os.access(self.working_dir, os.F_OK):
                self.viewer.display_info("Error: " + self.working_dir + " don't exist")
            elif not os.access(self.working_dir, os.R_OK):
                self.viewer.display_info("Error: " + self.working_dir + " can't be read")
            elif not os.access(self.transcoder_path, os.R_OK):
                self.viewer.display_info("Error: " + self.transcoder_path + " can't be read")
                self.viewer.display_message("Error: 'transcoder.py' is require")
            elif not os.access(self.transcoder_path, os.X_OK):
                self.viewer.display_info("Error: " + self.transcoder_path + " haven't executable permission")
            else:
                # Everything is test we can start to scan directory
                files_list_to_transcode = list()

    def add_transcode_task(self, file_path):
        cmd = list()
        cmd.append(unicode(self.taskspooler_path, 'utf-8'))
        if self.nice_path:
            cmd.append(unicode(self.nice_path, 'utf-8'))
            cmd.append(unicode("-n", 'utf-8'))
            cmd.append(unicode(self.nice_priority, 'utf-8'))

        cmd.append(unicode(self.transcoder_path, 'utf-8'))
        cmd.append(unicode(file_path, 'utf-8'))
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
            searching_command_txt += str(self.nice_priority)
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
            return "unknow"

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
            return 'Task Spooler v(unknown)'

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
            return 'Nice v(unknown)'

    def _getDirs(self, base):
        return [x for x in glob.iglob(os.path.join(base, '*')) if os.path.isdir(x)]

    def rglob(self, base, pattern):
        tmp_list = []
        tmp_list.extend(glob.glob(os.path.join(base, pattern)))
        dirs = self._getDirs(base)
        if len(dirs):
            for d in dirs:
                tmp_list.extend(self.rglob(os.path.join(base, d), pattern))
        return tmp_list

    @staticmethod
    def which(program):
        # It's execute from core/controller
        os.environ["PATH"] += os.pathsep + os.path.join(os.path.dirname(os.path.realpath(__file__)), './..')

        def is_exe(f_path):
            return os.path.isfile(f_path) and os.access(f_path, os.X_OK)

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

    @property
    def check_transcoder(self):
        if not self.which("transcoder.py"):
            self.viewer.display_info(
                "Error: Please install 'transcoder.py' or verify it is aviable on your $PATH env var"
            )
            self.viewer.display_message("Error: Scan will abort ...")
            return None
        else:
            return self.which("transcoder.py")

    @property
    def check_taskspooler(self):
        if not self.which("tsp"):
            self.viewer.display_info("Error: Please install 'task-spooler' or verify it is aviable on your $PATH env var")
            self.viewer.display_message("Error: Scan will abort ...")
            return None
        else:
            return self.which("tsp")

    @property
    def check_nice(self):
        if not self.which("nice"):
            self.viewer.display_info("Warning: Nice is require, for fixe low process priority")
            self.viewer.display_message("Warning: Scan will continue without ...")
            return None
        else:
            return self.which("nice")
