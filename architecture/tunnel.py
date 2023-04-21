"""
from actorinterface import ActorInterface

class Tunnel(ActorInterface):
    #"""
    Basically just a temporary solution to the issue of connection lines overlapping components.
    #"""

    tunnels = []

    def __init__(self):
        self._name = "Tunnel"
        self._id
        self._bindings = []
        self._alerts = []
        self._silent = False
        self._memory = ""
    
    def act(self):
        response = self.say()
        for (actor, to, _) in self._bindings:
            actor.receive(to, response)
        for actor in self._alerts:
            actor.act()

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
"""
