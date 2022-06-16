
import os
import sys, getopt
from lib.LangCrawler import LangCrawler
from lib.DomainCrawler import DomainCrawler
from lib.InstanceDist import CmmtCrawlerDist, CmmtLogAnalyzerDist, LangApiAnalyzerDist


def Daemonize():
    pid = os.fork()
    if pid:
        sys.exit(0)
 
    #os.chdir('/')
    os.umask(0)
    os.setsid()

    _pid = os.fork()
    if _pid:
        sys.exit(0)
 
    sys.stdout.flush()
    sys.stderr.flush()
 
    #with open('/dev/null') as read_null, open('/dev/null', 'w') as write_null:
    #    os.dup2(read_null.fileno(), sys.stdin.fileno())
    #    os.dup2(write_null.fileno(), sys.stdout.fileno())
    #    os.dup2(write_null.fileno(), sys.stderr.fileno())


def Help ():
    print ("====================================================")
    print ("====           PolyFax Help Information         ====")
    print ("====================================================")
    print ("= python mls.py -a crawler -t <lang/domain> -n <task num>")
    print ("= python mls.py -a crawler-cmmt -n <task num>")
    print ("= python mls.py -a api -n <task num>")
    print ("= python mls.py -a cmmt -n <task num>")
    print ("= python mls.py -a all -n <task num>")
    print ("====================================================\r\n")


def GetCrawler (Type):
    Cl = None
    if (Type == "lang"):
        Cl = LangCrawler(UserName="xxx", Token="xxx", LangList=[])
    elif (Type  == "domain"):
        Cl = DomainCrawler(UserName="xxx", Token="xxx", Domains=['web', 'hardware'])
    else:
        Help ()
        exit (0)
    return Cl
   
def main(argv):
    IsDaemon = False
    Type = 'lang'
    Act  = 'crawler'
    TaskNum = 4
    
    RepoDir  = ""

    try:
        opts, args = getopt.getopt(argv,"hdt:a:n:",["Type="])
    except getopt.GetoptError:
        Help ()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-t", "--type"):
            Type = arg;
        if opt in ("-a", "--action"):
            Act = arg;
        elif opt in ("-d", "--daemon"):
            IsDaemon = True;
        elif opt in ("-n", "--task number"):
            TaskNum = int (arg);
        elif opt in ("-h", "--help"):
            Help ()
            sys.exit(2)

    if IsDaemon == True:
        Daemonize ()
            
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
    elif Act == 'crawler':
        Cl = GetCrawler (Type)
        Cl.Grab ()

        CCTDist = CmmtCrawlerDist (TaskNum=TaskNum, RepoList=Cl.RepoList)
        CCTDist.Distributer ()
    elif Act == 'crawler-cmmt':
        CCTDist = CmmtCrawlerDist (TaskNum=TaskNum)
        CCTDist.Distributer ()
    elif Act == 'api':
        LAADist = LangApiAnalyzerDist (TaskNum=TaskNum)
        LAADist.Distributer ()
    elif Act == 'cmmt': 
        CLADist = CmmtLogAnalyzerDist (TaskNum=TaskNum)
        CLADist.Distributer ()
    else:
        Help()

if __name__ == "__main__":
    main(sys.argv[1:])
    
