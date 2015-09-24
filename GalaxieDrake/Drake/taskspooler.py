#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: Jérôme ORNECH alias "Tuux" <tuxa@rtnp.org> all rights reserved
__author__ = 'Tuux'

import os
import sys
import subprocess
import locale
import re


class TaskSpooler(object):
    def __init__(self, model):
        self.model = model
        self.command = self.model.taskspooler_path
        self.remove_args = '-r'
        self.state_args = '-s'
        self.info_args = '-i'
        self.output_args = '-o'
        self.version_args = '-V'
        self.get_output_args = '-c'
        locale.setlocale(locale.LC_ALL, '')
        self.code = locale.getpreferredencoding()
        self.decode = lambda b: b.decode(self.code)
        self._tasks = {}

    def check_taskspooler(self):
        if not self.which("tsp"):
            print "Error: Task Spooler is require, for enable transcoding queue"
            print "Error: Please install \"task-spooler\" or verify it is aviable on your $PATH env var"
            sys.exit(1)
        else:
            return self.which("tsp")
        return None

    def which(self, program):
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

    def remove_task(self, job_id=None):
        command = [self.command, self.remove_args]
        if job_id is not None:
            command.append(job_id)
        subprocess.call(command)

    def read_last_output_line(self, job_id=None):
        cmd = ['tail', '-n', '1']
        if job_id is not None:
            output_file = self.get_output(job_id)
        else:
            output_file = self.get_output()
        cmd.append(output_file)
        output = subprocess.check_output(cmd)
        if output:
            return output
        else:
            return ''



    def read_task_list(self):
        cmd = self.get_command([self.command])

        self._tasks = {}
        self.header = self.decode(next(cmd.stdout))

        for line in cmd.stdout:
            id_, task = self._parse_task(self.decode(line))
            self._tasks[id_] = task
        return self._tasks
        # self.order_tasks('id', reverse=True)

    def get_list(self):
        cmd = list()
        clear_list = list()
        job_info_list = list()
        cmd.append(self.command)
        output = subprocess.check_output(cmd)
        if output:
            # One job by line
            output = output.split('\n')
            for line in output:
                tmp_list = re.split(r'\s{2,}', line)
                if len(tmp_list) == 4 or len(tmp_list) == 5:
                    jobid = tmp_list[0]
                    state = tmp_list[1]
                    output = tmp_list[2]
                    if len(tmp_list) == 4:
                        elevel = ''
                        times = ''
                        command = tmp_list[3]
                    if len(tmp_list) == 5:
                        elevel = tmp_list[3]
                        times, command = tmp_list[4].split(' ', 1)
                    job_info = jobid + ';' + state + ';' + output + ';' + elevel + ';' + times + ';' + command
                    job_info_list = job_info.split(';')
                    clear_list.append(job_info_list)
                    #print job_info.split(';')
            #print clear_list
            return clear_list
        else:
            return None

    def get_info(self, jobid=None):
        command = [self.command, self.info_args]
        if jobid is not None:
            command.append(jobid)
        output = [subprocess.check_output(command)]
        if output:
            return output[0].rstrip(os.linesep)
        else:
            return "unknow"

    def get_state(self, jobid=None):
        command = [self.command, self.state_args]
        if jobid is not None:
            command.append(jobid)
        output = [subprocess.check_output(command)]
        if output:
            return output[0].rstrip(os.linesep)
        else:
            return "unknow"

    def get_command(self, jobid=None):
        if jobid is not None:
            job_infos = self.get_info(jobid)
        else:
            job_infos = self.get_info()

        job_infos = job_infos.split('\r')
        job_infos = job_infos[0].split('\n')

        if job_infos[1]:
            return job_infos[1].replace("Command: ", "")
        else:
            return None

    def get_output(self, jobid=None):
        command = [self.command, self.output_args]
        if jobid is not None:
            command.append(jobid)
        output = subprocess.check_output(command)
        if output:
            return output.rstrip(os.linesep)
        else:
            return None

    def get_state(self, jobid=None):
        command = [self.command, self.state_args]
        if jobid is not None:
            command.append(jobid)
        output = [subprocess.check_output(command)]
        if output:
            return output[0].rstrip(os.linesep)
        else:
            return "unknow"

    def get_version(self):
        command = [self.command, self.version_args]
        output = subprocess.check_output(command)
        if output:
            return output.split(" - ", 1)[0]
        else:
            return "Task Spooler v(unknow)"

    # Not on TaskSpooler
    def get_summary_info(self):
        list_to_return = list()
        job_list = self.get_list()
        job_number = len(job_list)
        job_running = 0
        job_queued = 0
        job_finished = 0
        job_finished_with_error = 0
        for I in job_list:
            if I[1] == "running":
                job_running += 1
            if I[1] == "queued":
                job_queued += 1
            if I[1] == "finished":
                job_finished += 1
                if not I[3] == "0":
                    job_finished_with_error += 1
        list_to_return.append(job_number)
        list_to_return.append(job_running)
        list_to_return.append(job_queued)
        list_to_return.append(job_finished)
        list_to_return.append(job_finished_with_error)
        return list_to_return

    def display_summary_info(self):
        job_list = self.get_list()
        job_number = len(job_list)
        job_running = 0
        job_queued = 0
        job_finished = 0
        job_finished_with_error = 0
        for I in job_list:
            if I[1] == "running":
                job_running += 1
            if I[1] == "queued":
                job_queued += 1
            if I[1] == "finished":
                job_finished += 1
                if not I[3] == "0":
                    job_finished_with_error += 1
        text_to_return = ""
        text_to_return += "TaskSpooler:"
        text_to_return += " "
        text_to_return += "Task"
        text_to_return += " "
        text_to_return += str(job_number)
        text_to_return += ", "
        text_to_return += "Running " + str(job_running)
        text_to_return += ", "
        text_to_return += "Queued " + str(job_queued)
        text_to_return += ", "
        text_to_return += "Finished " + str(job_finished)
        text_to_return += ", "
        text_to_return += "Error " + str(job_finished_with_error)
        return text_to_return


