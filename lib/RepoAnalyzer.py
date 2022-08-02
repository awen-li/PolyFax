
from lib.Util import Util
from lib.Analyzer import Analyzer
from lib.Config import Config
from lib.Scrubber import Scrubber
from lib.Repository import Repository
from progressbar import ProgressBar
import pandas as pd
import os
import sys

class RepoStats():

    def __init__(self, repo, top_langs):
        cur_top_langs = top_langs
        repo.LangsDict = eval (repo.LangsDict)

        self.repo = repo
        self.repo.LangsDict = Util.dictsort_value(repo.LangsDict, True)
        
        total_bytes_written = sum(list(repo.LangsDict.values()))
        language_distribution = self.repo.LangsDict.copy()
        LangsDist = {}
        for key in language_distribution.keys():
            LangsDist[key] = language_distribution[key]/total_bytes_written
        self.repo.LangsDist = LangsDist 

        self.all_languages = repo.Langs
        self.all_languages.sort()

        language_combinations = Util.create_unique_combo_list(
            self.all_languages,
            len(self.all_languages),
            max_combo_count=20,
            min_combo_count=2
        )

        language_combinations_new = []          
        for n in range (2, 6, 1):
            n_combinations = self._get_n_combination (n, cur_top_langs)
            if (len (n_combinations) == n):      
                language_combinations_new.append(n_combinations)

        self.repo.LangCombo = language_combinations_new

    def _get_n_combination (self, n, cur_top_langs):
        all_languages = []
        # only select language from the top languages
        for lang in self.all_languages:
            if lang in cur_top_langs:
                all_languages.append (lang)

        n_combination = []
        if (n <= len (all_languages)):
            n_combination = all_languages[0:n:1]
            n_combination.sort()
            if " ".join (n_combination) == 'css html':
                return []
        return n_combination
        

class LangComboStats():

    Header_Names = ["id", "combination", "count", "distribution"]

    def __init__(self, id, combination):
        self.combo_id = id
        self.combination = combination
        self.count = 0
        self.distribution = 0.0
        self.language_used = len(list(combination.split(" ")))

    def update(self):
        self.count = self.count + 1

    def update_distribution(self, total_combination):
        self.distribution = self.count/total_combination      

    def object_to_list(self, key):
        values = [self.combo_id]
        values.append(self.combination)
        values.append(self.count)
        values.append(self.distribution)

    def object_to_dict(self, key):
        keys = LangCombo_Stats.Header_Names
        values = self.object_to_list("")
        return {key: value for key, value in zip(keys, values)}


class RepoAnalyzer (Analyzer):
    def __init__(self, StartNo=0, EndNo=65535, InputFile='RepositoryList.csv', OutputFile='Repository_Stats.csv'):
        super(RepoAnalyzer, self).__init__(StartNo, EndNo, InputFile, OutputFile)
        self.RepoNum   = 0
        
        self.TopLangs  = []
        self.LoadTopLangs()

        self.ComboStats = {}
        self.AllComboStats = {}
        self.AllLanguageComboNum = 0

    def IsSegfin (self, RepoNum):
        if RepoNum < self.StartNo  or RepoNum >= self.EndNo:
            return True
        return False

    def LoadTopLangs (self, TopNum=50):
        LangFile = 'Data/Config/all_languages.txt'
        with open (LangFile, 'r') as LF:
            AllLines = LF.readlines ()
            lang_num = 0
            for line in AllLines:
                lang = line.replace('\n', '')
                self.TopLangs.append (lang.lower())
                lang_num += 1
                if lang_num >= TopNum:
                    break
                
    def UpdateAnalysis(self, Repo):

        self.RepoNum += 1
        if (self.IsSegfin (self.RepoNum)):
            return

        CmmtFile = Config.CmmtFile (Repo.Id)
        if Config.IsExist(CmmtFile) == False:
            return
        
        UpdatedRepo = RepoStats(Repo, self.TopLangs).repo
        self.AnalyzStats[self.RepoNum-1] = UpdatedRepo
                
        #update count of each combination
        if (UpdatedRepo.LangNum > 1):
            self.LangComboStat(UpdatedRepo)

    def LangComboStat(self, RepoStat):
        for combo in RepoStat.LangCombo:
            combo = ' '.join(combo)
            #print ("===> combo = " + str(combo))
            langcombo_stat = self.ComboStats.get(combo, None)
            if (langcombo_stat == None):
                langcombo_stat = LangComboStats(0, combo)
                self.ComboStats[combo] = langcombo_stat
            langcombo_stat.update()  

    def UpdateFinal (self):
        self.ComboStats = self.GetTopcombos(50)
        for combo, stat in self.ComboStats.items():
            stat.update_distribution (self.AllLanguageComboNum)

        print ("---> Update repo with top language combination...")
        self.UpdateRepoCombo()

        self.SaveData (self.FileName)

    def UpdateRepoCombo(self):
        AnlyStats = {}
        pbar = ProgressBar()
        for index, repo_item in pbar(self.AnalyzStats.items()):
            update_combinations = []
  
            for combo in reversed(repo_item.LangCombo):
                combo = ' '.join(combo)            
                if (combo in self.ComboStats.keys()):
                    update_combinations.append(combo)
                    break
            repo_item.LangCombo = update_combinations
            AnlyStats[index] = repo_item
        
        self.AnalyzStats = AnlyStats

    def GetTopcombos(self, top_num=1000):
        combination_stats = {}
        combination_sort = self.SortComboByCount()
        combination_id = 0
        for lang in combination_sort.keys():
            combo_stat = self.ComboStats[lang]
            combo_stat.combo_id = combination_id
            
            if (combination_id <= top_num):     
                combination_stats[lang] = combo_stat
                self.AllLanguageComboNum = self.AllLanguageComboNum + combo_stat.count

            self.AllComboStats[lang] = combo_stat
            combination_id = combination_id + 1

        return combination_stats
    
    def SortComboByCount(self):
        #collect items whose count > 1
        combinations = {}
        for combo, stat in self.ComboStats.items():
            combinations[combo] = stat.count
        return Util.dictsort_value (combinations, True)
    
    def SaveData (self, FileName=None):
        if (len(self.AnalyzStats) == 0):
            if FileName != None:
                Empty = "touch " + FileName
                os.system (Empty)
            return

        key0 = list(self.AnalyzStats.keys())[0]
        super(RepoAnalyzer, self).SaveData2 ("/StatData/" + FileName, self.AnalyzStats[key0].__dict__, self.AnalyzStats)
        
        key0 = list(self.AllComboStats.keys())[0]
        super(RepoAnalyzer, self).SaveData2 ("/StatData/LangCombo_Stats.csv", self.AllComboStats[key0].__dict__, self.AllComboStats)
                     
    def Obj2List(self, value):
        return super(RepoAnalyzer, self).Obj2List (value)
            
    def Obj2Dict(self, value):
        return super(RepoAnalyzer, self).Obj2Dict (value)
            
    def GetHeader(self, data):
        return super(RepoAnalyzer, self).GetHeader (data)
    
