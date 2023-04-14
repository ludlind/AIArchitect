from actorinterface import ActorInterface
#import json

class WrapperActor(ActorInterface):

    def __init__(self):
        self._name = "Wrapper"
        self._alerts = []
        self._internalerts = []
        self._aliases = {}
        self._silent = False
        self._wakeup = False

    def act(self):
        if self._wakeup:
            self._wakeup = False
            for actor in self._alerts:
                actor.act()
        else:
            if not self.silent and self.name != "":
                print(f"{self._name}:")
            for actor in self._internalerts:
                actor.act()

    def receive(self,
                key: str,
                value):
        if key == "_wakeup":
            self._wakeup = True
        else:
            actor, port = self._aliases[key]
            actor.receive(port, value)
    
    def bind(self,
             actor: ActorInterface,
             to: str,
             port: str=""):
        if port not in self._aliases:
            raise ValueError("must specify a valid wrapper outport when binding wrapper")
        internal_actor, intport = self._aliases[port]
        internal_actor.bind(actor, to, port=intport)

    def alert(self,
              actor: ActorInterface):
        self._alerts.append(actor)

    def intern_alert(self,
                     actor: ActorInterface):
        self._internalerts.append(actor)

    def alias(self,
              actor: ActorInterface,
              alias: str,
              port: str=""):
        self._aliases[alias] = (actor, port)

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

