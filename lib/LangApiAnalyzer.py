##### LangFfiSniffer.py #####
import os
import re
import csv
from lib.Process_Data import Process_Data
from lib.Collect_Research_Data import Collect_Research_Data

LANG_API_FFI = "FFI"
LANG_API_IRI = "IMI"  #Indirect remote-invocation
LANG_API_ID  = "EBD"  #inter-dependence
LANG_API_HI  = "HIT"  #Hidden interaction
FfiSignature = "@FfiSignature"

class State ():
    def __init__(self, id, signature, next=None):
        self.id = id
        self.signature = signature
        self.next = []
        if next != None:
            self.next.append(next)

        global FfiSignature
        FfiSignature += signature + "@FfiSignature@"

    def AddNext (self, next):
        self.next.append (next)

    def Match (self, String):
        if len (self.signature) == 0:
            return True
            
        #print ("\tMatchState=>", self.signature, " -> ", String, ":", len (String))
        if re.search(self.signature, String) != None:
            return True
        else:
            return False
        

class ApiClassifier ():
    def __init__(self, name, clstype, fileType):
        self.name     = name
        self.clstype  = clstype
        self.filetype = fileType.split()
        self.States = []

    def AddState (self, state):
        self.States.append (state)

    def MatchString (self, String):
        StateStack = self.States
        for state in StateStack:
            isMatch = state.Match(String)
            #print ("\t Match: ", isMatch, " String: ", String)
            if isMatch == False:
                continue

            if len (state.next) == 0:
                return True
            for next in state.next:
                StateStack.append (next)
        return False

    def Match (self, File):
        if not os.path.exists (File):
            return False
        
        Ext = os.path.splitext(File)[-1].lower()
        if "*" not in self.filetype and Ext not in self.filetype:
            return False

        #print ("Entry classifier: ", self.name)
        StateStack = self.States
        if len (StateStack) == 0:
            return False
        
        with open (File, "r", encoding="utf8", errors="ignore") as sf:
            for line in sf:
                if len (line) < 4:
                    continue
                for state in StateStack:
                    isMatch = state.Match(line)
                    if isMatch == False:
                        continue

                    #print ("\t Match: ", isMatch, " Line: ", line)
                    if len (state.next) == 0:
                        return True
                    for next in state.next:
                        StateStack.append (next)
        return False

