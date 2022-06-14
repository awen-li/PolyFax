
import os
import sys, getopt
from lib.LangCrawler import LangCrawler

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
   
def main(argv):
    Function = 'crawler'
    IsDaemon = False
    RepoDir  = ""

    try:
        opts, args = getopt.getopt(argv,"df:r:",["Function="])
    except getopt.GetoptError:
        print ("python mls.py -f <Function>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-f", "--Function"):
            Function = arg;
        elif opt in ("-d", "--daemon"):
            IsDaemon = True;

    if IsDaemon == True:
        Daemonize ()
    
    if (Function == "lang"):
        Cl = LangCrawler(UserName="", Token="", LangList=[])
        Cl.GrabProject ()
    if (Function == "domain"):
        Cl = LangCrawler(UserName="", Token="", LangList=[])
        Cl.GrabProject ()
    else:
        pass

if __name__ == "__main__":
    main(sys.argv[1:])
    
