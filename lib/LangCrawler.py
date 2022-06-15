
import os
from lib.Crawler import Crawler
from lib.Repository import Repository
    
class LangCrawler(Crawler):
    def __init__(self, FileName="RepositoryList.csv", UserName="", Token="", LangList=[], MaxGrabNum=-1):
        super(LangCrawler, self).__init__(FileName, UserName, Token, LangList, MaxGrabNum)
        self.LangList = LangList
        
        self.MinLang  = 2
        self.MaxLang  = 6
        self.LangSelectList = []
        
    def GetLangSelections ():
        for i in range(self.MinLang, self.MaxLang+1, 1):
            LangSelect = [list(x) for x in combinations(self.LangList, i)]
            if len(LangSelect) > 0:
                self.LangSelectList.extend(LangSelect)

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
                RepoSize = len (RepoList)       
                if RepoSize == 0:
                    print ("")
                    break

                print ("RepoSize: %u" %RepoSize)
                
                for Repo in RepoList:
                    LangsDict = self.GetRepoLangs (Repo['languages_url'])
                    LangsDict = self.LangValidate (LangsDict)
                    if LangsDict == None:
                        continue
                    
                    print ("\t[%u][%u] --> %s" %(len(self.RepoList), Repo['id'], Repo['clone_url']))
                    Langs = list(LangsDict.keys ())

                    RepoData = Repository (Repo['id'], Repo['stargazers_count'], Langs, Repo['url'], Repo['clone_url'], Repo['topics'], 
                                           Repo['description'], Repo['created_at'], Repo['pushed_at'])
                    self.RepoList[Repo['id']] = RepoData
                    self.AppendSave (RepoData)
                    
                    if self.MaxGrabNum != -1 and len(self.RepoList) >= self.MaxGrabNum:
                        Star = self.MinStar-1
                        break;
        self.Save()

    