
import csv
import sys
import os
import re
import pandas as pd
from lib.Config import Config
from lib.Util import Util
from lib.Crawler import Crawler
from lib.Scrubber import Scrubber

CFG = Config ()
CFG.LoadCfg ()


def IsNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

class Diff ():
    def __init__(self, file, content):
        self.file = file
        self.content = content

    def AddFile (self, file):
        self.file += " " + file

    def AddContent (self, content):
        self.content += " " + content

class Commit ():
    def __init__(self, id, sha, author, date, message):
        self.id      = id
        self.sha     = sha
        self.author  = author
        self.date    = date
        self.message = message
        self.issue   = ' '

        self.Diffs   = None

    def AddDiff (self, DF):
        if self.Diffs == None:
            self.Diffs = DF
        else:
            self.Diffs.AddFile(DF.file)
            self.Diffs.AddContent(DF.content)
        

class CmmtCrawler(Crawler):
    def __init__(self, LangList=[], startNo=0, endNo=65535, RepoList={}):
        super(CmmtCrawler, self).__init__()
        
        self.RepoList   = RepoList
        self.LangCheck  = CFG.Get ('LangConsistCheck')
        self.MinCmmtNum = CFG.Get ('MinCmmtNum')
        self.MaxCmmtNum = CFG.Get ('MaxCmmtNum')

        self.Commits  = []
        self.Exts = ['.h', '.c', '.cpp', '.cc', '.i', '.js', '.css', '.json', '.sh', '.jsx', '.xml', '.yml',
                     '.jade', '.scss', '.coffee', '.py', '.php', '.php3', '.ps1', '.zsh', '.bash', ".sh", '.pl', 
                     '.go', '.sh', '.java', '.asp', '.aspx', '.ashx', '.cs', '.html', '.cls', '.csc', '.cxx', 
                     '.hpp', '.jsp', '.pas', '.phtml', '.s', '.vbs', '.scala', '.as', '.r', '.rb', '.dart', '.rs',
                     '.m', '.mm', '.kt']

        self.startNo = startNo
        self.endNo   = endNo

        self.Scrubber  = Scrubber ()

    def WriteCommts (self, RepoId):
        CmmtFile = Config.BaseDir + "/CmmtSet/" + str (RepoId) + ".csv"
        Header = ['id', 'sha', 'author', 'date', 'issue', 'message', 'file', 'content']
        with open(CmmtFile, 'w', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            writer.writerow(Header)  
            for cmmt in self.Commits:
                if cmmt.Diffs == None:
                    row = [cmmt.id, cmmt.sha, cmmt.author, cmmt.date, cmmt.issue, cmmt.message, "", ""]
                else:
                    row = [cmmt.id, cmmt.sha, cmmt.author, cmmt.date, cmmt.issue, cmmt.message, cmmt.Diffs.file, cmmt.Diffs.content]
                writer.writerow(row)
        CsvFile.close()

    def PassLangs (self, LangFile="lang.ll"):
        if not os.path.exists (LangFile):
            return []
        
        with open(LangFile, 'r', encoding='latin1') as Lfile:
            Langs = []
            for line in Lfile:
                ll = re.findall(r"%  (.+?)\n", line)
                #print ("Line = ", line, ", lang = ", ll)
                if len (ll) == 0:
                    continue

                Lang = ll[0].strip().lower()
                if len (self.LangList) != 0 and Lang not in self.LangList:
                    continue
                Langs.append (Lang)
            #print ("Old langs -> ", Langs)
            return Langs
        
    def CheckLangs (self, Langs, Date='2020-06-01'):
        if self.LangCheck == 0:
            return True
        
        #print ("New langs -> ", Langs)
        CmmDate = None
        Cmmt = None
        for cmmt in self.Commits:
            CmmDate = re.findall('\d{4}-\d{2}-\d{2}', cmmt.date)[0]
            if CmmDate < Date:
                Cmmt = cmmt
                break
        if Cmmt == None:
            Cmmt = self.Commits[-1]
        HistCmd = "git checkout " + Cmmt.sha
        os.system (HistCmd)
        LangCmd = "github-linguist > lang.ll"
        os.system (LangCmd)

        HistLangs = self.PassLangs ()
        if len (HistLangs) == 0:
            return True
        
        if len (HistLangs) < len (Langs):
            #print ("Hist langs -> ", HistLangs)
            return False
        else:
            return True

    def IsInExt (self, Ext):
        lower = Ext.lower ()
        if lower in self.Exts:
            return True
        else:
            return False

    def GetRepoList(self, FileName="RepositoryList.csv"):
        if len (self.RepoList) != 0:
            return
        
        FilePath = Config.BaseDir + '/' + FileName
        df = pd.read_csv(FilePath)
        for index, row in df.iterrows():
            RepoData = Repository (row['Id'], row['Star'], row['Langs'], row['ApiUrl'], row['CloneUrl'], row['Topics'], 
                                   row['Descripe'], row['Created'], row['Pushed'])
            self.RepoList.append (RepoData)
        
    
    def WriteCsv (self, Data, FileName):
        with open(FileName, 'w', encoding='utf-8') as csv_file:       
            writer = csv.writer(csv_file)
            header = list(Data[0].keys()) 
            writer.writerow(header)            
            for item in Data:
                if item != None:
                    row = list(item.values())
                    writer.writerow(row)
        csv_file.close()


    def ParseLog (self, LogFile):
        
        with open(LogFile, 'r', encoding='latin1') as Lfile:
            state = 0
            Cmmt = None
            Message = ""
            Index   = 0
            Df      = None
            DfContent = ""
            for line in Lfile:
                if line[0:2] in ["- ", "@@",  "--", "++", "in"]:
                    continue
                
                if line[0:7] == "commit ":
                    if Df != None:
                        Df.content = self.Scrubber.Cleaning(DfContent) 
                        Cmmt.AddDiff (Df)
                        #print (DfContent)
                        Df = None
                        DfContent = ""
                                
                    Id  = len(self.Commits)
                    Sha = line[8:-1]
                    Cmmt = Commit (Id, Sha, None, None, None)
                    self.Commits.append (Cmmt)
                    state = 0
                elif line[0:8] == "Author: ":
                    Cmmt.author = line[9:-1]
                elif line[0:6] == "Date: ":
                    Cmmt.date = line[7:-1]
                    state = 1
                    Message = ""
                else:
                    if len (line) < 6 :
                        if Message != "":
                           Cmmt.message = Message
                           state = 2
                           Message = ""
                           #print (Cmmt.sha, " -> ", Cmmt.message)
                        continue

                    # message
                    if state == 1:
                        Message += ' ' + line

                    #diff
                    if state == 2:
                        if line[0:12] == "diff --git a":
                            if Df != None:
                                Df.content = self.Scrubber.Cleaning(DfContent)
                                Cmmt.AddDiff (Df)
                                Df = None
                                DfContent = ""
                                #print (DfContent)
                            Path, Name = os.path.split(line[13:-1])
                            File, Ext  = os.path.splitext(Name)
                            self.Extersion [Ext] = True
                            if self.IsInExt (Ext):
                                Df = Diff (Name, "") 
                            
                            continue
                    #diff content
                    if Df != None:
                        DfContent += ' ' + line
                 
    def ParseLogSmp (self, LogFile):      
        import re
        IssueNum = 0
        self.Commits  = []
        with open(LogFile, 'r', encoding='latin1') as Lfile:
            Cmmt   = None
            Author = None
            Date   = None
            Message = ""
            Index   = 0
            for line in Lfile:
                if line[0:7] == "commit ":
                    if Cmmt != None:
                        Cmmt.message = Message
                        Message = ''
                    Id  = len(self.Commits)
                    Sha = line[7:-1]
                    Cmmt = Commit (Id, Sha, None, None, None)
                    self.Commits.append (Cmmt)
                elif line[0:8] == "Author: ":
                    Cmmt.author = line[9:-1]
                elif line[0:7] == "Merge: ":
                    continue
                elif line[0:6] == "Date: ":
                    Cmmt.date = line[7:-1]
                else:
                    if len (line) < 6 :
                        continue
                    
                    issue = re.findall(r"#(\d+?)[\s\r\n]", line)
                    if len (issue) == 0:
                        issue = re.findall(r"/issues/(\d+?)[\s\r\n]", line)
                    if len (issue) != 0:
                        issue = issue[0]
                        if IsNumber (issue) == True:
                            #print ("\tExist issue -> ", line, ", issue -> ", issue)
                            Cmmt.issue = issue
                            IssueNum += 1
   
                    Message += ' ' +  self.Scrubber.Cleaning(line)
                    #print ("Get msg -> ", Message)
            return IssueNum
    
    def CloneLog (self, RepoId, RepoDir, RepoName, Langs):
        Repo = RepoDir + "/" + RepoName     
        os.chdir(Repo)
        print ("@@@ Repo -> ", Repo)

        LogFile = str (RepoId) + ".log"
        #LogCmd = "git log -" + str (self.MaxCmmtNum) + " --date=iso -p > " + LogFile # for ParseLog
        LogCmd = "git log -" + str (self.MaxCmmtNum) + " --date=iso > " + LogFile     # for ParseLogSmp
        os.system (LogCmd)
        print (LogCmd)
        print ("ParseLog....")
        IssueNum = self.ParseLogSmp (LogFile)
        #IssueRate = int (IssueNum*100/len (self.Commits))
        if self.CheckLangs (Langs) == True and len (self.Commits) >= self.MinCmmtNum:
            print ("@@@@@@ CmmtsNum = %d, IssueNum = %d" %(len(self.Commits), IssueNum))
            self.WriteCommts (RepoId)
            #os.remove (LogFile)
            return True
        else:
            RmCmd = "rm -rf " + RepoDir
            os.system (RmCmd)
            return False

    def Clean (self, RepoDir):
        if not os.path.exists (RepoDir):
            return
        os.chdir(RepoDir)
        CleanCmd = "find . -name \".git\" | xargs rm -rf"
        os.system (CleanCmd)
        
    def Clone (self):
        self.Extersion = {}
        self.GetRepoList ()
        
        BaseDir = Config.BaseDir + "/Repository/"
        if not os.path.exists (BaseDir):
            os.mkdir (BaseDir)
        
        Id = 0
        for rId, repo in self.RepoList.items ():
            if Id < self.startNo or Id > self.endNo:
                Id += 1
                continue

            RepoDir = BaseDir + str(repo.Id)
            if Config.AccessTag (str(repo.Id)):
                self.Clean (RepoDir)
                Id += 1
                continue
            
            if not os.path.exists (RepoDir):
                os.mkdir (RepoDir)
            else:
                RmCmd = "rm -rf " + RepoDir + "/*"
                os.system (RmCmd)         
            os.chdir(RepoDir)

            CloneCmd = "git clone " + repo.CloneUrl
            print ("[%d] --> %s" %(Id, CloneCmd))
            os.system (CloneCmd)
            Id += 1

            Langs = repo.Langs
            if self.CloneLog (repo.Id, RepoDir, repo.Name, Langs) == True:
                self.Clean (RepoDir)
            Config.SetTag (str(repo.Id))

    def StartRun (self):
        print ("\t[CmmtCrawler] StartNo: %d, EndNo: %d" %(self.startNo, self.endNo))
        self.Clone ()   
            

