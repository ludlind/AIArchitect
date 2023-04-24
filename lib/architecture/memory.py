from .interface import Interface

class Memory(Interface):
    
    _type_label = "memory"

    def __init__(self, args=None):
        self._name = "Memory"
        self._bindings = []
        self._alerts = []
        self._silent = False
        self._memory = ""
    
    def say(self):
        if not self._silent:
            prestring = f"{self.name}:\n" if self.name != "" else ""
            print(f"{prestring}{self._memory}\n")
        return self._memory
    
    def act(self):
        response = self.say()
        for (component, to, _) in self._bindings:
            component.receive(to, response)
        for component in self._alerts:
            component.act()

    def receive(self,
                key: str,
                value: str):
        if key == "store":
            self._memory += f"{value.strip()}\n"
        elif key == "clear":
            self._memory = ""
        elif key == "replace":
            self._memory = f"{value.strip()}\n"
    
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
