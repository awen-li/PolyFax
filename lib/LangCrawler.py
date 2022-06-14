
import os
from itertools import combinations
from lib.Crawler import Crawler

    
class LangCrawler(Crawler):
    def __init__(self, FileName="RepositoryList.csv", UserName="", Token="", LangList=[]):
        super(LangCrawler, self).__init__(FileName, UserName, Token)
        self.LangList = LangList
        
        self.MinLang  = 2
        self.MaxLang  = 6
        self.LangSelectList = []
        
    def GetLangSelections ():
        for i in range(self.MinLang, self.MaxLang+1, 1):
            LangSelect = [list(x) for x in combinations(self.LangList, i)]
            if len(LangSelect) > 0:
                self.LangSelectList.extend(LangSelect)

    def GetRepoLangs (self, LangUrl):
        Langs = self.HttpCall(LangUrl)
        Langs = dict(sorted(Langs.items(), key=lambda item:item[1], reverse=True))
        #Langs = [lang.lower() for lang in Langs.keys()]
        return Langs

    def IsCPython (self, LangsDict):
        Langs = list(LangsDict.keys ())[0:3]
        if 'C' not in Langs or 'Python' not in Langs:
            return False

        Size = 0
        for lg in Langs:
            Size += LangsDict[lg]
		
        Cp  = LangsDict['C']*100/Size
        if 'C++' in Langs:
            Cp  += LangsDict['C++']*100/Size
        
        Pyp =  LangsDict['Python']*100/Size
        print (LangsDict, end=", => ")
        print ("C percent = %u, Python percent = %u" %(Cp, Pyp))

        if Cp < 10:
            return False

        if Pyp < 30:
            return False

        return True

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
                Result = self.GetPageofRepos (StarRange, PageNo)
                if 'items' not in Result:
                    break
                RepoList = Result['items']
                for Repo in RepoList:
                    LangsDict = self.GetRepoLangs (Repo['languages_url'])
                    if self.IsCPython (LangsDict) == False and self.IsCJava (LangsDict) == False:
                        continue
                    
                    print ("\t[%u][%u] --> %s" %(len(self.RepoList), Repo['id'], Repo['clone_url']))
                    Langs = list(LangsDict.keys ())[0:3]
                    RepoData = Repository (Repo['id'], Repo['stargazers_count'], Langs, Repo['url'], Repo['clone_url'], Repo['description'])
                    self.RepoList[Repo['id']] = RepoData
                    self.Appendix (RepoData)
        self.Save()

    