class Prepare(object):
    def __init__(self, working_dir):
        self.taskspooler_path = self.check_taskspooler()
        self.nice_path = self.check_nice()
        self.working_dir = os.path.realpath(working_dir)
        self.transcoder_path = self.check_transcoder()
        # Test if the script can run without common errors
        if not os.access(self.working_dir, os.F_OK):
            print "Error: " + self.working_dir + " dont exist"
            sys.exit(1)
        elif not os.access(self.working_dir, os.R_OK):
            print "Error: " + self.working_dir + " can't be read"
            sys.exit(1)
        elif not os.access(self.transcoder_path, os.R_OK):
            print "Error: " + self.transcoder_path + " can't be read"
            print "Error: \"transcoder.py is require \""
            sys.exit(1)
        elif not os.access(self.transcoder_path, os.X_OK):
            print "Error: " + self.transcoder_path + " haven't executable permission"
            sys.exit(1)
        else:
            # Everything is test we can start to scan directory
            files_list_to_transcode = list()
            print " Transcoder Path: " + self.transcoder_path
            print " Source Direcory: " + self.working_dir + "/"
            print ""
            print "Searching for: "
            for file_pattern in self.model.searching_extension_list:
                print " " + file_pattern.upper()[2:],
            print ""
            print " Exeption Pattern: \"" + file_pattern_exception + "\""

            # Counter for the Text Progress Bar
            count = 1
            # For each file patterns extension
            for file_pattern in extension_list:

                # Call Text Progress Bar
                rows, columns = os.popen('stty size', 'r').read().split()
                self.cli_progress_bar(
                    "Scaning for " + file_pattern.upper()[2:] + ": ",
                    int(round(100 * count / len(extension_list))),
                    100,
                    int(columns)
                )

                # Scan directory recursivlly for Lower and Upper case file extension
                files_lower = self.rglob(self.working_dir, file_pattern.lower())
                files_upper = self.rglob(self.working_dir, file_pattern.upper())

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
            if len(files_list_to_transcode) and self.query_yes_no(query_label):
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

    def query_yes_no(self, question, default="yes"):
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

    def cli_progress_bar(self, label, val, end_val, bar_length):
        bar_length = int(bar_length - int(len(label) + 7))
        percent = float(val) / end_val
        hashes = '#' * int(round(percent * bar_length))
        spaces = ' ' * (bar_length - len(hashes))
        sys.stdout.write("\r" + label + "[{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
        sys.stdout.flush()

    def add_transcode_task(self, file):
        cmd = list()
        cmd.append(unicode(self.taskspooler_path, 'utf-8'))
        if self.nice_path:
            cmd.append(unicode(self.nice_path, 'utf-8'))
            cmd.append(unicode("-n", 'utf-8'))
            cmd.append(unicode(hnice_priority, 'utf-8'))

        cmd.append(unicode(self.transcoder_path, 'utf-8'))
        cmd.append(unicode(file, 'utf-8'))
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
            searching_command_txt = searching_command_txt + str(self.nice_path)
            searching_command_txt = searching_command_txt + " "
            searching_command_txt = searching_command_txt + str("-n")
            searching_command_txt = searching_command_txt + " "
            searching_command_txt = searching_command_txt + str(nice_priority)
            searching_command_txt = searching_command_txt + " "
        searching_command_txt = searching_command_txt + str(self.transcoder_path)
        searching_command_txt = searching_command_txt + " "
        searching_command_txt = searching_command_txt + str(file_to_transcode)

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
            return "unknow"

    def tsp_job_information(self, jobid):
        cmd = list()
        output = list()
        tmp_output = list()
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
        tmp_output = list()
        cmd.append(unicode(self.taskspooler_path, 'utf-8'))
        cmd.append(unicode("-V", 'utf-8'))
        output.append(subprocess.check_output(cmd))
        if output:
            tmp_output = re.split(r' - ', output[0])
            return tmp_output[0]
        else:
            return "Task Spooler v(unknow)"

    def nice_get_version(self):
        cmd = list()
        output = list()
        tmp_output = list()
        cmd.append(unicode(self.nice_path, 'utf-8'))
        cmd.append(unicode("--version", 'utf-8'))
        output.append(subprocess.check_output(cmd))
        if output:
            tmp_output = re.split(r'\n', output[0])
            return tmp_output[0].title()
        else:
            return "Nice v(unknow)"

    def _getDirs(self, base):
        return [x for x in glob.iglob(os.path.join(base, '*')) if os.path.isdir(x)]

    def rglob(self, base, pattern):
        list = []
        list.extend(glob.glob(os.path.join(base, pattern)))
        dirs = self._getDirs(base)
        if len(dirs):
            for d in dirs:
                list.extend(self.rglob(os.path.join(base, d), pattern))
        return list

    def which(self, program):
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

    def check_transcoder(self):
        if not self.which("transcoder.py"):
            print "Error: Transcoder is require, for enable transcoding queue"
            print "Error: Please install \"transcoder.py\" or verify it is aviable on your $PATH env var"
            print "Error: " + scriptname_title + " will abort ..."
            sys.exit(1)
        else:
            return self.which("transcoder.py")
        return None

    def check_taskspooler(self):
        if not self.which("tsp"):
            print "Error: Task Spooler is require, for enable transcoding queue"
            print "Error: Please install \"task-spooler\" or verify it is aviable on your $PATH env var"
            print "Error: " + scriptname_title + " will abort ..."
            sys.exit(1)
        else:
            return self.which("tsp")
        return None

    def check_nice(self):
        if not self.which("nice"):
            print "Warning: Nice is require, for fixe low process priority"
            print "Warning: " + scriptname_title + " will continue without ..."
            return None
        else:
            return self.which("nice")
        return None

#tsp = TaskSpooler()

# Test Version
#print tsp.get_version()

# Test read the entire queue list
#print "ID   State      Output               E-Level  Times(r/u/s)   Command"
#for I, S in enumerate(tsp.get_list()):
#    for II, SS in enumerate(S):
#        print SS,
#    print

# Test for enumerate the status of the entire queue list

#for I, S in enumerate(tsp.get_list()):
#    print S[0] + " " + tsp.get_state(S[0])

# Test for have the status of the last job
#print tsp.get_state()

# Test for have the executed command of the last job
#print tsp.get_command()

# Test for have the executed command of the entire queue list
#for I, S in enumerate(tsp.get_list()):
#    print S[0] + " " + tsp.get_command(S[0])

# Test it clone the tsp output but use all TaskSpooler Class:
#print "ID   State      Output               E-Level  Times(r/u/s)   Command"
#for I, S in enumerate(tsp.get_list()):
#    print S[0] + " " + tsp.get_state(S[0]) + " " + tsp.get_output(S[0]) + " " + tsp.get_command(S[0])