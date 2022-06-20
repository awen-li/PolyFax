
import abc
import copy
from lib.Task import Task

class TaskDistributer():
    def __init__(self, TaskName,     ItemSize, TaskNum=4):
        self.TaskNum   = TaskNum
        self.TaskName  = TaskName
        self.ItemSize  = ItemSize

        print ("TaskDistributer[%s]ItemSize:%d" %(TaskName, ItemSize))
        if self.TaskNum == 0:
            self.TaskNum = 4

    @abc.abstractmethod
    def InitObject(self, StartNo, EndNo):
        return None

    @abc.abstractmethod
    def Final(self):
        return None

    def Distributer(self):       
        TaskNo  = 0
        Tasks   = []
        StartNo = 0
        Delta   = int (self.ItemSize/self.TaskNum)
        Mod     = self.ItemSize%self.TaskNum
        if Delta == 0:
            self.TaskNum = 1
            Delta = self.ItemSize
        
        while TaskNo < self.TaskNum:
            
            EndNo = StartNo+Delta-1
            if TaskNo == self.TaskNum-1:
                EndNo += Mod

            print ("[Task%d][Distributer] -> [%u, %u]" %(TaskNo, StartNo, EndNo))
            CurObject = self.InitObject (StartNo, EndNo)
            SubTask = Task (TaskNo, self.TaskName, CurObject)
            TaskNo += 1
            
            SubTask.start()
            Tasks.append(SubTask)

            StartNo += Delta
        
        for t in Tasks:
            t.join()

        self.Final ()
        print ("====> Exiting.")
            

    



    