import pandas as pd
from lib.Config import Config
from lib.Analyzer import Analyzer
from lib.NbrAnalyzer import PreNbrData

class NbrData():
    def __init__(self, repo_id, combo, lang, lang_val,     pj_size, lg_num, age, commits_num, developer_num, se_num, se_rem_num, se_iibc_num, se_pd_num, se_other):
        self.repo_id   = repo_id
        self.combo     = combo
        self.lang      = lang
        self.lang_val  = lang_val
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


class NbrAnalyzerSL(Analyzer):

    stat_dir = "Data/StatData/"
    prenbr_stats   = stat_dir + "PreNbr_Stats.csv"

    def __init__(self, StartNo=0, EndNo=65535, InputFile='Repository_Stats.csv', OutputFile='NbrSingleLang_Stats'):
        super(NbrAnalyzerSL, self).__init__(StartNo, EndNo, InputFile, OutputFile)
        self.FilePath = Config.BaseDir + '/' + Config.StatisticDir
        self.LoadRepoList ()

        self.pre_nbr_stats = {}
        self.langs = {}
  
    def UpdateAnalysis(self, repo_item):
        pass

    def load_prenbr (self):
        cdf = pd.read_csv(NbrAnalyzerSL.prenbr_stats)
        for index, row in cdf.iterrows():
            repo_id = row['repo_id']
            combo = row['combo']
            combo = combo.replace ("c#", "csharp")
            combo = combo.replace ("c++", "cpp")
            combo = combo.replace ("objective-c", "objectivec")
            LangList = combo.split ("_")
            for Lang in LangList:
                self.langs [Lang] = 1
            self.pre_nbr_stats[repo_id] = PreNbrData (repo_id, combo, row['pj_size'], row['lg_num'], 
                                                      row['age'], row['cmmt_num'], row['dev_num'], row['se_num'],
                                                      row['se_rem_num'], row['se_iibc_num'], row['se_pd_num'], row['se_other'])

    def get_nbrdata (self, lang):
        for repo_id, predata in self.pre_nbr_stats.items():
            lang_val = 0
            LangList = predata.combo.split ("_")
            if lang in LangList:
                lang_val = 1
            nbrdata = NbrData (predata.repo_id, predata.combo, lang, lang_val, predata.pj_size, predata.lg_num, 
                               predata.age, predata.cmmt_num, predata.dev_num, predata.se_num,
                               predata.se_rem_num, predata.se_iibc_num, predata.se_pd_num, predata.se_other)
            self.AnalyzStats[repo_id] = nbrdata   

    def GetNbrExpr (self,      dv):
        expr = dv + " ~ "
        expr = expr + " + " + "html + javascript + typescript + shell + ruby + go + java + css + csharp + python + c + cpp + php + objectivec + pj_size + lg_num + age + cmmt_num + dev_num"
        return expr
        
    def UpdateFinal(self):
        
        self.load_prenbr ()

        print ("@@@ ALL langs ----> " + str(self.langs.keys()))
        for lang in self.langs.keys ():
            self.get_nbrdata (lang)
            self.SaveData("Nbr_" + lang + '.csv')

        index = 0
        for lang in self.langs.keys ():
            df = pd.read_csv(NbrAnalyzerSL.stat_dir + "Nbr_" + lang +".csv", header=0, 
                             infer_datetime_format=True, parse_dates=[0], index_col=[0])
            if not index:
                cdf = df
            
            cdf[lang] = df['lang_val']
            index += 1
        
        self.PrintTile ('   #Secutiry vulnerabilities vs Single language ')
        self.NbrCompute (cdf, "se_num")
        print ("\r\n\r\n")
        
        self.PrintTile ('   #Risky_resource_management vs Single language ')
        self.NbrCompute (cdf, "se_rem_num")
        print ("\r\n\r\n")
        
        self.PrintTile ('   #Insecure_interaction_between_components vs Single language ')
        self.NbrCompute (cdf, "se_iibc_num")
        print ("\r\n\r\n")
        
        self.PrintTile ('   #Porous_defenses vs Single language ')
        self.NbrCompute (cdf, "se_pd_num")
        print ("\r\n\r\n")

    def SaveData(self,     FileName=None):
        if (len(self.AnalyzStats) == 0):
            return
        
        key0 = list(self.AnalyzStats.keys())[0]
        super(NbrAnalyzerSL, self).SaveData2 (FileName, self.AnalyzStats[key0].__dict__, self.AnalyzStats)
        self.AnalyzStats = {}
        
    def Obj2List(self, value):
        return super(NbrAnalyzerSL, self).Obj2List (value)
                    
    def Obj2Dict(self, value):
        return super(NbrAnalyzerSL, self).Obj2Dict (value)
                    
    def GetHeader(self, data):
        return super(NbrAnalyzerSL, self).GetHeader (data)


