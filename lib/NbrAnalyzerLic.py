
from lib.Analyzer import Analyzer
from lib.NbrAnalyzer import PreNbrData
import pandas as pd

class NbrData():
    def __init__(self, repo_id, apity, apity_num, pj_size, lg_num, age, commits_num, developer_num, se_num, se_rem_num, se_iibc_num, se_pd_num, se_other):
        self.repo_id   = repo_id
        self.apity     = apity
        self.apity_num = apity_num
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


class NbrAnalyzerLic(Analyzer):

    stat_dir = "Data/StatData/"
    prenbr_stats   = stat_dir + "PreNbr_Stats.csv"
    apitype_stats  = stat_dir + "ApiSniffer.csv"

    def __init__(self, StartNo=0, EndNo=65535, InputFile='RepositoryList.csv', OutputFile='NbrAPI_Stats'):
        super(NbrAnalyzerLic, self).__init__(StartNo, EndNo, InputFile, OutputFile)

        self.pre_nbr_stats = {}
        self.apitypes = {}
        self.apitypes_set = None
  
    def UpdateAnalysis(self, repo_item):
        pass

    def load_apitypes (self):
        cdf = pd.read_csv(NbrAnalyzerLic.apitype_stats)
        for index, row in cdf.iterrows():
            clfType = row['clfType']
            if clfType == None:
                continue
            self.apitypes[row['id']] = clfType
            apitypes = set (self.apitypes.values())
        return apitypes

    def load_prenbr (self):
        cdf = pd.read_csv(NbrAnalyzerLic.prenbr_stats)
        for index, row in cdf.iterrows():
            repo_id = row['repo_id']
            combo = row['combo']
            combo = combo.replace ("c++", "cpp")
            combo = combo.replace ("objective-c", "objectivec")
            self.pre_nbr_stats[repo_id] = PreNbrData (repo_id, combo, row['pj_size'], row['lg_num'], 
                                                      row['age'], row['cmmt_num'], row['dev_num'], row['se_num'],
                                                      row['se_rem_num'], row['se_iibc_num'], row['se_pd_num'], row['se_other']) 

    def get_nbrdata (self, apity):
        for repo_id, predata in self.pre_nbr_stats.items():
            api_num = 0
            cur_apity = self.apitypes.get (repo_id)
            if cur_apity != None:
                if ((cur_apity in apity) or (apity in cur_apity)):
                    api_num = 1
            nbrdata = NbrData (predata.repo_id, cur_apity, api_num, predata.pj_size, predata.lg_num, 
                               predata.age, predata.cmmt_num, predata.dev_num, predata.se_num,
                               predata.se_rem_num, predata.se_iibc_num, predata.se_pd_num, predata.se_other)
            self.AnalyzStats[repo_id] = nbrdata
        
    def GetNbrExpr (self,      dv):
        expr = dv + " ~ "
        Init = True
        for api in self.apitypes_set:
            if Init == True:
                expr = expr + api
                Init = False
            else:
                expr = expr + " + " + api
        expr = expr + " + " +"pj_size + lg_num + age + cmmt_num + dev_num"
        return expr
  
    def UpdateFinal(self):
        
        self.load_prenbr ()
        self.apitypes_set = self.load_apitypes ()
        print ("@@@@@@@@@@ apitypes => ", self.apitypes_set)

        for apity in self.apitypes_set:
            self.get_nbrdata (apity)
            self.SaveData(apity)

        index = 0
        for apity in self.apitypes_set:
            df = pd.read_csv(NbrAnalyzerLic.stat_dir + apity +".csv", header=0, 
                             infer_datetime_format=True, parse_dates=[0], index_col=[0])
            if not index:
                cdf = df
            
            cdf[apity] = df['apity_num']
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
        super(NbrAnalyzerLic, self).SaveData2 ("/StatData/" + FileName, self.AnalyzStats[key0].__dict__, self.AnalyzStats)
        self.AnalyzStats = {}
        
    def Obj2List(self, value):
        return super(NbrAnalyzerLic, self).Obj2List (value)
                    
    def Obj2Dict(self, value):
        return super(NbrAnalyzerLic, self).Obj2Dict (value)
                    
    def GetHeader(self, data):
        return super(NbrAnalyzerLic, self).GetHeader (data)

