from .interface import Interface
import re

class Conditional(Interface):
    
    _type_label = "conditional"

    def __init__(self, args=None):
        self._name = "Conditional"
        self._alerts1 = []
        self._alerts2 = []
        self._silent = False
        self._regex = re.compile("\s*([Tt][Rr][Uu][Ee])\s*")
        self._cond = True
    
    def say(self):
        if not self._silent:
            prestring = f"{self.name}:\n" if self.name != "" else ""
            print(f"{prestring}{'True' if self._cond else 'False'}\n")
    
    def act(self):
        self.say()
        if self._cond:
            for component in self._alerts1:
                component.act()
        else:
            for component in self._alerts2:
                component.act()

    def receive(self,
                key: str,
                value: str):
        if key == "text":
            self._cond = re.fullmatch(self._regex, value) is not None
    
    def bind(self,
             component: Interface,
             to: str,
             port: str=""):
        if port == "if-true":
            self._alerts1.append(component)
        elif port == "if-false":
            self._alerts2.append(component)

    def alert(self,
              component: Interface):
        pass
        #self._alerts.append(component)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self,
             name: str):
        self._name = name

    @property
    def silent(self):
        return self._silent

    @silent.setter
    def silent(self,
             silent: bool):
        self._silent = silent
