from .interface import Interface
from elevenlabs import generate, play

class Voice(Interface):
    
    _type_label = "voice"

    def __init__(self, args=None):
        self._name = "Voice"
        self._bindings = []
        self._alerts = []
        self._silent = False
        self._text = ""
        self._voice = ""
    
    def say(self):
        if not self._silent:
            prestring = f"{self.name}:\n" if self.name != "" else ""
            print(f"{prestring}{self._voice}\n{self._text}\n")
        audio = generate(text=self._text, voice=self._voice)
        play(audio)
    
    def act(self):
        self.say()
        for (component, to, _) in self._bindings:
            component.receive(to, response)
        for component in self._alerts:
            component.act()

    def receive(self,
                key: str,
                value: str):
        if key == "text":
            self._text += value
        elif key == "voice":
            self._voice = f"{value.strip()}"
    
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
