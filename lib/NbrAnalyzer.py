
from lib.Analyzer import Analyzer
from lib.Config import Config
from datetime import datetime, timedelta
import time
import re
import pandas as pd


class SeCategory ():
    def __init__ (self, category, keywords):
        self.category = category
        self.keywords = keywords


class PreNbrData():
    def __init__(self, repo_id, combo, pj_size, lg_num, age, commits_num, developer_num, se_num,
                   se_rem_num, se_iibc_num, se_pd_num, se_other):
        self.repo_id  = repo_id
        self.combo    = combo
        self.pj_size  = pj_size    
        self.lg_num   = lg_num
        self.age      = age
        self.cmmt_num = commits_num
        self.dev_num  = developer_num
        self.se_num   = se_num
        self.se_rem_num  = se_rem_num
        self.se_iibc_num = se_iibc_num
        self.se_pd_num   = se_pd_num
        self.se_other    = se_other

    def update (self, age, cmmt_num, dev_num, se_num):
        self.age      = age
        self.cmmt_num = cmmt_num
        self.dev_num  = dev_num
        self.se_num   = se_num

    def update_secategory (self, se_rem_num, se_iibc_num, se_pd_num, se_other):
        self.se_rem_num  = se_rem_num
        self.se_iibc_num = se_iibc_num
        self.se_pd_num   = se_pd_num
        self.se_other    = se_other


class NbrData():
    def __init__(self, repo_id, combo, combo_num, pj_size, lg_num, age, commits_num, developer_num, se_num, se_rem_num, se_iibc_num, se_pd_num, se_other):
        self.repo_id   = repo_id
        self.combo     = combo
        self.combo_num = combo_num
        self.pj_size   = pj_size    
        self.lg_num    = lg_num
        self.age       = age
        self.cmmt_num  = commits_num
        self.dev_num   = developer_num
        self.se_num    = se_num
        self.se_rem_num  = se_rem_num
        self.se_iibc_num = se_iibc_num
        self.se_pd_num   = se_pd_num
        self.se_other    = se_other


