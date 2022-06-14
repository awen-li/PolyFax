
import os
from itertools import combinations
from lib.Crawler import Crawler

    
class DomainCrawler(Crawler):
    def __init__(self, FileName="RepositoryList-Domain.csv", UserName="", Token="", LangList=[]):
        super(LangCrawler, self).__init__(FileName, UserName, Token)
        self.LangList = LangList
        self.Domains  = []

    def LangValidate (self, LangsDict):
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

        if len (ValidLangs) < 2:
            return None

        return ValidLangs

    def GrabProject (self):
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
                Result = self.GetRepoByStar (StarRange, PageNo)
                if 'items' not in Result:
                    break
                
                RepoList = Result['items']
                for Repo in RepoList:
                    LangsDict = self.GetRepoLangs (Repo['languages_url'])
                    LangsDict = self.LangValidate (LangsDict)
                    if LangsDict == None:
                        continue
                    
                    print ("\t[%u][%u] --> %s" %(len(self.RepoList), Repo['id'], Repo['clone_url']))
                    Langs = list(LangsDict.keys ())
                    RepoData = Repository (Repo['id'], Repo['stargazers_count'], Langs, Repo['url'], Repo['clone_url'], Repo['description'])
                    self.RepoList[Repo['id']] = RepoData
                    self.Appendix (RepoData)
        self.Save()

    