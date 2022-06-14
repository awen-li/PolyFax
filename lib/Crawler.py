import csv
import os
import re
import requests
import sys, getopt
import pandas as pd
from time import sleep
from lib.Repository import Repository
    
class Crawler():
    def __init__(self, FileName="RepositoryList.csv", UserName="", Token=""):
        self.FileName = FileName
        self.Username = UserName
        self.Password = Token
        self.RepoList = {}

    def HttpCall(self, Url):
        Result = requests.get(Url,
                              auth=(self.Username, self.Password),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (Result.status_code != 200 and Result.status_code != 422):
            print("Status Code %s: %s, URL: %s" % (Result.status_code, Result.reason, Url))
            sleep(300)
            return self.HttpCall(Url)
        return Result.json()

    def GetPageofRepos(self, Star, PageNo):
        Url  = 'https://api.github.com/search/repositories?' + 'q=stars:' + Star + '+is:public+mirror:false'        
        Url += '&sort=stars&per_page=100' + '&order=desc' + '&page=' + str(PageNo)
        return self.HttpCall(Url)

    def Save (self):
        Header = ['id', 'Star', 'Languages', 'ApiUrl', 'CloneUrl', 'Description']
        with open(self.FileName, 'w', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            writer.writerow(Header)  
            for Id, Repo in self.RepoList.items():
                row = [Repo.Id, Repo.Star, Repo.Langs, Repo.ApiUrl, Repo.CloneUrl, Repo.Descripe]
                writer.writerow(row)
        return

    def AppendSave (self, Repo):
        IsNew = False
        if not os.path.exists (self.FileName):
            IsNew = True
        
        with open(self.FileName, 'a+', encoding='utf-8') as CsvFile:
            writer = csv.writer(CsvFile)      
            if IsNew == True:
                Header = ['id', 'Star', 'Languages', 'ApiUrl', 'CloneUrl', 'Description']
                writer.writerow(Header)
            Row = [Repo.Id, Repo.Star, Repo.Langs, Repo.ApiUrl, Repo.CloneUrl, Repo.Descripe]
            writer.writerow(Row)
        return

    def CrawlerProject (self):
        PageNum = 10  
        Star    = 15000
        Delta   = 100
        while Star > 100:
            Bstar = Star - Delta
            Estar = Star
            Star  = Star - Delta

            StarRange = str(Bstar) + ".." + str(Estar)
            for PageNo in range (1, PageNum+1):
                print ("===>[Star]: ", StarRange, ", [Page] ", PageNo)
                Result = self.GetPageofRepos (StarRange, PageNo)
                if 'items' not in Result:
                    break
                RepoList = Result['items']
                for Repo in RepoList:
                    LangsDict = self.GetRepoLangs (Repo['languages_url'])                    
                    print ("\t[%u][%u] --> %s" %(len(self.RepoList), Repo['id'], Repo['clone_url']))
                    Langs = list(LangsDict.keys ())[0:3]
                    RepoData = Repository (Repo['id'], Repo['stargazers_count'], Langs, Repo['url'], Repo['clone_url'], Repo['description'])
                    self.RepoList[Repo['id']] = RepoData
                    self.Appendix (RepoData)
        self.Save()

    def Clone (self):
        BaseDir = os.getcwd () + "/Repository/"
        if not os.path.exists (BaseDir):
            os.mkdir (BaseDir)
        
        Df = pd.read_csv(self.FileName)
        for Index, Row in Df.iterrows():            
            RepoId = Row['id']        
            RepoDir = BaseDir + str(RepoId)
            if not os.path.exists (RepoDir):
                os.mkdir (RepoDir)
            else:
                RmCmd = "rm -rf " + RepoDir + "/*"
                os.system (RmCmd)         
            os.chdir(RepoDir)

            CloneUrl = Row['CloneUrl']
            CloneCmd = "git clone " + CloneUrl
            print ("[", Index, "] --> ", CloneCmd)
            os.system (CloneCmd)

            CleanCmd = "find . -name \".git\" | xargs rm -rf"
            os.system (CleanCmd)

    def Sniffer (self, Dir):
        CRegex  = "#include <Python.h>|PyObject|Py_Initialize|PyMethodDef|cdll.LoadLibrary"
        PyRegex = "from cffi import FFI|from ctypes import|from.*cimport|cdef extern from"
        RuleSet = {".c":CRegex, ".py":PyRegex}
        
        RepoDirs = os.walk(Dir)
        for Path, Dirs, Fs in RepoDirs:
            for f in Fs:
                File = os.path.join(Path, f)
                if not os.path.exists (File):
                    continue
            
                Ext = os.path.splitext(File)[-1].lower()
                Rules = RuleSet.get (Ext)
                if Rules == None:
                    continue
                with open (File, "r", encoding="utf8", errors="ignore") as sf:
                    for line in sf:
                        if len (line) < 4:
                            continue

                        if re.search(Rules, line) != None:
                            print (Dir, " -> Python interacts with C.")
                            return True
        return False

