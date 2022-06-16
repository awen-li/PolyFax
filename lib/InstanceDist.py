
import os
from lib.Config import Config
from lib.TaskDistributer import TaskDistributer
from lib.CmmtCrawler import CmmtCrawler
from lib.CmmtLogAnalyzer import CmmtLogAnalyzer
from lib.LangApiAnalyzer import LangApiAnalyzer


class CmmtCrawlerDist (TaskDistributer):
    def __init__(self, TaskNum=4, RepoList=[]):
        self.TaskNum   = TaskNum
        self.RepoList  = RepoList
        super(CmmtCrawlerDist, self).__init__(TaskName='CmmtCrawler', ItemSize=len(RepoList), TaskNum=TaskNum)

    def InitObject(self, StartNo, EndNo):
        CCrawler = CmmtCrawler (startNo=StartNo, endNo=EndNo, RepoList=self.RepoList)
        return CCrawler

    def Final(self):
        return None


class CmmtLogAnalyzerDist (TaskDistributer):
    def __init__(self, TaskNum=4, RepoList=[]):
        self.TaskNum   = TaskNum
        if len (RepoList) == 0:
            CCAnalyzer = CmmtLogAnalyzer ()
            RepoList = CCAnalyzer.RepoList
        
        super(CmmtLogAnalyzerDist, self).__init__(TaskName='CmmtLogAnalyzer', ItemSize=len(RepoList), TaskNum=TaskNum)
        
    def InitObject(self, StartNo, EndNo):
        CCAnalyzer = CmmtLogAnalyzer (StartNo=StartNo, EndNo=EndNo)
        return CCAnalyzer

    def Final(self):
        return None
        
class LangApiAnalyzerDist (TaskDistributer):
    def __init__(self, TaskNum=4, RepoList=[]):
        self.TaskNum   = TaskNum
        if len (RepoList) == 0:
            LAAnalyzer = LangApiAnalyzer ()
            RepoList = LAAnalyzer.RepoList
                
        super(LangApiAnalyzerDist, self).__init__(TaskName='LangApiAnalyzer', ItemSize=len(RepoList), TaskNum=TaskNum)
                
    def InitObject(self, StartNo, EndNo):
        CCAnalyzer = LangApiAnalyzer (StartNo=StartNo, EndNo=EndNo, FileName='ApiSniffer'+str(StartNo))
        return CCAnalyzer
    
    def Final(self):
        Cmd = 'find Data/ -name ApiSniffer*'
        ALLFiles = os.popen(Cmd).read()
        ALLFiles = list (ALLFiles.split ('\n'))
        if ALLFiles[0] == '':
            print ("[Warning] No ApiSniffer.csv generagted.....")
            return

        print ("[Final]Start to merge sniffer files [%d].... " %len(ALLFiles))
        FinalFile = Config.BaseDir + '/' + Config.StatisticDir + '/ApiSniffer.csv'
        for file in ALLFiles:
            if len (file) == 0 or file.find ('ApiSniffer.csv') != -1:
                continue
            Cmd = 'cat ' +  file + ' >> ' + FinalFile + '; rm -f ' + file
            print ("\t ->" + Cmd)
            os.system (Cmd)

   