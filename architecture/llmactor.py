import langchain as lc
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from actorinterface import ActorInterface
from typing import Union
import json

class LLMActor(ActorInterface):

    presets = {}

    def __init__(self):
        self._name = ""
        self._bindings = []
        self._alerts = []
        self._ports = {}
        self._silent = False
        self._llm = None
        self._prompt = None
        self._chain = None
    
    @classmethod
    def preset(cls,
               label: str):
        return cls.presets[label]

    @classmethod
    def loadPresets(cls,
                    archdict: dict):
        for label, presetdict in archdict["llmactor-presets"].items():
            cls.presets[label] = (presetdict["input_variables"], presetdict["template"])

    def setup(self,
              input_variables: list[str],
              template: str,
              temperature: float=0.7,
              model_name: str="text-davinci-003"):
        self._llm = OpenAI(temperature=temperature,
                          model_name=model_name)
        self._prompt = PromptTemplate(input_variables=input_variables,
                                     template=template)
        self._chain = LLMChain(llm=self._llm,
                              prompt=self._prompt)

    def loadPreset(self,
                   label: Union[str, list[str]],
                   temperature: float=0.7,
                   model_name: str="text-davinci-003"):
        if isinstance(label, str):
            self.setup(*LLMActor.preset(label),
                       temperature=temperature,
                       model_name=model_name)
            self.name = label
        elif isinstance(label, list):
            name = ""
            template = ""
            input_variables = []
            for lbl in label:
                invars, temp = LLMActor.preset(lbl)
                name += f" {lbl}"
                template += temp
                input_variables = list(set().union(input_variables, invars))
            self.setup(input_variables,
                       template,
                       temperature=temperature,
                       model_name=model_name)
            self.name = name.strip()


    def say(self):
        response = self._chain.run(self._ports)
        response = response.strip()
        if not self.silent:
            prestring = f"{self.name}:\n" if self.name != "" else ""
            print(f"{prestring}{response}\n")
        return response

    def act(self):
        response = self.say()
        for (actor, to, _) in self._bindings:
            actor.receive(to, response)
        for actor in self._alerts:
            actor.act()

    def receive(self,
                key: str,
                value):
        self._ports[key] = value 
    
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
