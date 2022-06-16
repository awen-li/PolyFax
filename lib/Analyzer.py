

import abc
import csv 
import sys
import pandas as pd
from progressbar import ProgressBar
from lib.Config import Config
from lib.Util import Util
from lib.Repository import Repository


csv.field_size_limit(sys.maxsize)


class Analyzer(metaclass=abc.ABCMeta):

    Language_Combination_Limit = 20

    def __init__(self, StartNo=0, EndNo=65535, FileName="Analyzer.csv"):
        self.FileName = FileName
        self.StartNo  = StartNo
        self.EndNo    = EndNo
        self.FilePath = Config.BaseDir
        self.AnalyzStats = {}

        self.RepoList = []
        self.LoadRepoList ()
        
    @abc.abstractmethod
    def SaveData (self, data, FileName=None):
        if (FileName == None):
            FileName = self.FileName
        self.__WriteCsv (data, FileName)

    def SaveData2 (self, FileName, Header, Dict):
        FilePath = self.FilePath + FileName + '.csv'      
        with open(FilePath, 'w') as CsvFile:
            W = csv.writer(CsvFile)            
            W.writerow(Header)
            for Key, Value in Dict.items():
                Row = self.Obj2List (Value)
                W.writerow(Row)

    def __WriteCsv (self, Data, FileName):
        CurFile = self.FilePath + FileName
        if CurFile.find ('.csv') == -1:
            CurFile += '.csv'       
        with open(CurFile, 'w') as CsvFile:
            W = csv.writer(CsvFile)
            W.writerow(self.__GetHeader (Data))
            for Key, Value in Data.items():
                Row = self.Obj2List (Value)
                writer.writerow(Row)

    def LoadRepoList (self, FileName="RepositoryList.csv"):
        FilePath = self.FilePath + '/' + FileName
        df = pd.read_csv(FilePath)
        for index, row in df.iterrows():
            RepoData = Repository (row['Id'], row['Star'], row['Langs'], row['ApiUrl'], row['CloneUrl'], row['Topics'], 
                                   row['Descripe'], row['Created'], row['Pushed'])
            self.RepoList.append (RepoData)

    @abc.abstractmethod
    def Obj2List (self, Value):
        return list(Value.__dict__.values())

    @abc.abstractmethod
    def Obj2Dict (self, Value):
        return Value.__dict__

    @abc.abstractmethod
    def GetHeader (self, Data):
        Headers = list(list(Data.values())[0].__dict__.keys())
        return [header.replace(" ", "_") for header in Headers]

    def AnalyzeData (self, RepoList):
        pbar = ProgressBar()
        for Repo in pbar(RepoList):
            self.UpdateAnalysis (Repo)
        self.UpdateFinal ()

    @abc.abstractmethod
    def UpdateFinal (self):
        print("Abstract Method that is implemented by inheriting classes")

    @abc.abstractmethod
    def UpdateAnalysis(self, CurRepo):
        print("Abstract Method that is implemented by inheriting classes")

    def StartRun (self):
        self.AnalyzeData (self.RepoList)
        

   