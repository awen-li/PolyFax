
class Repository ():
    def __init__(self, Id, Star,     Langs, ApiUrl, CloneUrl, Topics, Descripe, Created, Pushed):
        Langs = eval (str(Langs))
        self.Id       = Id
        self.Name     = ''
        self.Star     = Star
        self.MainLang = ''
        self.Langs    = [lang.lower () for lang in Langs]
        self.ApiUrl   = ApiUrl
        self.CloneUrl = CloneUrl
        self.Topics   = Topics
        self.Descripe = Descripe
        self.Created  = Created
        self.Pushed   = Pushed
        
    def SetMainLang (self, MainLang):
        self.MainLang = MainLang.lower ()

    def SetName (self, Name):
        self.Name = Name
    
