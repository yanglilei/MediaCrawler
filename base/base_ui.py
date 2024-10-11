import re
from typing import List

import psutil


def is_cell_input_legal(input_text: str):
    ret = False
    if input_text is not None and isinstance(input_text, str) and len(input_text) > 0:
        pattern = "^[a-zA-Z]+[1-9][0-9]*$"
        if re.match(pattern, input_text):
            ret = True
    return ret


class BusiException(Exception):
    pass


class Singleton:
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self, *args, **kwargs):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls(*args)
        return self._instance[self._cls]


# output_local_flag = False
#
# if ConfigFileReader.get_val(Constants.ConfigFileKey.LOG_LOCAL_FLAG,
#                             section_name=ConfigFileReader.base_section_name) != "0":
#     output_local_flag = True


def sys_runtime():
    pids = psutil.pids()
    for pid in pids:
        process = psutil.Process(pid)
        print("进程名称：%s，进程ID：%d，父进程ID：%d" % (process.name(), process.pid, process.ppid()))


def get_child_processes(parent_pid, child_processes: List[psutil.Process]):
    for process in psutil.process_iter():
        if process.ppid() == parent_pid:
            # print("进程名称：%s，进程ID：%d，父进程ID：%d" % (process.name(), process.pid, process.ppid()))
            child_processes.append(process)
            get_child_processes(process.pid, child_processes)


def get_processes_by_name(process_name):
    ret = list()
    process_iter = psutil.process_iter()
    for process in process_iter:
        if process.name() == process_name:
            ret.append(process)
    return
