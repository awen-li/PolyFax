
import os
import sys, getopt
from lib.Config import Config
from lib.LangCrawler import LangCrawler
from lib.DomainCrawler import DomainCrawler
from lib.InstanceDist import CmmtCrawlerDist, CmmtLogAnalyzerDist, LangApiAnalyzerDist
from lib.RepoAnalyzer import RepoAnalyzer
from lib.NbrAnalyzer import NbrAnalyzer
from lib.NbrAnalyzerLic import NbrAnalyzerLic
from lib.NbrAnalyzerSL import NbrAnalyzerSL


CFG = Config ()
CFG.LoadCfg ()

#LangCrawler().Transer ()


def Help ():
    print ("====================================================")
    print ("====           PolyFax Help Information         ====")
    print ("====================================================")
    print ("= python mls.py -a crawler -t <lang/domain> -n <task num>")
    print ("= python mls.py -a crawler-cmmt -n <task num>")
    print ("= python mls.py -a lic -n <task num>")
    print ("= python mls.py -a vcc -n <task num>")
    print ("= python mls.py -a all -n <task num>")
    print ("====================================================\r\n")


def GetCrawler (Type):
    Cl = None
    
    if (Type == "lang"):
        Cl = LangCrawler()
    elif (Type  == "domain"):
        Cl = DomainCrawler()
    else:
        Help ()
        exit (0)
    return Cl
   
def main(argv):
    IsDaemon = False
    Type     = 'lang'
    Act      = 'crawler'
    TaskNum  = CFG.Get('TaskNum')
    
    RepoDir  = ""

    try:
        opts, args = getopt.getopt(argv,"ht:a:n:",["Type="])
    except getopt.GetoptError:
        Help ()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-t", "--type"):
            Type = arg;
        if opt in ("-a", "--action"):
            Act = arg;
        elif opt in ("-n", "--task number"):
            TaskNum = int (arg);
        elif opt in ("-h", "--help"):
            Help ()
            sys.exit(2)

    if Act == 'all': 
        # 1.  grab the project 
        Cl = GetCrawler (Type)
        Cl.Grab ()

        # 2. grab commits
        CCTDist = CmmtCrawlerDist (TaskNum=TaskNum, RepoList=Cl.RepoList)
        CCTDist.Distributer ()

        # 3. analyze commits
        CLADist = CmmtLogAnalyzerDist (TaskNum=TaskNum, RepoList=Cl.RepoList)
        CLADist.Distributer ()

        # 4. analyze the APIs
        LAADist = LangApiAnalyzerDist (TaskNum=TaskNum, RepoList=Cl.RepoList)
        LAADist.Distributer ()

        # 5. analyze repos
        Ra = RepoAnalyzer ()
        Ra.StartRun ()

        # 6. nbr analysise
        Nbra = NbrAnalyzer ()
        Nbra.StartRun ()

        NbraLic = NbrAnalyzerLic ()
        NbraLic.StartRun ()
        
    elif Act == 'crawler':
        Cl = GetCrawler (Type)
        Cl.Grab ()

        CCTDist = CmmtCrawlerDist (TaskNum=TaskNum, RepoList=Cl.RepoList)
        CCTDist.Distributer ()

        Ra = RepoAnalyzer ()
        Ra.StartRun ()
    elif Act == 'crawler-cmmt':
        CCTDist = CmmtCrawlerDist (TaskNum=TaskNum)
        CCTDist.Distributer ()
    elif Act == 'lic':
        LAADist = LangApiAnalyzerDist (TaskNum=TaskNum)
        LAADist.Distributer ()
    elif Act == 'vcc': 
        CLADist = CmmtLogAnalyzerDist (TaskNum=TaskNum)
        CLADist.Distributer ()
    elif Act == 'nbr-combo':
        Nbra = NbrAnalyzer ()
        Nbra.StartRun ()
    elif Act == 'nbr-lic':
        NbraLic = NbrAnalyzerLic ()
        NbraLic.StartRun ()
    elif Act == 'nbr-single':
        NbraSL = NbrAnalyzerSL ()
        NbraSL.StartRun ()
    else:
        Help()

if __name__ == "__main__":
    main(sys.argv[1:])
    
