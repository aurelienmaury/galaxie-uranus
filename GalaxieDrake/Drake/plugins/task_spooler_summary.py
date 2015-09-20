__author__ = 'tuxa'

import curses


class TaskSpoolerSummary(object):
    def __init__(self, parent, y, x, max_size, model):
        self.parent = parent
        self.y_parent_max, self.x_parent_max = self.parent.getbegyx()
        self.y = y
        self.x = x
        self.max_size = max_size
        self.model = model

        line_number = self.y
        #  = "TaskSpooler"
        taskspooler_title_text = self.model.taskspooler_title_text
        taskspooler_title_text += ": "
        #  = "Task"
        taskspooler_job_number_text = self.model.taskspooler_job_number_text
        # = "Running"
        taskspooler_running_text = self.model.taskspooler_running_text
        taskspooler_running_text = ", " + taskspooler_running_text
        # = "Queued"
        taskspooler_queued_text = self.model.taskspooler_queued_text
        taskspooler_queued_text = ", " + taskspooler_queued_text
        #  = "Finished"
        taskspooler_finished_text = self.model.taskspooler_finished_text
        taskspooler_finished_text = ", " + taskspooler_finished_text
        #  = "Error"
        taskspooler_finished_with_error_text = self.model.taskspooler_finished_with_error_text
        taskspooler_finished_with_error_text = ", " + taskspooler_finished_with_error_text

        if self.model.taskspooler_summary_list:
            taskspooler_job_number_value = str(self.model.taskspooler_summary_list[0])
            taskspooler_running_value = str(self.model.taskspooler_summary_list[1])
            taskspooler_queued_value = str(self.model.taskspooler_summary_list[2])
            taskspooler_finished_value = str(self.model.taskspooler_summary_list[3])
            taskspooler_finished_with_error_value = str(self.model.taskspooler_summary_list[4])
        else:
            taskspooler_job_number_value = " "
            taskspooler_running_value = " "
            taskspooler_queued_value = " "
            taskspooler_finished_value = " "
            taskspooler_finished_with_error_value = " "

        # Position Calculation
        x_pos = self.x
        taskspooler_pos_title_label = x_pos

        taskspooler_pos_job_number_label = x_pos
        taskspooler_pos_job_number_label += len(str(taskspooler_title_text))

        taskspooler_pos_job_number = taskspooler_pos_job_number_label
        taskspooler_pos_job_number += len(taskspooler_job_number_text)
        taskspooler_pos_job_number += 1

        taskspooler_pos_running_label = taskspooler_pos_job_number
        taskspooler_pos_running_label += len(str(taskspooler_job_number_value))

        taskspooler_pos_running = taskspooler_pos_running_label
        taskspooler_pos_running += len(str(taskspooler_running_text))
        taskspooler_pos_running += 1

        taskspooler_pos_queued_label = taskspooler_pos_running
        taskspooler_pos_queued_label += len(str(taskspooler_running_value))

        taskspooler_pos_queued = taskspooler_pos_queued_label
        taskspooler_pos_queued += len(str(taskspooler_queued_text))
        taskspooler_pos_queued += 1

        taskspooler_pos_finished_label = taskspooler_pos_queued
        taskspooler_pos_finished_label += len(str(taskspooler_queued_value))

        taskspooler_pos_finished = taskspooler_pos_finished_label
        taskspooler_pos_finished += len(str(taskspooler_finished_text))
        taskspooler_pos_finished += 1

        taskspooler_pos_finished_with_error_label = taskspooler_pos_finished
        taskspooler_pos_finished_with_error_label += len(str(taskspooler_finished_value))

        taskspooler_pos_finished_with_error = taskspooler_pos_finished_with_error_label
        taskspooler_pos_finished_with_error += len(str(taskspooler_finished_with_error_text))
        taskspooler_pos_finished_with_error += 1

        taskspooler_pos_end = taskspooler_pos_finished_with_error
        taskspooler_pos_end += len(str(taskspooler_finished_with_error_value))

        # Color calculation
        if taskspooler_running_value == (0 or "0"):
            taskspooler_running_color = curses.color_pair(3)
        else:
            taskspooler_running_color = curses.color_pair(7)

        if taskspooler_queued_value == (0 or "0"):
            taskspooler_queued_color = curses.color_pair(3)
        else:
            taskspooler_queued_color = curses.color_pair(7)

        if taskspooler_finished_with_error_value == (0 or "0"):
            taskspooler_finished_with_error_color = curses.color_pair(3)
        else:
            taskspooler_finished_with_error_color = curses.color_pair(9)

        # If we have the space to display
        if (taskspooler_pos_end - self.x) < self.max_size:
            # Display the Titles
            self.parent.addstr(
                line_number,
                taskspooler_pos_title_label,
                str(taskspooler_title_text),
                curses.color_pair(3) | curses.A_BOLD
            )
            # Display the Job Label Text
            self.parent.addstr(
                line_number,
                taskspooler_pos_job_number_label,
                str(taskspooler_job_number_text),
                curses.color_pair(3)
            )
            # Display the Job Value
            self.parent.addstr(
                line_number,
                taskspooler_pos_job_number,
                str(taskspooler_job_number_value),
                curses.color_pair(3) | curses.A_BOLD
            )
            # Display the Running Label Text
            self.parent.addstr(
                line_number,
                taskspooler_pos_running_label,
                str(taskspooler_running_text),
                curses.color_pair(3)
            )
            # Display the Running Value
            self.parent.addstr(
                line_number,
                taskspooler_pos_running,
                str(taskspooler_running_value),
                taskspooler_running_color | curses.A_BOLD
            )
            # Display the Queued Label Text
            self.parent.addstr(
                line_number,
                taskspooler_pos_queued_label,
                str(taskspooler_queued_text),
                curses.color_pair(3)
            )
            # Display the Queued Value
            self.parent.addstr(
                line_number,
                taskspooler_pos_queued,
                str(taskspooler_queued_value),
                taskspooler_queued_color | curses.A_BOLD
            )
            # Display the Finished Label Text
            self.parent.addstr(
                line_number,
                taskspooler_pos_finished_label,
                str(taskspooler_finished_text),
                curses.color_pair(3)
            )
            # Display the Finished Label Value
            self.parent.addstr(
                line_number,
                taskspooler_pos_finished,
                str(taskspooler_finished_value),
                curses.color_pair(3) | curses.A_BOLD
            )
            # Display the Finished With Error Text
            self.parent.addstr(
                line_number,
                taskspooler_pos_finished_with_error_label,
                str(taskspooler_finished_with_error_text),
                curses.color_pair(3)
            )
            # Display the Finished With Error Value
            self.parent.addstr(
                line_number,
                taskspooler_pos_finished_with_error,
                str(taskspooler_finished_with_error_value),
                taskspooler_finished_with_error_color | curses.A_BOLD
            )
