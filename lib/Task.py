

from progressbar import ProgressBar
from multiprocessing import  Process

class Task(Process):
    def __init__(self, TaskNo, TaskName, CurObject):
        super(Task, self).__init__()
        self.CurObject = CurObject
        self.TaskNo    = TaskNo
        self.TaskName  = TaskName

    def run(self):
        print ("[Task%d]Start run task: %s.." %(self.TaskNo, self.TaskName))
        self.CurObject.StartRun ()
        print ("[Task%d]Finish task: %s.." %(self.TaskNo, self.TaskName))



    