class NbrAnalyzer(Analyzer):

    stat_dir = "Data/StatData/"
    prenbr_stats   = stat_dir + "PreNbr_Stats.csv"
    topcombo_stats = stat_dir + "LangCombo_Stats.csv"

    def __init__(self, StartNo=0, EndNo=65535, InputFile='RepositoryList.csv', OutputFile='PreNbr_Stats'):
        super(NbrAnalyzer, self).__init__(StartNo, EndNo, InputFile, OutputFile)
        
        self.RepoNum = 0  
        self.max_cmmt_num = Config.MAX_CMMT_NUM
        self.pre_nbr_stats = {}
        self.topcombo = []
        self.secategory_stats = {}

        self.load_secategory ()

    def is_prenbr_ready (self):
        return Config.IsExist(NbrAnalyzer.prenbr_stats)

    def load_secategory (self):
        file = "./Data/StatData/SeCategory_Stats.csv"
        cdf = pd.read_csv(file)
        for index, row in cdf.iterrows():
            self.secategory_stats[index] = SeCategory (row['category'], row['keywords'])

    def get_secategory (self, catetory):
        for id, secate_stat in self.secategory_stats.items ():
            if catetory == secate_stat.category:
                return id
        return None

    def get_cmmtinfo (self, NbrStats):
        repo_id = NbrStats.repo_id

        cmmt_file = Config.CmmtFile (repo_id)
        if (Config.is_exist(cmmt_file) == False):
            return

        #developers & commit_num
        cdf = pd.read_csv(cmmt_file)
        
        commits_num = 0
        if (cdf.shape[0] < self.max_cmmt_num):
            commits_num = cdf.shape[0]
        else:
            commits_num = self.max_cmmt_num

        developers = {}
        max_date   = "1999-01-01 13:44:12"
        min_date   = "2020-12-31 13:44:12"
        for index, row in cdf.iterrows():
            developers[row['author']] = 1
            date = row['date']
            date = re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date)[0]
            if (date > max_date):
                max_date = date
            if (date < min_date):
                min_date = date
        developer_num = len (developers)

        max_time = datetime.strptime(max_date, '%Y-%m-%d %H:%M:%S')
        min_time = datetime.strptime(min_date, '%Y-%m-%d %H:%M:%S')
        age = (max_time - min_time).days
        
            
        #security bug num
        cmmt_stat_file = Config.CmmtStatFile (repo_id) + ".csv"
        if Config.is_exist(cmmt_stat_file) == False:
            NbrStats.update (age, commits_num, developer_num, 0)
            NbrStats.update_secategory (0, 0, 0, 0)      
            self.pre_nbr_stats[repo_id] = NbrStats
            return
            
        cdf = pd.read_csv(cmmt_stat_file)
        se_num = cdf.shape[0]
        NbrStats.update (age, commits_num, developer_num, se_num)

        #se categories
        se_rem_num  = 0
        se_iibc_num = 0 
        se_pd_num = 0
        se_other = 0
        for index, row in cdf.iterrows():
            catetory = row['catetory']
            seId = self.get_secategory (catetory)
            if seId == None:
                continue
            if (seId == 0):
                se_rem_num += 1
            elif (seId == 1):
                se_iibc_num += 1
            elif (seId == 2):
                se_pd_num += 1
            else:
                se_other += 1
        
        NbrStats.update_secategory (se_rem_num, se_iibc_num, se_pd_num, se_other)          
        self.pre_nbr_stats[repo_id] = NbrStats


    def IsSegfin (self, RepoNum):
        if RepoNum < self.StartNo  or RepoNum >= self.EndNo:
            return True
        return False

    
    def UpdateAnalysis(self, repo_item):
        start_time = time.time()
        if (self.is_prenbr_ready ()):
            return
        
        self.RepoNum += 1      
        if ((repo_item.languages_used < 2) or (len(repo_item.language_combinations) == 0)):
            return
       
        repo_id = repo_item.id

        combo = "".join (repo_item.language_combinations)
        combo = combo.replace ("c++", "cpp")
        combo = combo.replace ("objective-c", "objectivec")
        combo = combo.replace (" ", "_")

        #basic
        NbrStats = PreNbrData (repo_id, combo, repo_item.size, repo_item.languages_used, 0, 0, 0, 0, 0, 0, 0, 0)     
        
        #commits
        self.get_cmmtinfo (NbrStats)

        print ("[%u]%u -> timecost:%u s" %(self.RepoNum, repo_id, int(time.time()-start_time)) )

    def load_prenbr (self):
        cdf = pd.read_csv(NbrAnalyzer.prenbr_stats)
        for index, row in cdf.iterrows():
            repo_id = row['repo_id']
            combo = row['combo']
            combo = combo.replace ("c++", "cpp")
            combo = combo.replace ("objective-c", "objectivec")
            self.pre_nbr_stats[repo_id] = PreNbrData (repo_id, combo, row['pj_size'], row['lg_num'], 
                                                      row['age'], row['cmmt_num'], row['dev_num'], row['se_num'],
                                                      row['se_rem_num'], row['se_iibc_num'], row['se_pd_num'], row['se_other']) 

    def load_top_combo (self, top_num=50):
        print ("===================> top language selections:")
        cdf = pd.read_csv(NbrAnalyzer.topcombo_stats)
        for index, row in cdf.iterrows():
            combo = row['combination']
            combo = combo.replace ("c++", "cpp")
            combo = combo.replace ("c#", "csharp")
            combo = combo.replace ("objective-c", "objectivec")
            combo = combo.replace (" ", "_")
            self.topcombo.append(combo)
            print ("\t\t%-32s %-10s %.2f%%" %(combo, "-", row['distribution']*100))
            if (index >= top_num):
                break
        return

    def get_nbrdata (self, combo):
        for repo_id, predata in self.pre_nbr_stats.items():
            combo_num = 0
            if ((combo in predata.combo) or (predata.combo in combo)):
                combo_num = 1
            nbrdata = NbrData (predata.repo_id, predata.combo, combo_num, predata.pj_size, predata.lg_num, 
                               predata.age, predata.cmmt_num, predata.dev_num, predata.se_num,
                               predata.se_rem_num, predata.se_iibc_num, predata.se_pd_num, predata.se_other)
            self.AnalyzStats[repo_id] = nbrdata


    def GetNbrExpr (self, dv):
        expr = dv + " ~ "
        Init = True
        for combo in self.topcombo:
            if Init == True:
                expr = expr + combo
                Init = False
            else:
                expr = expr + " + " + combo
        expr = expr + " + " +"pj_size + lg_num + age + cmmt_num + dev_num"
        return expr
    
    def UpdateFinal(self):
        if (len(self.pre_nbr_stats) == 0):
            self.load_prenbr ()
        else:
            super(NbrAnalyzer, self).save_data2(self.pre_nbr_stats, None)

        self.load_top_combo ()

        for combo in self.topcombo:
            #print ("NMR --- %s " %combo)
            #print ("%s + " %combo, end="")
            self.get_nbrdata (combo)
            self.SaveData(combo)

        index = 0
        for combo in self.topcombo:
            df = pd.read_csv(NbrAnalyzer.stat_dir + combo+".csv", header=0, 
                             infer_datetime_format=True, parse_dates=[0], index_col=[0])
            if not index:
                cdf = df
            
            cdf[combo] = df['combo_num']
            index += 1
        
        #Setup the regression expression in patsy notation. 
        #We are telling patsy that se_num is our dependent variable 
        #and it depends on the regression variables: combinations .... project variables

        print ("==================================== secutiry vulnerabilities ====================================")
        self.NbrCompute (cdf, "se_num")
        print ("\r\n\r\n")
        
        print ("==================================== Risky_resource_management ====================================")
        self.NbrCompute (cdf, "se_rem_num")
        print ("\r\n\r\n")

        print ("==================================== Insecure_interaction_between_components ====================================")
        self.NbrCompute (cdf, "se_iibc_num")
        print ("\r\n\r\n")
       
        print ("==================================== Porous_defenses ====================================")
        self.NbrCompute (cdf, "se_pd_num")
        print ("\r\n\r\n")

    def SaveData(self,     FileName=None):
        if (len(self.AnalyzStats) == 0):
            return

        key0 = list(self.AnalyzStats.keys())[0]
        super(NbrAnalyzer, self).SaveData2 ("/StatData/" + FileName, self.AnalyzStats[key0].__dict__, self.AnalyzStats)
        self.AnalyzStats = {}

    def Obj2List(self, value):
        return super(NbrAnalyzer, self).Obj2List (value)
            
    def Obj2Dict(self, value):
        return super(NbrAnalyzer, self).Obj2Dict (value)
            
    def GetHeader(self, data):
        return super(NbrAnalyzer, self).GetHeader (data)

