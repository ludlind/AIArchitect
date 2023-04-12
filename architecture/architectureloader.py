import os
os.environ["OPENAI_API_KEY"] = "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"

from llmactor import LLMActor
from memoryactor import MemoryActor
import json
import sys

actorBuffer = {}
def loadArch(archdict: dict):
    global actorBuffer
    for section in archdict["architecture"].values():
        for key, cmds in section.items():
            act = None
            if key in actorBuffer:
                act = actorBuffer[key]
            for cmdkey in cmds.keys():
                if cmdkey == "llmactor":
                    act = LLMActor()
                    act.loadPreset(cmds[cmdkey])
                    actorBuffer[key] = act
                elif cmdkey == "memoryactor":
                    act = MemoryActor()
                    actorBuffer[key] = act
                elif cmdkey == "bind":
                    for actkey, value in cmds[cmdkey].items():
                        act2 = actorBuffer[actkey]
                        act.bind(act2, value)
                elif cmdkey == "alert":
                    for actkey in cmds[cmdkey].keys():
                        act.alert(actorBuffer[actkey])
                elif cmdkey == "receive":
                    for input_variable in cmds[cmdkey].keys():
                        value = cmds[cmdkey][input_variable]
                        act.receive(input_variable, value)
                elif cmdkey == "act":
                    act.act()

if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, "r") as f:
        archdict = json.load(f)
    LLMActor.loadPresets(archdict)
    loadArch(archdict)
