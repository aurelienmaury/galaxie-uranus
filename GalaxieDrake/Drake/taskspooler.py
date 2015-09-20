#!/usr/bin/python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: Jerome ORNECH alias "Tuux" <tuxa@rtnp.org> all rights reserverd

import os
import sys
import subprocess
import locale
import re


class TaskSpooler(object):
    def __init__(self):
        self.command = self.check_taskspooler()
        self.remove_args = '-r'
        self.state_args = '-s'
        self.info_args = '-i'
        self.output_args = '-o'
        self.version_args = '-V'
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

    def remove_task(self, jobid=None):
        command = [self.command, self.remove_args]
        if jobid is not None:
            command.append(jobid)
        subprocess.call(command)

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
        output = [subprocess.check_output(command)]
        if output:
            return output[0].rstrip(os.linesep)
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

tsp = TaskSpooler()

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