import os
os.environ["OPENAI_API_KEY"] = "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"

from llmactor import LLMActor
from memoryactor import MemoryActor

LLMActor.loadPresets("presets.json")

a = LLMActor()
s = LLMActor()
m = MemoryActor()
a.loadPreset("Lister")
s.loadPreset("Summarizer")
a.receive("list", "Fruit")
a.bind(m, "store")
a.alert(m)
m.bind(s,"text")
m.alert(s)
s.bind(m, "replace")
s.alert(m)
a.act()
