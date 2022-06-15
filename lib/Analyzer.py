

import abc
import csv 
import sys 
from progressbar import ProgressBar
from lib.Config import Config
from lib.Util import Util


csv.field_size_limit(sys.maxsize)


class Analyzer(metaclass=abc.ABCMeta):

    Language_Combination_Limit = 20

    def __init__(self, FileName):
        self.FileName = FileName
        self.FilePath = Config.getdir_stat()
        self.AnalyzStats = {}
        
    @abc.abstractmethod
    def SaveData (self, data, FileName=None):
        if (FileName == None):
            FileName = self.file_name
        self.__WriteCsv (data, file_name)

    def SaveData2 (self, FileName, Header, Dict):
        FilePath = self.FilePath + FileName + '.csv'      
        with open(FilePath, 'w') as CsvFile:
            W = csv.writer(CsvFile)            
            W.writerow(Header)
            for item in Dict.items():
                W.writerow(item)

    def __WriteCsv (self, Data, FileName):
        CurFile = self.FilePath + FileName
        if CurFile.find ('.csv') == -1:
            CurFile += '.csv'       
        with open(CurFile, 'w') as CsvFile:
            W = csv.writer(CsvFile)
            W.writerow(self.__GetHeader (Data))
            for Key, Value in Data.items():
                Row = self.__Obj2List (Value)
                writer.writerow(Row)

    def LoadRepoList (FileName="RepoList.csv"):
        pass

    @abc.abstractmethod
    def __Obj2List (self, Value):
        return list(Value.__dict__.values())

    @abc.abstractmethod
    def __Obj2Dict (self, Value):
        return Value.__dict__

    @abc.abstractmethod
    def __GetHeader (self, Data):
        Headers = list(list(Data.values())[0].__dict__.keys())
        return [header.replace(" ", "_") for header in Headers]

    def AnalyzeData (self, RepoList):
        pbar = ProgressBar()
        for Repo in pbar(RepoList):
            self.__UpdateAnalysis (Repo)
        self.__UpdateFinal ()

    @abc.abstractmethod
    def __UpdateFinal (self):
        print("Abstract Method that is implemented by inheriting classes")

    @abc.abstractmethod
    def __UpdateAnalysis(self, CurRepo):
        print("Abstract Method that is implemented by inheriting classes")

   