class LangApiSniffer(Collect_Research_Data):
    def __init__(self, StartNo=0, EndNo=65535, file_name='ApiSniffer'):
        super(LangApiSniffer, self).__init__(file_name=file_name)
        self.StartNo = StartNo
        self.EndNo   = EndNo
        self.Index   = 0
        
        self.FFIClfList = []
        self.IRIClfList = []
        self.IDClfList  = []
        self.HIClfList  = []

        self.Langs = {}
        
        self.TopLanguages = {"c":".c", "c++":".cpp .cc", "java":".java", "javascript":".js", "typescript":".ts", 
                             "python":".py", "html":".html", "php":".php", "go":".go", "ruby":".rb", "objective-c":".m .mm", 
                             "css":".css", "shell":".sh .zsh .bsh"}

        # Init FFI classifier
        self.InitFfiClass ()

        # Init IRI classifier
        self.InitIriClass ()

        # Init HD classifier
        self.InitIDClass ()

        # Init HD classifier
        self.InitHIClass ()

        # Test
        self.TestClf ()

        # Default file 
        Header = ['id', 'languages', 'classifier', 'clfType', 'fileType']
        SfFile = self.file_path + "ApiSniffer" + '.csv'
        with open(SfFile, 'w', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            writer.writerow(Header)      

    def AddClf (self, Classifier):
        self.FFIClfList.append (Classifier)

    def _update(self):
        self.save_data ()

    def _update_statistics(self, repo_item):
        #print (self.Index, " -> [", self.StartNo, ", ", self.EndNo, "]")
        if self.Index < self.StartNo or self.Index > self.EndNo:
            self.Index += 1
            return
        
        ReppId  = repo_item.id
        RepoDir = "./Data/Repository/" + str(ReppId)
        if not os.path.exists (RepoDir):
            self.Index += 1
            return
        
        TopLangs = self.TopLanguages.keys()
        Langs = [lang for lang in repo_item.all_languages if lang in TopLangs]

        #print ("Scan ", RepoDir, Langs)
        self.Sniffer(ReppId, Langs, RepoDir)
        self.Index += 1

    def SnifferByFFI (self, Langs, File):
        for Clf in self.FFIClfList:
            #print ("\t->>>Scan by ", Clf.name)
            IsMatch = Clf.Match (File)
            if IsMatch == True:
                return Clf
        #C-C++ classifier
        if "c" in Langs and "c++" in Langs:
            return self.FFIClfList[0]
        return None

    def SnifferByIri (self, Langs, File):
        Fext = os.path.splitext(File)[-1].lower()
        
        IsFiltered = True
        for lang in Langs:
            Ext = self.TopLanguages [lang].split ()
            if Fext in Ext:
                IsFiltered = False
                break
        if IsFiltered == True:
            return None
        
        for Clf in self.IRIClfList:
            #print ("\t->>>Scan by ", Clf.name)
            IsMatch = Clf.Match (File)
            if IsMatch == True:
                return Clf
        return None

    def SnifferByID (self, Langs, File):
        LangNum = 0
        Languages = ["javascript", "typescript", "css", "html"]
        for lang in Langs:
            if lang in Languages:
                LangNum += 1
        if (LangNum < 2):
            return None
        
        for Clf in self.IDClfList:
            IsMatch = Clf.Match (File)
            if IsMatch == True:
                return Clf
        return None

    def SnifferByHI (self, Langs, File):
        for Clf in self.HIClfList:
            IsMatch = Clf.Match (File)
            if IsMatch == True:
                return Clf
        return None

    def AddScanResult (self, ClfList, Clf):
        for C in ClfList:
            if C.name == Clf.name:
                return
        ClfList.append (Clf)

    def Sniffer (self, ReppId, Langs, Dir):
        if len (Langs) <= 1:
            return None

        ClfList = []
        self.Langs [ReppId] = Langs
        
        # 1. FFI Scan      
        RepoDirs = os.walk(Dir)
        for Path, Dirs, Fs in RepoDirs:
            for f in Fs:
                File = os.path.join(Path, f)
                Clf = self.SnifferByFFI (Langs, File)
                if Clf != None:
                    #print ("Match:", Langs[0:3], "[", ReppId, "] -> ", Clf.name, " = ", Clf.clstype)
                    self.AddScanResult (ClfList, Clf)

        if (len (ClfList) >= len(Langs)-1):
            self.research_stats [ReppId] = ClfList
            return

        # 2. IRI Scan      
        RepoDirs = os.walk(Dir)
        for Path, Dirs, Fs in RepoDirs:
            for f in Fs:
                File = os.path.join(Path, f)
                Clf = self.SnifferByIri (Langs, File)
                if Clf != None:
                    self.AddScanResult (ClfList, Clf)
        
        if (len (ClfList) >= 3 or len (ClfList) >= len(Langs)-1):
            self.research_stats [ReppId] = ClfList
            return

        #3. ID Scan
        RepoDirs = os.walk(Dir)
        for Path, Dirs, Fs in RepoDirs:
            for f in Fs:
                File = os.path.join(Path, f)
                Clf = self.SnifferByID (Langs, File)
                if Clf != None:
                    self.AddScanResult (ClfList, Clf)
        
        if (len (ClfList) != 0):
            self.research_stats [ReppId] = ClfList
            return
        
        # 4. HI Scan      
        RepoDirs = os.walk(Dir)
        for Path, Dirs, Fs in RepoDirs:
            for f in Fs:
                File = os.path.join(Path, f)
                Clf = self.SnifferByHI (Langs, File)
                if Clf != None:
                    self.AddScanResult (ClfList, Clf)

        self.research_stats [ReppId] = ClfList
        return None

    def FormatTypes (self, TypeList):
        if len (TypeList) == 0:
            return LANG_API_HI
        
        Types = ""
        TypeOrder = [LANG_API_FFI, LANG_API_IRI, LANG_API_ID, LANG_API_HI]
        for type in TypeOrder:
            if type not in TypeList:
                continue
            if Types == "":
                Types = type
            else:
                Types += "_" + type
        return Types
    
    def save_data(self, file_name=None):
        if (len(self.research_stats) == 0):
            return
        #Header = ['id', ''langs', 'classifier', 'clfType', 'fileType']
        SfFile = self.file_path + self.file_name + '.csv'
        with open(SfFile, 'w', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            #writer.writerow(Header)  
            for Id, ClfList in self.research_stats.items():
                Names = []
                Types = []
                FileTypes = []
                for clf in ClfList:
                    print ("Clf: ", clf.name)
                    Names.append (clf.name)
                    Types.append (clf.clstype)
                    FileTypes += clf.filetype

                Names = "_".join(list(set (Names)))
                Types = self.FormatTypes(list(set (Types)))
                row = [Id, self.Langs [Id], Names, Types, FileTypes]
                print (row)
                writer.writerow(row)
        self.research_stats = {}
             
    def _object_to_list(self, value):
        return super(LangApiSniffer, self)._object_to_list(value)
    
    def _object_to_dict(self, value):
        return super(LangApiSniffer, self)._object_to_dict(value)
    
    def _get_header(self, data):
        return super(LangApiSniffer, self)._get_header(data)

    def TestClf (self):
        print ("Start test FFI classifiers:")
        for Clf in self.FFIClfList:
            IsMatch = Clf.MatchString (FfiSignature)
            if IsMatch == False:
                print ("[Fail]: ", Clf.name, "->", Clf.clstype)
            else:
                print ("[Pass]: ", Clf.name, "->", Clf.clstype)
                
    def InitIriClass (self):
        ############################################################
        # Class: Java*
        ############################################################
        Class = ApiClassifier ("Java*", LANG_API_IRI, ".java")
        S0 = State (0, "import java.net.*")
        S1 = State (1, "ServerSocket|Socket")
        S0.AddNext(S1)
        Class.AddState(S0)
        S2 = State (2, "import org.freedesktop.DBus|import io.grpc.inprocess")
        Class.AddState(S2)
        self.IRIClfList.append (Class)

        ############################################################
        # Class: Python*
        ############################################################
        Class = ApiClassifier ("Python*", LANG_API_IRI, ".py")
        S0 = State (0, "import.*dbus|from dbus import|import subprocess")
        S1 = State (1, "SessionBus|Interface|subprocess.run")
        S0.AddNext(S1)
        Class.AddState(S0)
        S2 = State (2, "import.*socket|from socket import")
        S3 = State (3, "AF_INET|SOCK_STREAM|SOCK_DGRAM")
        S2.AddNext(S3)
        Class.AddState(S2)
        S4 = State (4, "os.system.*\)")
        Class.AddState(S4)
        self.IRIClfList.append (Class)


        ############################################################
        # Class: JavaScript*
        ############################################################
        Class = ApiClassifier ("JavaScript*", LANG_API_IRI, ".ts .js .html")
        S0 = State (0, "interface.*WebSocket|WebSocket")
        Class.AddState(S0)
        S1 = State (1, "require\('child_process'\)")
        S2 = State (2, "exec\(.*\)")
        S1.AddNext(S2)
        Class.AddState(S1)
        self.IRIClfList.append (Class)


        ############################################################
        # Class: Ruby*
        ############################################################
        Class = ApiClassifier ("Ruby*", LANG_API_IRI, ".rb")
        S0 = State (0, "require.*socket")
        S1 = State (1, "Socket.new|TCPSocket|UDPSocket|TCPServer|UDPServer")
        S0.AddNext(S1)
        Class.AddState(S0)
        S2 = State (2, "system\(.*\)|exec\(.*\)")
        Class.AddState(S2)
        self.IRIClfList.append (Class)

        ############################################################
        # Class: PHP*
        ############################################################
        Class = ApiClassifier ("PHP*", LANG_API_IRI, ".php")
        S0 = State (0, "socket_create|socket_connect|socket_write|namespace Grpc")
        Class.AddState(S0)
        self.IRIClfList.append (Class)

        ############################################################
        # Class: Objective-C*
        ############################################################
        Class = ApiClassifier ("Objective-C*", LANG_API_IRI, ".mm")
        S0 = State (0, "#import.*GRPCClient")
        Class.AddState(S0)
        self.IRIClfList.append (Class)

        ############################################################
        # Class: Go*
        ############################################################
        Class = ApiClassifier ("Go*", LANG_API_IRI, ".go")
        S0 = State (0, "org.freedesktop.DBus")
        Class.AddState(S0)
        S1 = State (1, "import .*net|import .*fmt|import .*grpc")
        Class.AddState(S1)
        self.IRIClfList.append (Class)

        ############################################################
        # Class: Shell*
        ############################################################
        Class = ApiClassifier ("Shell*", LANG_API_IRI, ".sh .bsh .zsh")
        S0 = State (0, " ")
        Class.AddState(S0)
        self.IRIClfList.append (Class)

    def InitIDClass (self):
        ############################################################
        # Class: HD*
        ############################################################
        Class = ApiClassifier ("JS-CSS-HTML*", LANG_API_ID, ".html .js .css")
        S0 = State (0, " ")
        Class.AddState(S0)
        self.IDClfList.append (Class)
        
    
    def InitHIClass (self):
        ############################################################
        # Class: HI*
        ############################################################
        Class = ApiClassifier ("HIT*", LANG_API_HI, "*")
        S0 = State (0, " ")
        Class.AddState(S0)
        self.HIClfList.append (Class)
    
    
    def InitFfiClass (self):
        ############################################################
        # Class: C and C++
        ############################################################
        Class = ApiClassifier ("C-C++", LANG_API_FFI, ".c .cpp")
        self.FFIClfList.append (Class)
        
        ############################################################
        # Class: Java and C
        ############################################################
        Class = ApiClassifier ("Java-C", LANG_API_FFI, ".java .c")
        S0 = State (0, "System.loadLibrary")
        S1 = State (1, " native ")
        S0.AddNext(S1)
        Class.AddState(S0)

        S2 = State (2, "JavaVM|JNIEXPORT.*JNICALL.*JNIEnv")
        Class.AddState(S2)
        
        self.FFIClfList.append (Class)

        ############################################################
        # Class: Java and Python
        ############################################################
        Class = ApiClassifier ("Java-Python", LANG_API_FFI, ".py .java")
        S0 = State (0, "from java.* import")
        Class.AddState(S0)
        S1 = State (1, "import org.python.core.*")
        Class.AddState(S1)
        self.FFIClfList.append (Class)

        ############################################################
        # Class: Java and JavaScript
        ############################################################
        Class = ApiClassifier ("Java-JavaScript", LANG_API_FFI, ".java")
        S0 = State (0, "@JavascriptInterface")
        Class.AddState(S0)
        self.FFIClfList.append (Class)

        ############################################################
        # Class: Java and TypeScript
        ############################################################
        Class = ApiClassifier ("Java-TypeScript", LANG_API_FFI, ".ts")
        S0 = State (0, "Cocos2dxJavascriptJavaBridge")
        Class.AddState(S0)
        self.FFIClfList.append (Class)

        ############################################################
        # Class: Java and Ruby
        ############################################################
        Class = ApiClassifier ("Java-Ruby", LANG_API_FFI, ".java .rb")
        S0 = State (0, "require \"java\"")
        Class.AddState(S0)
        S1 = State (1, "org.jruby.javasupport.bsf.JRubyEngine")
        Class.AddState(S1)
        self.FFIClfList.append (Class)

        ############################################################
        # Class: C and Python
        ############################################################
        Class = ApiClassifier ("C-Python", LANG_API_FFI, ".c .py")
        S0 = State (0, "from cffi import FFI|import ctypes")
        Class.AddState(S0)
        S1 = State (1, "#include <Python.h>")
        S2 = State (2, "PyObject|Py_Initialize|PyMethodDef")
        S1.AddNext(S2)
        S3 = State (3, "ctypes.CDLL")
        S1.AddNext(S3)
        Class.AddState(S1)
        self.FFIClfList.append (Class)

        ############################################################
        # Class: C++ and JavaScript
        ############################################################
        Class = ApiClassifier ("C++-JavaScript", LANG_API_FFI, ".cpp .cc")
        S0 = State (0, "Handle<Object>|v8::Local<v8::Object>|v8::Handle<v8::FunctionTemplate>")
        Class.AddState(S0)
        S1 = State (1, "JSContext|JSGlobalContextRef|JSObjectRef|JSStringRef|JSStaticFunction|JSClassDefinition")
        Class.AddState(S1)
        S2 = State (2, "CComPtr<IActiveScript>") 
        S3 = State (3, "IID_IActiveScript|ParseScriptText")
        S2.AddNext(S3)
        Class.AddState(S2)
        self.FFIClfList.append (Class)

        ############################################################
        # Class: C++ and Ruby
        ############################################################
        Class = ApiClassifier ("C++-Ruby", LANG_API_FFI, ".cpp .cc .rb")
        S0 = State (0, "rb_define_module|rb_define_class|rb_class_.*method|rb_define_.*_function|Fiddle.dlopen|require.*fiddle")
        Class.AddState(S0)
        self.FFIClfList.append (Class)

        ############################################################
        # Class: C++ and Objective-C
        ############################################################
        Class = ApiClassifier ("C++-Objective-C", LANG_API_FFI, ".mm")
        S0 = State (0, " ")
        Class.AddState(S0)
        self.FFIClfList.append (Class)

        ############################################################
        # Class: C and Go
        ############################################################
        Class = ApiClassifier ("C-Go", LANG_API_FFI, ".go")
        S0 = State (0, "import \"C\"")
        Class.AddState(S0)
        self.FFIClfList.append (Class)

        ############################################################
        # Class: C and PHP
        ############################################################
        Class = ApiClassifier ("C-PHP", LANG_API_FFI, ".php")
        S0 = State (0, "PHP_FUNCTION")
        S1 = State (1, "ZEND_NUM_ARGS")
        S0.AddNext(S1)
        S2 = State (2, "zend_parse_parameters")
        S1.AddNext(S2)
        Class.AddState(S0)
        self.FFIClfList.append (Class)

        ############################################################
        # Class: Python and Objective-C
        ############################################################
        Class = ApiClassifier ("Python-Objective-C", LANG_API_FFI, ".m")
        S0 = State (0, "PyMODINIT_FUNC")
        S1 = State (1, "PyObject|Py_InitModule")
        S0.AddNext(S1)
        Class.AddState(S0)
        self.FFIClfList.append (Class)

        ############################################################
        # Class: Python and Go
        ############################################################
        Class = ApiClassifier ("Python-Go", LANG_API_FFI, ".go")
        S0 = State (0, "import \"C\"")
        S1 = State (1, "Py_Initialize|Py_Finalize")
        S0.AddNext(S1)
        Class.AddState(S0)
        self.FFIClfList.append (Class)

        ############################################################
        # Class: JavaScript and Go
        ############################################################
        Class = ApiClassifier ("JavaScript-Go", LANG_API_FFI, ".go")
        S0 = State (0, "import \"syscall/js\"")
        Class.AddState(S0)
        self.FFIClfList.append (Class)

        ############################################################
        # Class: Ruby and Go
        ############################################################
        Class = ApiClassifier ("Ruby-Go", LANG_API_FFI, ".go")
        S0 = State (0, "require.*ffi")
        Class.AddState(S0)
        self.FFIClfList.append (Class)


        
    
    
