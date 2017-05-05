import imp
import os

class Bootstrap():
    Modules = {} # Modules
    def __init__(self):
        self.start()
    def start(self):
        files = os.listdir("./modules");
        modules = []
        for path in files:
            if path.find(".py") != -1 and path.find(".pyc") == -1:
                modules.append(path)
        for i in range(0,len(modules)):
            filename = modules[i];
            name = modules[i].replace(".py","")
            self.Modules[name] = imp.load_source(name,"./modules/" + filename);