import os
os.environ["OPENAI_API_KEY"] = "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"
os.environ["ELEVEN_API_KEY"] = "e4e7cd6dd6d00c1035bc7f5f123b06a6"

from .interface import Interface
from .llmactor import LLMActor
from .memory import Memory
from .regex import Regex
from .input import Input
from .wrapper import Wrapper
from .voice import Voice
from .conditional import Conditional
import json
import yaml
import sys
import argparse

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def debugmes(mes, level=0, debug=False):
    if debug:
        lev = ""
        if level == 1:
            lev = "+ "
        if level > 1:
            lev = "|"
            lev += "--"*(level-1) + " "
        if isinstance(mes, str):
            print(f"{lev}{mes}")
            sys.stdout.flush()
        else:
            for m in list(mes):
                print(f"{lev} {mes}")
            sys.stdout.flush()

def loadArch(archdict: dict, debug=False):
    componentBuffer = {}
    for sectkey, section in archdict["architecture"].items():
        debugmes(sectkey, 1, debug)
        for key, cmds in section.items():
            debugmes(key, 2, debug)
            act = None
            if key in componentBuffer:
                act = componentBuffer[key]
            for cmdkey, cmdargs in cmds.items():
                debugmes(cmdkey, 3, debug)
                if cmdkey == "init":
                    for label, cls in Interface._subclass_dictionary.items():
                        if isinstance(cmdargs, list):
                            if cmdargs[0] == label:
                                act = cls(args=cmdargs[1:])
                                componentBuffer[key] = act
                        else:
                            if cmdargs == label:
                                act = cls()
                                componentBuffer[key] = act
                elif cmdkey == "name":
                    if not isinstance(cmdargs, str):
                        raise ValueError("value of name has to be a string")
                    act.name = cmdargs
                elif cmdkey == "silent":
                    act.silent = True
                elif cmdkey == "bind":
                    for actkey, value in cmdargs.items():
                        debugmes(actkey, 4, debug)
                        debugmes(value, 5, debug)
                        act2 = componentBuffer[actkey]
                        if isinstance(value, list):
                            act.bind(act2, value[0], port=value[1])
                        else:
                            act.bind(act2, value)
                elif cmdkey == "alert":
                    for actkey in cmdargs.keys():
                        debugmes(actkey, 4, debug)
                        act.alert(componentBuffer[actkey])
                elif cmdkey == "receive":
                    for input_variable, value in cmdargs.items():
                        debugmes(input_variable, 4, debug)
                        debugmes(value, 5, debug)
                        act.receive(input_variable, value)
                elif cmdkey == "act":
                    act.act()
                elif cmdkey == "alias":
                    if not isinstance(act, Wrapper):
                        raise TypeError("alias can only be run on wrappers")
                    for actkey, value in cmdargs.items():
                        debugmes(actkey, 4, debug)
                        debugmes(value, 5, debug)
                        act2 = componentBuffer[actkey]
                        if isinstance(value, list):
                            act.alias(act2, value[0], port=value[1])
                        else:
                            act.alias(act2, value)
                elif cmdkey == "internalert":
                    if not isinstance(act, Wrapper):
                        raise TypeError("alias can only be run on wrappers")
                    for actkey in cmdargs.keys():
                        debugmes(actkey, 4, debug)
                        act.intern_alert(componentBuffer[actkey])
    return componentBuffer

def loadFile(filename, debug):
    with open(filename, "r") as f:
        dictionary = yaml.load(f, Loader=Loader)
    if "include" in dictionary:
        for incfilename in dictionary["include"]:
            loadFile(incfilename, debug)
    if "llmactor-presets" in dictionary:
        LLMActor.loadPresets(dictionary)
    if "architecture" in dictionary:
        debugmes("\nBuild Order:", 0, debug)
        loadArch(dictionary, debug=debug)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='archiload',
                    description='Loads presets and architectures from yaml files.',
                    epilog='')
    parser.add_argument('filename')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()
    loadFile(args.filename, args.debug)
