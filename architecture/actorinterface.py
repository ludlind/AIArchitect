from abc import ABC, abstractmethod

class ActorInterface(ABC):

    _subclass_dictionary = dict()
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._subclass_dictionary[cls._type_label] = cls

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
