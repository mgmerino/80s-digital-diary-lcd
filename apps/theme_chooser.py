from apps.base import App
from core.ui import cls, header
from core.context import THEMES

class ThemeChooserApp(App):
    title="Tema"; tick_ms=200
    def __init__(self):
        self.names=list(THEMES.keys()); self.idx=0
    
    def draw(self, ctx):
        cls(ctx); header(ctx,"Tema")
        for i,n in enumerate(self.names):
            mark=">" if i==self.idx else " "
            ctx.d.text("{} {}".format(mark,n), 2, 12+i*8, ctx.W, 1)
    
    def handle_key(self, ctx, k):
        if k in (ord('q'),27): return "pop"
        if k==ord('j') and self.idx< len(self.names)-1: self.idx+=1
        elif k==ord('k') and self.idx>0: self.idx-=1
        elif k==13:
            ctx.settings["theme"]=self.names[self.idx]
            ctx.ds.update_settings({"theme":ctx.settings["theme"]})
            ctx.theme.apply()
            return "pop"


  