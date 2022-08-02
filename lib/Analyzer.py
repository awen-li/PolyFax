

import abc
import csv 
import sys
import pandas as pd
from patsy import dmatrices
import statsmodels.api as sm
import statsmodels.formula.api as smf
from progressbar import ProgressBar
from lib.Config import Config
from lib.Util import Util
from lib.Repository import Repository


csv.field_size_limit(sys.maxsize)


class Analyzer(metaclass=abc.ABCMeta):

    Language_Combination_Limit = 20

    def __init__(self, StartNo=0, EndNo=65535, InputFile='RepositoryList.csv', OutputFile="Analyzer.csv"):
        self.FileName  = OutputFile
        self.InputFile = InputFile
        
        self.StartNo  = StartNo
        self.EndNo    = EndNo
        self.FilePath = Config.BaseDir
        self.AnalyzStats = {}

        self.RepoList = []
        self.LoadRepoList ()
        
    @abc.abstractmethod
    def SaveData (self, data, FileName=None):
        if (FileName == None):
            FileName = self.FileName
        self.__WriteCsv (data, FileName)

    def SaveData2 (self, FileName, Header, Dict):
        FilePath = self.FilePath + FileName   
        with open(FilePath, 'w') as CsvFile:
            W = csv.writer(CsvFile)            
            W.writerow(Header)
            for Key, Value in Dict.items():
                Row = self.Obj2List (Value)
                W.writerow(Row)

    def __WriteCsv (self, Data, FileName):
        CurFile = self.FilePath + FileName
        if CurFile.find ('.csv') == -1:
            CurFile += '.csv'       
        with open(CurFile, 'w') as CsvFile:
            W = csv.writer(CsvFile)
            W.writerow(self.__GetHeader (Data))
            for Key, Value in Data.items():
                Row = self.Obj2List (Value)
                writer.writerow(Row)

    def LoadRepoList (self):
        FilePath = self.FilePath + '/' + self.InputFile
        if Config.IsExist (FilePath) == False:
            return
        
        df = pd.read_csv(FilePath)
        for index, row in df.iterrows():
            RepoData = Repository (row['Id'], row['Star'], row['Langs'], row['ApiUrl'], row['CloneUrl'], row['Topics'], 
                                   row['Descripe'], row['Created'], row['Pushed'])
            RepoData.SetLangDict(row['LangsDict'])
            RepoData.SetName(row['Name'])
            RepoData.SetMainLang(row['MainLang'])
            RepoData.SetSize(row['Size'])
            RepoData.SetLangCombo(row['LangCombo'])
            RepoData.SetLangsDist(row['LangsDist'])
            
            self.RepoList.append (RepoData)

    def NbrDump (self, r_val, nbrSum):
        import sys
        file = './Data/StatData/' + self.__class__.__name__ + '_' + r_val + '.nbr'
        with open(file, 'w') as f:
            original_stdout = sys.stdout
            sys.stdout = f
            print(nbrSum)
            sys.stdout = original_stdout
        return file

    def NbrShow (self, nbrData):
        for key, value in nbrData.items ():
            tag = ''
            if value < 0.001:
                tag = '***'
            elif value < 0.01:
                tag = '**'
            elif value < 0.05:
                tag = '*'

            print ("%-32s - %-8s" %(key, tag))
    
    def NbrAnalyze (self, r_val, nbrSum):
        nbrData = {}
        file = self.NbrDump (r_val, nbrSum)
        with open(file, 'r') as nbrF:
            allLines = nbrF.readlines ()
            startFlag = False
            for line in allLines:
                if line.find ('Intercept') != -1:
                    startFlag = True
                 
                if startFlag == False or line.find('==') != -1:
                    continue

                line = line.replace ('\n', '')
                items = line.split ('   ')
                itemIndex = 0
                name = ''
                p_value = 0.0
                for item in items:
                    if item == '':
                        continue
                    
                    if itemIndex == 0:
                        name = item
                        itemIndex += 1
                        continue
                    elif itemIndex == 4:
                        p_value = float (item)
                        break
                    else:
                        itemIndex += 1
                nbrData[name] = p_value               

        self.NbrShow (nbrData)

                
    def NbrCompute (self, cdf, r_val):
        df_train = cdf

        if df_train[r_val].sum () == 0:
            print ("@@@@ No enough data for NBR analysis....\r\n")
            return

        expr = self.GetNbrExpr (r_val)
              
        #Set up the X and y matrices for the training and testing data sets
        y_train, X_train = dmatrices(expr, df_train, return_type='dataframe')
        
        #Using the statsmodels GLM class, train the Poisson regression model on the training data set
        poisson_training_results = sm.GLM(y_train, X_train, family=sm.families.Poisson()).fit()
        
        #Add the λ vector as a new column called 'BB_LAMBDA' to the Data Frame of the training data set
        df_train['BB_LAMBDA'] = poisson_training_results.mu
        
        #add a derived column called 'AUX_OLS_DEP' to the pandas Data Frame. This new column will store the values of the dependent variable of the OLS regression
        df_train['AUX_OLS_DEP'] = df_train.apply(lambda x: ((x[r_val] - x['BB_LAMBDA'])**2 - x[r_val]) / x['BB_LAMBDA'], axis=1)
        
        #use patsy to form the model specification for the OLSR
        ols_expr = """AUX_OLS_DEP ~ BB_LAMBDA - 1"""
        
        #Configure and fit the OLSR model
        aux_olsr_results = smf.ols(ols_expr, df_train).fit()
        
        #train the NB2 model on the training data set
        nb2_training_results = sm.GLM(y_train, X_train,family=sm.families.NegativeBinomial(alpha=aux_olsr_results.params[0])).fit()
        
        #print the training summary
        nbrSum = nb2_training_results.summary()
        self.NbrAnalyze (r_val, nbrSum)

    def GetNbrExpr (self, Value):
        pass
        
    @abc.abstractmethod
    def Obj2List (self, Value):
        return list(Value.__dict__.values())

    @abc.abstractmethod
    def Obj2Dict (self, Value):
        return Value.__dict__

    @abc.abstractmethod
    def GetHeader (self, Data):
        Headers = list(list(Data.values())[0].__dict__.keys())
        return [header.replace(" ", "_") for header in Headers]

    def AnalyzeData (self, RepoList):
        pbar = ProgressBar()
        for Repo in pbar(RepoList):
            self.UpdateAnalysis (Repo)
        self.UpdateFinal ()

    @abc.abstractmethod
    def UpdateFinal (self):
        print("Abstract Method that is implemented by inheriting classes")

    @abc.abstractmethod
    def UpdateAnalysis(self, CurRepo):
        print("Abstract Method that is implemented by inheriting classes")

    def StartRun (self):
        self.AnalyzeData (self.RepoList)
        

   