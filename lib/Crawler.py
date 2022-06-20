import csv
import os
import re
import requests
import sys, getopt
import pandas as pd
from time import sleep
from lib.Repository import Repository
from lib.Config import Config
    
class Crawler():
    def __init__(self, FileName="RepositoryList.csv", UserName="", Token="", LangList=[], MaxGrabNum=-1):
        self.FileName = Config.BaseDir + '/' + FileName
        self.Username = UserName
        self.Password = Token
        self.LangList = LangList
        
        self.RepoList = {}

        self.MaxStar = 15000
        self.MinStar = 1000
        self.Delta   = 100

        self.MaxGrabNum = MaxGrabNum

    
    def IsContinue (self, errcode):
        codes = [404, 500]
        if (errcode in codes):
            return False
        else:
            return True

    def HttpCall(self, Url):
        Result = requests.get(Url,
                              auth=(self.Username, self.Password),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (self.IsContinue (Result.status_code) == False):
            print("$$$%s: %s, URL: %s" % (Result.status_code, Result.reason, Url))
            return None
        
        if (Result.status_code != 200 and Result.status_code != 422):
            print("Status Code %s: %s, URL: %s" % (Result.status_code, Result.reason, Url))
            sleep(300)
            return self.HttpCall(Url)
        return Result.json()

    def GetRepoByStar(self, Star, PageNo):
        Url  = 'https://api.github.com/search/repositories?' + 'q=stars:' + Star + '+is:public+mirror:false'        
        Url += '&sort=stars&per_page=100' + '&order=desc' + '&page=' + str(PageNo)
        return self.HttpCall(Url)

    def GetRepoByDomain(self, Domain, PageNo):
        Url  = 'https://api.github.com/search/repositories?' + 'q=' + Domain + '+is:public+mirror:false'        
        Url += '&sort=stars&per_page=100' + '&order=desc' + '&page=' + str(PageNo)
        return self.HttpCall(Url)

    def GetRepoLangs (self, LangUrl):
        Langs = self.HttpCall(LangUrl)
        Langs = dict(sorted(Langs.items(), key=lambda item:item[1], reverse=True))
        lowerLangs = {}
        for lang, size in Langs.items():
            lowerLangs [lang.lower()] = size
        #Langs = [lang.lower() for lang in Langs.keys()]
        return lowerLangs

    def Save (self, Header=None):
        if len (self.RepoList) == 0:
            return
        
        WriteHeader = False
        with open(self.FileName, 'w', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            
            for Id, Repo in self.RepoList.items():
                if WriteHeader == False:
                    Header = Repo.__dict__.keys()
                    writer.writerow(Header)
                    WriteHeader = True
                
                row = [Repo.Id, Repo.Star, Repo.MainLang, Repo.Langs, Repo.ApiUrl, Repo.CloneUrl, Repo.Topics, Repo.Descripe, Repo.Created, Repo.Pushed]
                writer.writerow(row)
        return

    def AppendSave (self, Repo):
        WriteHeader = False
        if os.path.exists (self.FileName):
            WriteHeader = True

        with open(self.FileName, 'a+', encoding='utf-8') as CsvFile:
            writer = csv.writer(CsvFile)      
            if WriteHeader == False:
                Header = Repo.__dict__.keys ()
                writer.writerow(Header)
            Row = [Repo.Id, Repo.Star, Repo.MainLang, Repo.Langs, Repo.ApiUrl, Repo.CloneUrl, Repo.Topics, Repo.Descripe, Repo.Created, Repo.Pushed]
            writer.writerow(Row)
        return

    def GetMainLang (self, LangsDict):
        MaxSize  = 0
        MainLang = ''
        for lang, size in LangsDict.items ():
            if size > MaxSize:
                MaxSize  = size
                MainLang = lang
        return MainLang
            
    def LangValidate (self, LangsDict):
        if len (self.LangList) == 0:
            return LangsDict

        Langs = list(LangsDict.keys ())[0:6]

        # compute all language size
        Size = 0
        for lg in Langs:
            Size += LangsDict[lg]

        # compute proportion for each langage
        ValidLangs = {}
        for lang in LangsDict:
            if lang not in self.LangList:
                continue
            ptop = LangsDict[lang]*100.0/Size
            if ptop < 5:
                continue
            ValidLangs [lang] = ptop

        #multi-languages
        if len (ValidLangs) < 2:
            return None

        return ValidLangs

    def GrabProject (self):
        PageNum = 10  
        Star    = self.MaxStar
        Delta   = self.Delta
        while Star > self.MinStar:
            Bstar = Star - Delta
            Estar = Star
            Star  = Star - Delta

            StarRange = str(Bstar) + ".." + str(Estar)
            for PageNo in range (1, PageNum+1):
                print ("===>[Star]: ", StarRange, ", [Page] ", PageNo, end=", ")
                Result = self.GetRepoByStar (StarRange, PageNo)
                if 'items' not in Result:
                    break
                
                RepoList = Result['items']
                RepoNum  = len (RepoList)       
                if RepoNum == 0:
                    print ("")
                    break

                print ("RepoNum: %u" %RepoNum)
                for Repo in RepoList:
                    LangsDict = self.GetRepoLangs (Repo['languages_url'])
                    MainLang  = self.GetMainLang (LangsDict)
                    
                    Langs = list(LangsDict.keys ())[0:6]
                    if len (Langs) == 0:
                        continue

                    print ("\t[%u][%u] --> %s" %(len(self.RepoList), Repo['id'], Repo['clone_url']))
                    RepoData = Repository (Repo['id'], Repo['stargazers_count'], Langs, Repo['url'], Repo['clone_url'], Repo['topics'], 
                                           Repo['description'], Repo['created_at'], Repo['pushed_at'])
                    RepoData.SetMainLang(MainLang)
                    
                    self.RepoList[Repo['id']] = RepoData
                    self.AppendSave (RepoData)
        #self.Save()

    def Grab (self):
        # grab repository list
        self.GrabProject ()



