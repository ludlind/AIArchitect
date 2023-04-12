import os
os.environ["OPENAI_API_KEY"] = "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"

import sys

import langchain as lc
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def use_identity(prompt, variables):
    variables.append("name")
    return "You are \"{name}\". " + prompt

def use_memory(prompt, variables):
    variables.append("memory")
    return "You remember the following: \"{memory}\". " + prompt

def use_post(prompt, post):
    return prompt + post

class Actor:
    def __init__(self, temperature, input_variables, template, parameters, name):
        self.name = name
        if "identity" in parameters:
            template = use_identity(template, input_variables)
        if "memory" in parameters:
            template = use_memory(template, input_variables)
        if "post" in parameters:
            template = use_post(template, parameters["post"])
        self.llm = OpenAI(temperature=temperature, model_name="text-davinci-003")
        self.prompt = PromptTemplate(
            input_variables=input_variables,
            template=template,
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.to_targets = []
        self.alert_targets = []
        self.args = {}
        self.arg("name", name)

    def setName(self, name):
        self.name = name
        self.arg("name", name)

    def say(self, remove_whitespace=True, silence=False):
        response = self.chain.run(self.args)
        if remove_whitespace:
            response = response.strip()
        if not silence:
            print(f"{self.name}:\n", response, "\n")
        return response

    def act(self, remove_whitespace=True):
        response = self.say(remove_whitespace=remove_whitespace)
        for (actor, key) in self.to_targets:
            actor.arg(key, response)
        for actor in self.alert_targets:
            actor.act()

    def to(self, actor, key):
        self.to_targets.append((actor, key))

    def alert(self, actor):
        self.alert_targets.append(actor)
    
    def shout(self, actor, key):
        self.to_targets.append((actor, key))
        self.alert_targets.append(actor)

    def arg(self, key, value):
        self.args[key] = value 

class Lister(Actor):
    def __init__(self, temperature = 0.5, ordered = False, parameters = []):
        if ordered:
            prompt = "Each item in an ordered list starts with a number like \"1. \". Generate an ordered list of the following: {list}. "
        else:
            prompt = "Each item in an unordered list starts with a dash, \"- \". Generate an unordered list of the following: {list}. "
        variables = ["list"]
        super().__init__(temperature, variables, prompt, parameters, "Lister")

class Evaluator(Actor):
    def __init__(self, temperature = 0.5, parameters = []):
        variables = ["criteria", "text"]
        prompt = "In the following text: \"{text}\", evaluate the criteria: \"{criteria}\". "
        super().__init__(temperature, variables, prompt, parameters, "Evaluator")

class Checker(Actor):
    def __init__(self, temperature = 0.5, parameters = []):
        variables = ["condition", "text"]
        prompt = "In the following text: \"{text}\", check that the following condition is satisfied: \"{condition}\". Answer only True or False. "
        super().__init__(temperature, variables, prompt, parameters, "Checker")

class Critic(Actor):
    def __init__(self, temperature = 0.5, parameters = []):
        variables = ["criteria", "text"]
        prompt = "Criticize the following text: \"{text}\" according to the following criteria: \"{criteria}\". "
        super().__init__(temperature, variables, prompt, parameters, "Critic")

class Arguer(Actor):
    def __init__(self, temperature = 0.5, parameters = []):
        variables = ["goal", "text"]
        prompt = "Argue the following point: \"{goal}\" in response to the following: \"{text}\". "
        super().__init__(temperature, variables, prompt, parameters, "Arguer")

class Modifier(Actor):
    def __init__(self, temperature = 0.5, parameters = []):
        variables = ["modification", "text"]
        prompt = "Perform the modification: \"{modification}\" in the following text: \"{text}\". "
        super().__init__(temperature, variables, prompt, parameters, "Modifier")

class Quiter(Actor):
    def __init__(self):
        self.to_targets = []
        self.alert_targets = []
        self.name = "Quiter"
    
    def say(self, remove_whitespace=True, silence=False):
        if not silence and self.shouldQuit:
            print("Shuting down!")

    def act(self, remove_whitespace=True):
        self.say(remove_whitespace=remove_whitespace)
        if self.shouldQuit:
            sys.exit()

    def arg(self, key, value):
        self.shouldQuit = (key.lower() == "quit" and "true" in value.lower())

class Accumulator(Actor):
    def __init__(self):
        self.to_targets = []
        self.alert_targets = []
        self.acc = ""
        self.name = "Accumulator"
    
    def say(self, remove_whitespace=True, silence=False):
        response = self.acc
        self.acc = ""
        if remove_whitespace:
            response = response.strip()
        if not silence:
            print(f"{self.name}:\n", response, "\n")
        return response
    
    def arg(self, key, value):
        self.acc += f"{key}: {value}\n" 

class Memory(Actor):
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

