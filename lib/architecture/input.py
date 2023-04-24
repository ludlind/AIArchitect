from .interface import Interface

class Input(Interface):
    
    _type_label = "input"

    def __init__(self, args=None):
        self._name = "Input"
        self._prompt = "Prompt: "
        self._bindings = []
        self._alerts = []
        self._silent = False
    
    def say(self):
        if not self._silent and self.name != "":
            print(f"{self.name}:")
        user_input = input(self._prompt)
        print("")
        return user_input
    
    def act(self):
        response = self.say()
        for (component, to, _) in self._bindings:
            component.receive(to, response)
        for component in self._alerts:
            component.act()

    def receive(self,
                key: str,
                value: str):
        if key == "prompt":
            self._prompt = f"{value.strip()}"
    
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
