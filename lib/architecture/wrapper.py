from .interface import Interface

class Wrapper(Interface):

    _type_label = "wrapper"

    def __init__(self, args=None):
        self._name = "Wrapper"
        self._alerts = []
        self._internalerts = []
        self._aliases = {}
        self._silent = False
        self._wakeup = False

    def act(self):
        if self._wakeup:
            self._wakeup = False
            for component in self._alerts:
                component.act()
        else:
            if not self.silent and self.name != "":
                print(f"{self._name}:")
            for component in self._internalerts:
                component.act()

    def receive(self,
                key: str,
                value):
        if key == "_wakeup":
            self._wakeup = True
        else:
            component, port = self._aliases[key]
            component.receive(port, value)
    
    def bind(self,
             component: Interface,
             to: str,
             port: str=""):
        if port not in self._aliases:
            raise ValueError("must specify a valid wrapper outport when binding wrapper")
        internal_component, intport = self._aliases[port]
        internal_component.bind(component, to, port=intport)

    def alert(self,
              component: Interface):
        self._alerts.append(component)

    def intern_alert(self,
                     component: Interface):
        self._internalerts.append(component)

    def alias(self,
              component: Interface,
              alias: str,
              port: str=""):
        self._aliases[alias] = (component, port)

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

