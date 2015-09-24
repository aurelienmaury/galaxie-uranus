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
import fnmatch


class ScanDir(object):
    def __init__(self, model, viewer):
        self.viewer = viewer
        self.model = model

        # Test if the script can run without common errors
        if not os.access(self.model.scanning_directory, os.F_OK):
            self.viewer.display_info("Error: " + self.model.scanning_directory + " don't exist")
        elif not os.access(self.model.scanning_directory, os.R_OK):
            self.viewer.display_info("Error: " + self.model.scanning_directory + " can't be read")
        else:
            # Everything is test we can start to scan directory
            files_list_to_transcode = list()
            # Counter for the Text Progress Bar
            count = 1
            # For each file patterns extension
            for self.model.scanning_file_pattern in self.model.searching_extension_list:
                # Call Text Progress Bar
                self.model.scanning_percent = int(round(100 * count / len(self.model.searching_extension_list)))
                # Scan directory recursivlly for Lower and Upper case file extension
                files_lower = self.rglob(self.model.scanning_directory, self.model.scanning_file_pattern.lower())
                files_upper = self.rglob(self.model.scanning_directory, self.model.scanning_file_pattern.upper())

                # Add Lower case file extension to the final file list to encode
                if len(files_lower):
                    for file_lower in files_lower:
                        if not fnmatch.fnmatch(file_lower, self.model.scanning_file_pattern):
                            self.model.files_list_to_transcode.append(file_lower)
                # Add Upper case file extension to the final file list to encode
                if len(files_upper):
                    for file_upper in files_upper:
                        if not fnmatch.fnmatch(file_upper, self.model.scanning_file_pattern):
                            self.model.files_list_to_transcode.append(file_upper)

                # Counter for the Text Progress Bar
                count += 1
                # Set progress bar value
                #screen.refresh()


    def add_transcode_task(self, file_path):
        cmd = list()
        cmd.append(unicode(self.model.taskspooler_path, 'utf-8'))
        if self.model.nice_path:
            cmd.append(unicode(self.model.nice_path, 'utf-8'))
            cmd.append(unicode("-n", 'utf-8'))
            cmd.append(unicode(self.model.nice_priority, 'utf-8'))

        cmd.append(unicode(self.model.transcoder_path, 'utf-8'))
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
        if self.model.nice_path:
            searching_command_txt += str(self.model.nice_path)
            searching_command_txt += " "
            searching_command_txt += str("-n")
            searching_command_txt += " "
            searching_command_txt += str(self.model.nice_priority)
            searching_command_txt += " "
        searching_command_txt += str(self.model.transcoder_path)
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
        cmd.append(unicode(self.model.taskspooler_path, 'utf-8'))
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
        cmd.append(unicode(self.model.taskspooler_path, 'utf-8'))
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
        cmd.append(unicode(self.model.taskspooler_path, 'utf-8'))
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
        cmd.append(unicode(self.model.taskspooler_path, 'utf-8'))
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
        cmd.append(unicode(self.model.nice_path, 'utf-8'))
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
