
import os
from lib.Crawler import Crawler
from lib.Repository import Repository
    
class DomainCrawler(Crawler):
    def __init__(self, FileName="RepositoryList.csv"):
        super(DomainCrawler, self).__init__(FileName)

        if os.path.exists (self.FileName):
            os.rename (self.FileName, self.FileName+"-back.csv")

    def GrabProject (self):
        PageNum = 10  
        for Domain in self.Domains:
            if self.MaxGrabNum != -1 and len(self.RepoList) >= self.MaxGrabNum:
                break;
                        
            for PageNo in range (1, PageNum+1):
                if self.MaxGrabNum != -1 and len(self.RepoList) >= self.MaxGrabNum:
                    break;
                
                print ("===>[Domain]: ", Domain, ", [Page] ", PageNo, end=", ")
                Result = self.GetRepoByDomain (Domain, PageNo)
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

                    Stars = Repo['stargazers_count']
                    if Stars < self.MinStar:
                        continue

                    print ("\t[%u][%u] --> %s" %(len(self.RepoList), Repo['id'], Repo['clone_url']))
                    RepoData = Repository (Repo['id'], Repo['stargazers_count'], Langs, Repo['url'], Repo['clone_url'], Repo['topics'], 
                                           Repo['description'], Repo['created_at'], Repo['pushed_at'])
                    RepoData.SetMainLang(MainLang)
                    RepoData.SetName(Repo['name'])

                    Exist = self.RepoList.get (Repo['id'])
                    if Exist != None:
                        continue
                    
                    self.RepoList[Repo['id']] = RepoData
                    self.AppendSave (RepoData)

                    if self.MaxGrabNum != -1 and len(self.RepoList) >= self.MaxGrabNum:
                        break;
        #self.Save()

    