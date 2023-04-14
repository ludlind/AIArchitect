import os
os.environ["OPENAI_API_KEY"] = "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"

from llmactor import LLMActor
from memoryactor import MemoryActor
from regexactor import RegexActor
from inputactor import InputActor
from wrapperactor import WrapperActor
import json
import sys
import argparse

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
    actorBuffer = {}
    for sectkey, section in archdict["architecture"].items():
        debugmes(sectkey, 1, debug)
        for key, cmds in section.items():
            debugmes(key, 2, debug)
            act = None
            if key in actorBuffer:
                act = actorBuffer[key]
            for cmdkey, cmdargs in cmds.items():
                debugmes(cmdkey, 3, debug)
                if cmdkey == "llmactor":
                    debugmes(cmdargs, 4, debug)
                    act = LLMActor()
                    act.loadPreset(cmdargs)
                    actorBuffer[key] = act
                elif cmdkey == "memoryactor":
                    act = MemoryActor()
                    actorBuffer[key] = act
                elif cmdkey == "regexactor":
                    act = RegexActor()
                    actorBuffer[key] = act
                elif cmdkey == "inputactor":
                    act = InputActor()
                    actorBuffer[key] = act
                elif cmdkey == "wrapperactor":
                    act = WrapperActor()
                    actorBuffer[key] = act
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
                        act2 = actorBuffer[actkey]
                        if isinstance(value, list):
                            act.bind(act2, value[0], port=value[1])
                        else:
                            act.bind(act2, value)
                elif cmdkey == "alert":
                    for actkey in cmdargs.keys():
                        debugmes(actkey, 4, debug)
                        act.alert(actorBuffer[actkey])
                elif cmdkey == "receive":
                    for input_variable, value in cmdargs.items():
                        debugmes(input_variable, 4, debug)
                        debugmes(value, 5, debug)
                        act.receive(input_variable, value)
                elif cmdkey == "act":
                    act.act()
                elif cmdkey == "alias":
                    if not isinstance(act, WrapperActor):
                        raise TypeError("alias can only be run on wrappers")
                    for actkey, value in cmdargs.items():
                        debugmes(actkey, 4, debug)
                        debugmes(value, 5, debug)
                        act2 = actorBuffer[actkey]
                        if isinstance(value, list):
                            act.alias(act2, value[0], port=value[1])
                        else:
                            act.alias(act2, value)
                elif cmdkey == "internalert":
                    if not isinstance(act, WrapperActor):
                        raise TypeError("alias can only be run on wrappers")
                    for actkey in cmdargs.keys():
                        debugmes(actkey, 4, debug)
                        act.intern_alert(actorBuffer[actkey])

    return actorBuffer

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='archiload',
                    description='Loads presets and architectures from json files.',
                    epilog='')
    parser.add_argument('filename')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()
    with open(args.filename, "r") as f:
        archdict = json.load(f)
    LLMActor.loadPresets(archdict)
    debugmes("\nBuild Order:", 0, args.debug)
    loadArch(archdict, debug=args.debug)
