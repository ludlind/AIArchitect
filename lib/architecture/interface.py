from abc import ABC, abstractmethod

class Interface(ABC):

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
    def bind(self, component, to, port=""):
        pass

    @abstractmethod
    def alert(self, component):
        pass

    @property
    @abstractmethod
    def name(self):
        pass
