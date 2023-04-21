from .actorinterface import ActorInterface
from elevenlabs import generate, play

class VoiceActor(ActorInterface):
    
    _type_label = "voiceactor"

    def __init__(self):
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
        for (actor, to, _) in self._bindings:
            actor.receive(to, response)
        for actor in self._alerts:
            actor.act()

    def receive(self,
                key: str,
                value: str):
        if key == "text":
            self._text += value
        elif key == "voice":
            self._voice = f"{value.strip()}"
    
    def bind(self,
             actor: ActorInterface,
             to: str,
             port: str=""):
        self._bindings.append((actor, to, port))

    def alert(self,
              actor: ActorInterface):
        self._alerts.append(actor)

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
