#!/usr/bin/python

from lib.Util import Util
from lib.Analyzer import Analyzer
from lib.Config import Config
from lib.Scrubber import Scrubber

CFG = Config ()
CFG.LoadCfg ()


from progressbar import ProgressBar
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import time
from time import sleep
import re
import os
import ast
import sys
import requests


class SeCategory ():
    def __init__ (self, category, keywords):
        self.category = category
        self.keywords = keywords
        self.count = 0

    def IsMatch (self, keyword):
        if (keyword in self.keywords):
            return True
        else:
            return False

    def AppendKeyword (self, keyword, count):
        self.keywords.append (keyword)
        self.count += count

    def Update (self, count):
        self.count += count

class CmmtLogs():
    def __init__ (self, sha, message, catetory, matched):
        self.sha      = sha
        self.message  = message
        self.catetory = catetory
        self.matched  = matched

class CmmtLogAnalyzer(Analyzer):

    def __init__(self, StartNo=0, EndNo=65535, RegexMode=False, FileName='CmmtLogAnalyzer.csv'):
        super(CmmtLogAnalyzer, self).__init__(StartNo=StartNo, EndNo=EndNo, FileName=FileName)
        self.RegexMode = RegexMode 
        self.Scrubber  = Scrubber ()
        self.keywords  = self.LoadKeywords ()
        self.CommitNum = 0
        self.RepoNum   = 0
        self.MaxCommitNum = CFG.Get ('MaxCmmtNum')
        self.MinLangs = CFG.Get ('MinLangs')
        
        self.SeCategoryStats = {}
        self.InitSecategory ()

    def InitSecategory (self):
        
        self.SeCategoryStats[0] = SeCategory ("Risky_resource_management", 
                                                ['path traversal', 'deadlock', 'data race', 'data leak', 'buffer overflow', 'stack overflow', 'memory overflow', 'Out memory',
                                                 'integer overflow', 'integer underflow', 'overrun', 'integer wraparound', 'uncontrolled format', 'Data loss', 'uninitialized memory',
                                                 'dangerous function', 'untrusted control', 'improper limitation', 'Improper Validation', 'integrity check', 'null pointer', 
                                                 'missing init', 'Incorrect Length', 'Forced Browsing', 'User-Controlled Key', 'Critical Resource', 'Exposed Dangerous',
                                                 'crashing length', 'Memory corruption', 'Memory leak', 'Double free', 'Use after free', 'Dangling pointers', 'overflow fix', 'boundary check'])
  
        self.SeCategoryStats[1] = SeCategory ("Insecure_interaction_between_components", 
                                                ['sql injection', 'command injection', 'csrf', 'cross site', 'Request Forgery', 'sqli', 'xsrf', 'backdoor', 'Open Redirect',
                                                 'untrusted site', 'specialchar', 'unrestricted upload', 'unrestricted file', 'man in the middle', 'reflected xss', 'get based xss',
                                                 'Improper Neutralization', 'Dangerous Type', 'Cursor Injection', 'Dangling Database Cursor', 'Unintended Proxy', 'Unintended Intermediary',
                                                 'Argument Injection', 'Argument Modification', 'XSS Manipulation', 'Incomplete Blacklist', 'Origin Validation Error'])

        self.SeCategoryStats[2] = SeCategory ("Porous_defenses", 
                                                ['missing authentication', 'missing authorization', 'hard coded credential', 'missing encryption', 'untrusted input', 'unnecessary privilege', 
                                                 'sensitive data', 'User-Controlled Key', 'Authorization Bypass',  'Hard coded Password', 'Hard coded Cryptographic', 'Key Management Error',
                                                 'incorrect authorization', 'incorrect permission', 'broken cryptographic', 'risky cryptographic', 'excessive authentication', 'privilege escalation',
                                                 'without a salt', 'unauthenticated', 'information disclosure', 'authentication bypass', 'cnc vulnerability', 'access control', 'cleartext storage',
                                                 'Least Privilege Violation', 'Insufficient Compartmentalization', 'Dropped Privileges', 'Assumed Immutable Data', 'Insufficient Entropy',
                                                 'Cryptographically Weak PRNG', 'adaptive chosen ciphertext', 'chosen ciphertext attack', 'Authorization Bypass'])

        self.SeCategoryStats[3] = SeCategory ("General", 
                                                ['security', 'denial service', 'insecure', 'penetration', 'bypass security', 'crash', 'vulnerability fix'])

        if self.RegexMode == True:
            self.RegexCompile ()         
            #self.RegexMatchTest ()
        else:
            self.threshhold = 90
            #self.FuzzTest ()

        #TotalPhrase = 0
        #for Id, Sec in self.SeCategoryStats.items():
        #    keywords = Sec.keywords
        #    print ("===> %s ---- key phrase number ---->%d" %(Sec.category, len(keywords)))
        #    TotalPhrase += len(keywords)
        #print ("===> Whole ---- key phrase number ---->%d" %(TotalPhrase))

    def RegexCompile (self):
        for Id, Sec in self.SeCategoryStats.items():
            keywords = Sec.keywords
            regx = r''
            for key in keywords:
                if len (regx) != 0:
                    regx += '|'
                regx += key
            Sec.reEngine = re.compile (regx)
        
    def RegexMatchTest (self):
        for Id, Sec in self.SeCategoryStats.items():
            reEngine = Sec.reEngine
            keywords = " ".join(Sec.keywords)
            CleanText = self.Scrubber.CleanText (keywords)
            Res = reEngine.match (keywords)
            print (CleanText, " ---> ", Res)
            if Res != None:
                print (Sec.category, " >>> match ---> success!!")
            else:
                print (Sec.category, " >>> match ---> fail!!")

    def RegexMatch (self, message, threshhold=0):
        message = " ".join(message)
        for Id, Sec in self.SeCategoryStats.items():
            reEngine = Sec.reEngine
            Res = reEngine.match (message)
            if Res != None:
                #Sec.count += 1
                return Sec.category, Res.group(0)
        return None, None 

    def FuzzTest (self):
        message = ['sqli',  'injection', 'commands', 'injection']
        Clf, Matched = self.FuzzMatch (message, self.threshhold)
        if Clf == "Insecure_interaction_between_components":
            print ("\t fuzz_match_test -> %s pass!!!!" %message)
        else:
            print ("\t fuzz_match_test -> %s fail!!!!" %message)

        message = ['path',  'traversal', 'deadlock', 'race']
        Clf, Matched = self.FuzzMatch (message, self.threshhold)
        if Clf == "Risky_resource_management":
            print ("\t fuzz_match_test -> %s pass!!!!" %message)
        else:
            print ("\t fuzz_match_test -> %s fail!!!!" %message)

        message = ['hard', 'coded', 'credential', 'encryption']
        Clf, Matched = self.FuzzMatch (message, self.threshhold)
        if Clf == "Porous_defenses":
            print ("\t fuzz_match_test -> %s pass!!!!" %message)
        else:
            print ("\t fuzz_match_test -> %s fail!!!!" %message)

    
    def FuzzMatch(self, message, threshhold=90):  
        fuzz_results = {}
        #print ("FuzzMatch -> ", message)
        for Id, Sec in self.SeCategoryStats.items():
            keywords = Sec.keywords
            for str in keywords:
                key_len = len(str.split())
                msg_len = len (message)
                gram_meg = []
                
                if key_len < msg_len:
                    for i in range (0, len (message)):
                        end = i + key_len
                        if end > msg_len:
                            break
                        msg = " ".join(message[i:end])
                        gram_meg.append (msg)
                    #print ("\t[%s][%s] Try -> %s" %(Sec.category, str, gram_meg))
                    result = process.extractOne(str, gram_meg, scorer=fuzz.ratio)
                    #print ("\t\t1 => [%s][%f]fuzz match" %(result[0], result[1]))
                    if (result[1] >= threshhold):
                        fuzz_results[result[0]] = int (result[1])           
                        #Sec.count += 1
                        return Sec.category, fuzz_results 
                elif key_len == msg_len:
                    msg = " ".join(message)
                    gram_meg.append (msg)
                    result = process.extractOne(str, gram_meg, scorer=fuzz.ratio)
                    #print ("\t\t2 => [%s][%f]fuzz match" %(result[0], result[1]))
                    if (result[1] >= threshhold):
                        fuzz_results[result[0]] = int (result[1])
                        
                        #Sec.count += 1
                        return Sec.category, fuzz_results
                
                
        return None, None

    def FormalizeMsg (self, message):
        message = str (message)
        if (message == ""):
            return []
        
        CleanText = self.Scrubber.CleanText (message, 64)
        if (CleanText == ""):
            return []

        return self.Scrubber.Subject(CleanText, 3)

    def IsProcessed (self, CmmtStatFile):
        CmmtStatFile = CmmtStatFile + ".csv"
        return Config.IsExist (CmmtStatFile)

    def IsSegFin (self, RepoNum):
        if ((RepoNum < self.StartNo) or (RepoNum >= self.EndNo)):
            return True
        return False  
                
    def UpdateAnalysis(self, RepoItem):
        StartTime = time.time()

        LangNum = len (RepoItem.Langs)
        if LangNum < self.MinLangs:
            return

        self.RepoNum += 1
        if (self.IsSegFin (self.RepoNum)):
            return
        
        RepoId   = RepoItem.Id
        CmmtFile = Config.CmmtFile (RepoId)
        if (Config.IsExist (CmmtFile) == False):
            return

        cdf = pd.read_csv(CmmtFile)
        CmmtStatFile = Config.CmmtStatFile (RepoId)
        if self.IsProcessed (CmmtStatFile) or os.path.exists(CmmtStatFile):
            if (cdf.shape[0] < self.MaxCommitNum):
                self.CommitNum += cdf.shape[0]
            else:
                self.CommitNum += self.MaxCommitNum
            print ("[%u]%u -> accumulated commits: %u, timecost:%u s" %(self.RepoNum, RepoId, self.CommitNum, int(time.time()-StartTime)))
            return
                
        print ("[%u]%u start...commit num:%u" %(self.RepoNum, RepoId, cdf.shape[0]))
        for index, row in cdf.iterrows():
            self.CommitNum += 1

            message = str(row['message']) #+ " " + row['content']
            message = self.FormalizeMsg (message)
            if len (message) == 0:
                continue
                
            #print ("Message length -> %d " %len (message))
            Clf = None
            Matched = None
            if self.RegexMode == True:
                Clf, Matched = self.RegexMatch (message)
            else:
                Clf, Matched = self.FuzzMatch (message, self.threshhold)
            
            if Clf != None:
                #print (Clf)
                No = len (self.AnalyzStats)
                self.AnalyzStats[No] = CmmtLogs (row['sha'], message, Clf, Matched)
                print ("<%d>[%d/%d] retrieve cmmits -> %d" %(self.RepoNum, index, cdf.shape[0], No))
            if (index >= self.MaxCommitNum):
                break

        #save by repository
        print ("[%u]%u -> accumulated commits: %u, timecost:%u s" %(self.RepoNum, RepoId, self.CommitNum, int(time.time()-StartTime)) )
        self.SaveData (str(RepoId))
        self.AnalyzStats = {}

    def ClassifySeC (self, Msg):
        message = self.FormalizeMsg (Msg)
        if (message == None):
            return "None"

        Clf, Matched = self.FuzzMatch (message, 90)
        if Clf != None:
            for id, secate in self.SeCategoryStats.items ():
                if Clf == secate.category:
                    print ("@@@@ Match %s!!!" %secate.category)
                    return secate.category                  
            return "None"            
        else:
            #print ("@@@@ Match None!!!")
            return "None"
        
    def UpdateFinal (self):
        print ("Final: repo_num: %u -> accumulated commits: %u" %(self.RepoNum, self.CommitNum))

        CmmtStatDir = os.walk("./Data/StatData/CmmtSet")
        keywors_stats = {}
        for Path, DirList, FileList in CmmtStatDir:  
            for FileName in FileList:
                StatFile = os.path.join(Path, FileName)
                FileSize = os.path.getsize(StatFile)/1024
                if (FileSize == 0):
                    continue
                cdf = pd.read_csv(StatFile)
                for index, row in cdf.iterrows():
                    Clf = row['catetory']
                    for Id, Sec in self.SeCategoryStats.items():
                        if Sec.category == Clf:
                            Sec.count += 1                 
        super(CmmtLogAnalyzer, self).SaveData2 ("/StatData/SeCategory_Stats", self.SeCategoryStats[0].__dict__, self.SeCategoryStats)
        

    def LoadKeywords(self):
        df_keywords = pd.read_table(Config.KEYWORD_FILE)
        df_keywords.columns = ['key']
        return df_keywords['key']

    def SaveData (self, FileName=None):
        if (len(self.AnalyzStats) == 0):
            if FileName != None:
                Empty = "touch " + FileName
                os.system (Empty)
            return
        super(CmmtLogAnalyzer, self).SaveData2 ("/StatData/CmmtSet/" + FileName, self.AnalyzStats[0].__dict__, self.AnalyzStats)
         
    def Obj2List (self, value):
        return super(CmmtLogAnalyzer, self).Obj2List (value)

    def Obj2Dict (self, value):
        return super(CmmtLogAnalyzer, self).Obj2Dict (value)

    def GetHeader (self, data):
        return super(CmmtLogAnalyzer, self).GetHeader (data)


    
