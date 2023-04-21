from actorinterface import ActorInterface

class InputActor(ActorInterface):
    
    _type_label = "inputactor"

    def __init__(self):
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
        for (actor, to, _) in self._bindings:
            actor.receive(to, response)
        for actor in self._alerts:
            actor.act()

    def receive(self,
                key: str,
                value: str):
        if key == "prompt":
            self._prompt = f"{value.strip()}"
    
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
