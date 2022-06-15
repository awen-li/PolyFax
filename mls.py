
import os
import sys, getopt
from lib.LangCrawler import LangCrawler
from lib.LangApiAnalyzer import LangApiAnalyzer

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
    print ("= python mls.py -a api")
    print ("= python mls.py -a cmmt")
    print ("= python mls.py -a all")
    print ("====================================================\r\n")


def GetCrawler (Type):
    Cl = None
    if (Type == "lang"):
        Cl = LangCrawler(UserName="Daybreak2019", Token="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", LangList=[], MaxGrabNum=10)
    elif (Type  == "domain"):
        Cl = LangCrawler(UserName="", Token="", LangList=[])
    else:
        Help ()
        exit (0)
    return Cl
   
def main(argv):
    IsDaemon = False
    Type = 'lang'
    Act  = 'crawler'
    
    RepoDir  = ""

    try:
        opts, args = getopt.getopt(argv,"dt:a:",["Type="])
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

    if IsDaemon == True:
        Daemonize ()

    if Act == 'all':
        # 1.  grap the project 
        Cl = GetCrawler (Type)
        Cl.Grab ()

        # 2. analyze commits

        # 3. analyze the APIs
        Analyzer = LangApiAnalyzer ()
        Analyzer.AnalyzeData (Analyzer.RepoList)
    elif Act == 'crawler':
        Cl = GetCrawler (Type)
        Cl.Grab ()
    elif Act == 'api':
        Analyzer = LangApiAnalyzer ()
        Analyzer.AnalyzeData (Analyzer.RepoList)
    elif Act == 'cmmt':
        Help ()
    else:
        Help()

if __name__ == "__main__":
    main(sys.argv[1:])
    
