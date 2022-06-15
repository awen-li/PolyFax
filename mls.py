
import os
import sys, getopt
from lib.LangCrawler import LangCrawler
from lib.DomainCrawler import DomainCrawler


def Daemonize(pid_file=None):
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
 
    with open('/dev/null') as read_null, open('/dev/null', 'w') as write_null:
        os.dup2(read_null.fileno(), sys.stdin.fileno())
        os.dup2(write_null.fileno(), sys.stdout.fileno())
        os.dup2(write_null.fileno(), sys.stderr.fileno())
 
    if pid_file:
        with open(pid_file, 'w+') as f:
            f.write(str(os.getpid()))
        atexit.register(os.remove, pid_file)


def Help ():
    print ("====================================================")
    print ("====           PolyFax Help Information         ====")
    print ("====================================================")
    print ("= python mls.py -a crawler -t <lang/domain>")
    print ("= python mls.py -a crawler-cmmt -s <start-no> -e <end-no>")
    print ("= python mls.py -a api")
    print ("= python mls.py -a cmmt")
    print ("= python mls.py -a all")
    print ("====================================================\r\n")


def GetCrawler (Type):
    Cl = None
    if (Type == "lang"):
        Cl = LangCrawler(UserName="Daybreak2019", Token="", LangList=[], MaxGrabNum=10)
    elif (Type  == "domain"):
        Cl = DomainCrawler(UserName="Daybreak2019", Token="", Domains=['web', 'hardware'], MaxGrabNum=10)
    else:
        Help ()
        exit (0)
    return Cl
   
def main(argv):
    IsDaemon = False
    Type = 'lang'
    Act  = 'crawler'
    StartNo = 0
    EndNo   = 65535
    
    RepoDir  = ""

    try:
        opts, args = getopt.getopt(argv,"hdt:a:s:e:",["Type="])
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
        elif opt in ("-s", "--start number"):
            StartNo = int (arg);
        elif opt in ("-e", "--end number"):
            EndNo = int (arg);
        elif opt in ("-h", "--help"):
            Help ()
            sys.exit(2)

    if IsDaemon == True:
        Daemonize ()

    from lib.CmmtCrawler import CmmtCrawler
    from lib.LangApiAnalyzer import LangApiAnalyzer
    from lib.CmmtLogAnalyzer import CmmtLogAnalyzer

    if Act == 'all':
        # 1.  grab the project 
        Cl = GetCrawler (Type)
        Cl.Grab ()

        # 2. grab commits
        CmmtGraber= CmmtCrawler (RepoList=Cl.RepoList)
        CmmtGraber.Clone ()

        # 3. analyze commits
        Analyzer = CmmtLogAnalyzer ()
        Analyzer.AnalyzeData (Analyzer.RepoList)

        # 4. analyze the APIs
        Analyzer = LangApiAnalyzer ()
        Analyzer.AnalyzeData (Analyzer.RepoList)
    elif Act == 'crawler':
        Cl = GetCrawler (Type)
        Cl.Grab ()

        CmmtGraber= CmmtCrawler (RepoList=Cl.RepoList)
        CmmtGraber.Clone ()
    elif Act == 'crawler-cmmt':
        CmmtGraber= CmmtCrawler (startNo=StartNo, endNo=EndNo)
        CmmtGraber.Clone ()
    elif Act == 'api':
        Analyzer = LangApiAnalyzer ()
        Analyzer.AnalyzeData (Analyzer.RepoList)
    elif Act == 'cmmt': 
        Analyzer = CmmtLogAnalyzer ()
        Analyzer.AnalyzeData (Analyzer.RepoList)
    else:
        Help()

if __name__ == "__main__":
    main(sys.argv[1:])
    
