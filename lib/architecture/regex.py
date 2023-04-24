from .interface import Interface
import re

class Regex(Interface):
    
    _type_label = "regex"

    def __init__(self, args=None):
        self._name = "Regular Expression"
        self._bindings = []
        self._alerts = []
        self._silent = False
        self._regex = None
        self._text = ""
    
    def say(self):
        match = self._regex.search(self._text)
        first = match.group()
        if match.span()[1] < len(self._text):
            rest = self._text[match.span()[1]:]
        else:
            rest = ""
        if not self._silent:
            prestring = f"{self.name}:\n" if self.name != "" else ""
            print(f"{prestring}{first}\n")
        return first, rest
    
    def act(self):
        first, rest = self.say()
        for (component, to, port) in self._bindings:
            if port == "first":
                component.receive(to, first)
            elif port == "rest":
                component.receive(to, rest)
        for component in self._alerts:
            component.act()

    def receive(self,
                key: str,
                value: str):
        if key == "regex":
            self._regex = re.compile(value)
        if key == "text":
            self._text = value
    
    def bind(self,
             component: Interface,
             to: str,
             port: str=""):
        self._bindings.append((component, to, port))

    def alert(self,
              component: Interface):
        self._alerts.append(component)

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
