
import os


class Config ():

    START_YEAR   = 2013
    END_YEAR     = 2022
    PAGE_COUNT   = 10
    PER_PAGE     = 100


    OriginCollect= "OriginData"
    OriginStat   = "StatData"
    Evoluation   = "Evoluation"

    BaseDir      = os.getcwd() + "/Data"
    CollectDir   = OriginCollect
    StatisticDir = OriginStat

    Version      = "None"

    CMMT_DIR     = BaseDir + "/CmmtSet/"
    if not os.path.exists (CMMT_DIR):
        os.makedirs (CMMT_DIR)
        
    CMMT_STAT_DIR= BaseDir + "/" + OriginStat + "/CmmtSet/"
    if not os.path.exists (CMMT_STAT_DIR):
        os.makedirs (CMMT_STAT_DIR)

    KEYWORD_FILE = BaseDir + "/Config/keywords.txt"

    MAX_CMMT_NUM = 20 * 1024

    TagSet       = BaseDir + "/TagSet"
    if not os.path.exists (TagSet):
        os.makedirs (TagSet)

    IssueDir     = BaseDir + "/Issues"
    if not os.path.exists (IssueDir):
        os.makedirs (IssueDir)

    CFG_Type = ['int', 'str', 'list']

    def __init__(self, CfgFile='config.ini'):
        self.CfgFile = CfgFile

        self.CFG = {}
        self.CFG['UserName']   = 'str'
        self.CFG['Token']      = 'str'
        self.CFG['TaskNum']    = 'int'
        self.CFG['Languages']  = 'list'
        self.CFG['Domains']    = 'list'
        self.CFG['MaxGrabNum'] = 'int'

    def Get (self, Key):
        return self.CFG[Key]

    def LoadCfg (self):
        CfgPath = Config.BaseDir + "/Config/" + self.CfgFile
        print (CfgPath)
        with open (CfgPath, "r") as CF:
            AllLines = CF.readlines ()
            for Line in AllLines:
                Line = Line.replace ('\n', '')
                if Line.find (':') == -1:
                    continue      
                
                Key, Content = Line.split (':')

                Type = self.CFG.get (Key)
                if Type == 'int':
                    self.CFG[Key] = int (Content)               
                elif Type == 'str':
                    self.CFG[Key] = Content
                elif Type == 'list':
                    CList = list (Content.split (' '))
                    self.CFG[Key] = [item for item in CList if item != '']
                else:
                    continue
                #print ('Key %s   ----->  Content %s' %(Key, str(self.CFG[Key])))

    @staticmethod
    def IssueFile (id):
        return (Config.IssueDir + "/" + str(id) + ".csv")
    
    @staticmethod
    def CmmtFile (id):
        return (Config.CMMT_DIR + str(id) + ".csv")

    @staticmethod
    def CmmtStatFile (id):
        return (Config.CMMT_STAT_DIR + str(id))

    @staticmethod
    def IsExist (file):
        isExists = os.path.exists(file)
        if (not isExists):
            return False
        
        fsize = os.path.getsize(file)/1024
        if (fsize == 0):
            return False
        return True      

    @staticmethod
    def MakeDir (path):
        path=path.strip()
        path=path.rstrip("\\")
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path)

    @staticmethod
    def SetTag (tag):
        NewDir = Config.TagSet
        if not os.path.exists (NewDir):
            os.mkdir (NewDir)
        file = open(NewDir + "/" + tag, 'w')
        file.close()
        
    @staticmethod
    def AccessTag (tag):
        tagPath = Config.TagSet + "/" + tag
        isExists = os.path.exists(tagPath)
        if not isExists:
            return False
        return True
 
