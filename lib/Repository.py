
class Repository ():
    def __init__(self, Id, Star,     Langs, ApiUrl, CloneUrl, Topics, Descripe, Created, Pushed):
        self.Id       = Id
        self.Star     = Star
        self.MainLang = ''
        self.Langs    = Langs
        self.ApiUrl   = ApiUrl
        self.CloneUrl = CloneUrl
        self.Topics   = Topics
        self.Descripe = Descripe
        self.Created  = Created
        self.Pushed   = Pushed
        
    def SetMainLang (self, MainLang):
        self.MainLang = MainLang
    
