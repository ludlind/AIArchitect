from abc import ABC, abstractmethod

class ActorInterface(ABC):
    
    @abstractmethod
    def act(self):
        pass
    
    @abstractmethod
    def receive(self, key, value):
        pass
    
    @abstractmethod
    def bind(self, actor, to, port=""):
        pass

    @abstractmethod
    def alert(self, actor):
        pass

    @property
    @abstractmethod
    def name(self):
        pass
