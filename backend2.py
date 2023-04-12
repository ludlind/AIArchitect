import os
os.environ["OPENAI_API_KEY"] = "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"

import sys

import langchain as lc
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from actorinterface import ActorInterface

class LLMActor(ActorInterface):

    presets = {
            "Lister": (["list"], "Make a list of the following: \"{list}\"")
    }

    def __init__(self,
                 name: str):
        self.name = name
        self.bindings = []
        self.alerts = []
        self.ports = {}
        self.llm = None
        self.prompt = None
        self.chain = None
    
    @classmethod
    def preset(cls,
               label: str):
        return *(cls.presets[label])

    def setup(self,
              input_variables: list[str],
              template: str,
              temperature: float=0.7,
              model_name: str="text-ada-001"):
        self.llm = OpenAI(temperature=temperature,
                          model_name=model_name)
        self.prompt = PromptTemplate(input_variables=input_variables,
                                     template=template)
        self.chain = LLMChain(llm=self.llm,
                              prompt=self.prompt)

    def loadPreset(self,
                   label: str,
                   temperature: float=0.7,
                   model_name: str="text-ada-001"):
        self.setup(LLMActor.preset(label),
                   temperature=temperature,
                   model_name=model_name)

    def say(self):
        response = self.chain.run(self.ports)
        response = response.strip()
        if not self.silent:
            print(f"{self.name}:\n{response}\n")
        return response

    def act(self):
        response = self.say()
        for (actor, to) in self.bindings:
            actor.receive(to, response)
        for actor in self.alerts:
            actor.act()

    def receive(self,
                key: str,
                value):
        self.ports[key] = value 
    
    def bind(self,
             actor: ActorInterface,
             to: str):
        self.bindings.append((actor, to))

    def alert(self,
              actor: ActorInterface):
        self.alerts.append(actor)

    @property
    def name(self):
        return self.name

    @name.setter
    def name(self,
             name: str):
        self.name = name

class MemoryActor(ActorInterface):
    def __init__(self, temperature, parameters = []):
        super().__init__(temperature, ["text"], "Summarize the following text: \"{text}\". ", parameters, "Memory")
        self.memory = ""
        self.args = {}
    
    def say(self, remove_whitespace=True, silence=False):
        for key, value in self.args.items():
            if key != "summarize":
                self.memory += f"{key}: {value}\n"
        if "summarize" in self.args:
            self.memory = self.chain.run(self.memory)
        if remove_whitespace:
            self.memory = self.memory.strip()
        self.args = {}
        if not silence:
            print(f"{self.name}:\n", self.memory, "\n")
        return self.memory

