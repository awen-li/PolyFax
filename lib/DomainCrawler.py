
import os
from itertools import combinations
from lib.Crawler import Crawler

    
class DomainCrawler(Crawler):
    def __init__(self, FileName="RepositoryList-Domain.csv", UserName="", Token="", LangList=[], Domains=[]):
        super(LangCrawler, self).__init__(FileName, UserName, Token)
        self.LangList = LangList
        self.Domains  = Domains

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
                    
                    LangsDict = self.LangValidate (LangsDict)
                    if LangsDict == None:
                        continue
                    
                    Langs = list(LangsDict.keys ())
                    if len (Langs) == 0:
                        continue

                    print ("\t[%u][%u] --> %s" %(len(self.RepoList), Repo['id'], Repo['clone_url']))
                    RepoData = Repository (Repo['id'], Repo['stargazers_count'], Langs, Repo['url'], Repo['clone_url'], Repo['topics'], 
                                           Repo['description'], Repo['created_at'], Repo['pushed_at'])
                    RepoData.SetMainLang(MainLang)
                    
                    self.RepoList[Repo['id']] = RepoData
                    self.AppendSave (RepoData)
        self.Save()

    