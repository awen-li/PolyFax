#!/usr/bin/python

from lib.Util import Util
from lib.Analyzer import Analyzer
from lib.Config import Config
from lib.Scrubber import Scrubber

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
        self.reEngine = None

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

    def __init__(self, StartNo=0, EndNo=65535, RegexMode=False, FileName='CmmtLogs_Stats'):
        super(CmmtLogAnalyzer, self).__init__(FileName=FileName)
        self.RegexMode = RegexMode 
        self.Scrubber  = Scrubber ()
        self.keywords  = self.LoadKeywords ()
        self.CommitNum = 0
        self.RepoNum   = 0
        self.StartNo   = StartNo
        self.EndNo     = EndNo
        self.MaxCommitNum = Config.MAX_CMMT_NUM
        
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
            self.RegexMatchTest ()
        else:
            self.threshhold = 90
            self.FuzzTest ()

        TotalPhrase = 0
        for Id, Sec in self.SeCategoryStats.items():
            keywords = Sec.keywords
            print ("===> %s ---- key phrase number ---->%d" %(Sec.category, len(keywords)))
            TotalPhrase += len(keywords)
        print ("===> Whole ---- key phrase number ---->%d" %(TotalPhrase))

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
        print (self.SeCategoryStats)
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
        return Config.is_exist (CmmtStatFile)

    def IsSegFin (self, RepoNum):
        if ((RepoNum < self.start_no) or (RepoNum >= self.end_no)):
            return True
        return False  
                
    def __UpdateAnalysis(self, RepoItem):
        StartTime = time.time()

        if ((RepoItem.languages_used < 2) or (len(RepoItem.language_combinations) == 0)):
            return

        self.RepoNum += 1
        if (self.IsSegFin (self.RepoNum)):
            return
        
        RepoId   = RepoItem.id
        CmmtFile = Config.CmmtFile (RepoId)
        if (Config.is_exist(CmmtFile) == False):
            return

        cdf = pd.read_csv(CmmtFile)
        CmmtStatFile = Config.CmmtStatFile (RepoId)
        if self.IsProcessed (cmmt_stat_file) or os.path.exists(CmmtStatFile):
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
                No = len (self.research_stats)
                self.research_stats[No] = CmmtLogs (row['sha'], message, Clf, Matched)
                print ("<%d>[%d/%d] retrieve cmmits -> %d" %(self.RepoNum, index, cdf.shape[0], No))
            if (index >= self.MaxCommitNum):
                break

        #save by repository
        print ("[%u]%u -> accumulated commits: %u, timecost:%u s" %(self.RepoNum, RepoId, self.CommitNum, int(time.time()-StartTime)) )
        self.SaveData (CmmtStatFile)
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
        
    def __UpdateFinal (self):
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
        super(CmmtLogAnalyzer, self).SaveData2 (self.SeCategoryStats, "./Data/StatData/SeCategory_Stats")
        

    def LoadKeywords(self):
        df_keywords = pd.read_table(System.KEYWORD_FILE)
        df_keywords.columns = ['key']
        return df_keywords['key']

    def SaveData (self, file_name=None):
        if (len(self.research_stats) == 0):
            if file_name != None:
                Empty = "touch " + file_name
                os.system (Empty)
            return
        super(CmmtLogAnalyzer, self).SaveData2 (self.AnalyzStats, file_name)
         
    def __Obj2List (self, value):
        return super(CmmtLogAnalyzer, self).__Obj2List (value)

    def __Obj2Dict (self, value):
        return super(CmmtLogAnalyzer, self).__Obj2Dict (value)

    def __GetHeader (self, data):
        return super(CmmtLogAnalyzer, self).__GetHeader (data)


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
    def __init__(self, StartNo=0, EndNo=65535, FileName='CmmtLogs_Issues'):
        super(IssueAnalyzer, self).__init__(FileName=FileName)
        self.RepoNum   = 0
        self.StartNo   = StartNo
        self.EndNo     = EndNo

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
                              auth=("yifanlee", "c32ae4e7dfa97983fda72d09aa24acf3bbe2635c"),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (self.IsContinue (result.status_code) == False):
            #print("$$$%s: %s, URL: %s" % (result.status_code, result.reason, url))
            return None
        
        if (result.status_code != 200 and result.status_code != 422):
            print("%s: %s, URL: %s" % (result.status_code, result.reason, url))
            sleep(1200)
            return self.GetIssue(url, issue)     
        return result.json()
                
    def __UpdateAnalysis(self, Repo):

        self.RepoNum += 1
        if (self.IsSegfin (self.RepoNum)):
            return
        
        RepoId   = Repo.id
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

            IssJson = self.GetIssue (Repo.url, IsNo)
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

        self.save_data (IssueFile)
        self.AnalyzStats = {}

    def __UpdateFinal (self):
        pass

    def SaveData (self, FileName=None):
        if (len(self.AnalyzStats) == 0):
            if FileName != None:
                Empty = "touch " + FileName
                os.system (Empty)
            return
        super(IssueAnalyzer, self).SaveData2 (self.AnalyzStats, FileName)
                     
    def __Obj2List(self, value):
        return super(IssueAnalyzer, self).__Obj2List (value)
            
    def __Obj2Dict(self, value):
        return super(IssueAnalyzer, self).__Obj2Dict (value)
            
    def __GetHeader(self, data):
        return super(IssueAnalyzer, self).__GetHeader (data)
    
