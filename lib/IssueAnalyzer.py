
from lib.Util import Util
from lib.Analyzer import Analyzer
from lib.Config import Config
from lib.Scrubber import Scrubber

from progressbar import ProgressBar
import pandas as pd
import time
from time import sleep
import re
import os
import ast
import sys
import requests

class IssueItem():
    def __init__ (self, url, state, title, label, comments_url, diff_url, patch_url):
        self.url   = url
        self.state = state
        self.title = title
        self.label = label
        self.comments_url = comments_url
        self.diff_url = diff_url
        self.patch_url = patch_url
        
class IssueAnalyzer (Analyzer):
    def __init__(self, StartNo=0, EndNo=65535, FileName='IssueAnalyzer.csv', UserName='', Token=''):
        super(IssueAnalyzer, self).__init__(StartNo=StartNo, EndNo=EndNo, FileName=FileName)
        self.RepoNum   = 0
        self.UserName  = UserName
        self.Token     = Token

    def IsSegfin (self, RepoNum):
        if RepoNum < self.StartNo  or RepoNum >= self.EndNo:
            return True
        return False

    def IsContinue (self, errcode):
        codes = [410, 404, 500]
        if (errcode in codes):
            return False
        else:
            return True

    def GetIssue (self, url, issue):
        url = url + "/issues/" + issue
        result = requests.get(url,
                              auth=(self.UserName, self.Token),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (self.IsContinue (result.status_code) == False):
            #print("$$$%s: %s, URL: %s" % (result.status_code, result.reason, url))
            return None
        
        if (result.status_code != 200 and result.status_code != 422):
            print("%s: %s, URL: %s" % (result.status_code, result.reason, url))
            sleep(1200)
            return self.GetIssue(url, issue)     
        return result.json()
                
    def UpdateAnalysis(self, Repo):

        self.RepoNum += 1
        if (self.IsSegfin (self.RepoNum)):
            return
        
        RepoId   = Repo.Id
        CmmtFile = Config.CmmtFile (RepoId)
        if (Config.IsExist(CmmtFile) == False):
            return

        cdf = pd.read_csv(CmmtFile)
        IssueFile = Config.IssueFile (RepoId)
        if os.path.exists(IssueFile):
            return
                
        print ("[%u]%u start...commit num:%u" %(self.RepoNum, RepoId, cdf.shape[0]))
        ExIssues = {}
        for index, row in cdf.iterrows():
            IsNo = row['issue']
            if IsNo == ' ':
                continue

            if ExIssues.get (IsNo) != None:
                continue

            IssJson = self.GetIssue (Repo.ApiUrl, IsNo)
            if IssJson == None:
                continue

            # get label
            Label   = ' '
            Labels = IssJson['labels']
            if len (Labels) != 0:
                Label = Labels[0]['name']

            # get pullrequest
            diff_url  = ' ' 
            patch_url = ' '
            if 'pull_request' in IssJson:
                pull_request = IssJson['pull_request']
                diff_url  = pull_request['diff_url']
                patch_url = pull_request['patch_url']
            
            No = len (self.AnalyzStats)
            self.AnalyzStats[No] = IssueItem (IssJson['url'], IssJson['state'], IssJson['title'], Label, 
                                              IssJson['comments_url'], diff_url, patch_url)
            ExIssues [IsNo] = True
            print ("<%d>[%d/%d] %d -> retrieve %s" %(self.RepoNum, index, cdf.shape[0], No, IssJson['url']))

        self.SaveData (str(RepoId))
        self.AnalyzStats = {}

    def UpdateFinal (self):
        pass

    def SaveData (self, FileName=None):
        if (len(self.AnalyzStats) == 0):
            if FileName != None:
                Empty = "touch " + FileName
                os.system (Empty)
            return
        super(IssueAnalyzer, self).SaveData2 ("/StatData/CmmtSet/" + FileName, self.AnalyzStats[0].__dict__, self.AnalyzStats)
                     
    def Obj2List(self, value):
        return super(IssueAnalyzer, self).Obj2List (value)
            
    def Obj2Dict(self, value):
        return super(IssueAnalyzer, self).Obj2Dict (value)
            
    def GetHeader(self, data):
        return super(IssueAnalyzer, self).GetHeader (data)
    
