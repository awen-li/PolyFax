
import os


class Config():

    START_YEAR   = 2013
    END_YEAR     = 2022
    PAGE_COUNT   = 10
    PER_PAGE     = 100
    RELEASE      = "release"

    TOP_LANGUAGES = ["c","c++","java","c#","javascript","python","php","go","ruby", "dart", "matlab",
                     "objective-c","assembly","scala", "perl","r","perl", "swift", "rust", "kotlin"]

    VERSION_REPO_NUM = 100

    OriginCollect= "OriginData"
    OriginStat   = "StatData"
    Evoluation   = "Evoluation"

    BaseDir      = os.getcwd() + "/Data"
    CollectDir   = OriginCollect
    StatisticDir = OriginStat

    Version      = "None"

    CMMT_DIR     = BaseDir + "/CmmtSet/"
    if not os.path.exists (CMMT_DIR):
        os.mkdir (CMMT_DIR)
        
    CMMT_STAT_DIR= BaseDir + "/" + OriginStat + "/CmmtSet/"
    if not os.path.exists (CMMT_STAT_DIR):
        os.mkdir (CMMT_STAT_DIR)

    KEYWORD_FILE = BaseDir + "/" + OriginCollect + "/keywords.txt"

    MAX_CMMT_NUM = 20 * 1024

    TagSet       = BaseDir + "/TagSet"
    if not os.path.exists (TagSet):
        os.mkdir (TagSet)

    IssueDir     = BaseDir + "/Issues"
    if not os.path.exists (IssueDir):
        os.mkdir (IssueDir)

    @staticmethod
    def IssueFile (id):
        return (Config.IssueDir + "/" + str(id) + ".csv")
    
    @staticmethod
    def CmmtFile (id):
        return (Config.CMMT_DIR + str(id) + ".csv")

    @staticmethod
    def CmmtStatFile (id):
        return (System.CMMT_STAT_DIR + str(id))

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
 
