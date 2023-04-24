import tkinter as tk
from .canvasobject import CanvasObject
from .port import Port

class Component(CanvasObject):

    presets = {}
    preset_counter = {}

    def __init__(self, app, x, y, preset):
        super().__init__(app, x, y)
        self.fill = ""
        self.label = ""
        self.type = ""
        self.args = ""
        self.ports = []
        self.loadPreset(preset)

    def __del__(self):
        for port in self.ports:
            port.__del__()
        super().__del__()
        

    def display_info(self):
        infodisp = self.app.infodisp
        infodisp.setTitle(self.label)
        infodisp.clear()
        infodisp.addLabel("Label")
        infodisp.addLabel("Type")
        infodisp.addLabel("Arguments")
        def set_label(txt, self=self):
            self.label = txt
            self.display_info()
        def set_type(txt, self=self):
            self.type = txt
            self.display_info()
        def set_args(txt, self=self):
            self.args = txt
            self.display_info()
        infodisp.addEntry(self.label, set_label)
        infodisp.addEntry(self.type, set_type)
        infodisp.addEntry(self.args, set_args)

    def move(self, dx, dy):
        super().move(dx, dy)
        for port in self.ports:
            port.update() 

    def loadPreset(self,
                   label: str):
        self.preset = label
        presetdict = self.presets[label]
        self.label = label + f" {self.preset_counter[label]}"
        self.preset_counter[label] += 1
        self.type = presetdict["type"]
        self.args = presetdict["args"]
        for value in presetdict["shapes"]:
            self.add_shape(value, setTag="body")
        for presetlabel, portdict in presetdict["ports"].items():
            port = Port(self, presetlabel, portdict)
            self.ports.append(port)
    
    def serialize_setup(self, rootdict):
        comp_setup_dict = {}
        preset_dict = self.presets[self.preset]
        comp_setup_dict["init"] = [preset_dict["type"]] +\
                (preset_dict["args"] if isinstance(preset_dict["args"], list) else [preset_dict["args"]])
        for port in self.ports:
            port.serialize_setup(comp_setup_dict)
        if comp_setup_dict:
            rootdict[self.label] = comp_setup_dict

    def serialize_struct(self, rootdict):
        comp_struct_dict = {}
        for port in self.ports:
            port.serialize_struct(comp_struct_dict)
        if comp_struct_dict:
            rootdict[self.label] = comp_struct_dict

    def serialize_run(self, rootdict):
        comp_run_dict = {}
        for port in self.ports:
            port.serialize_run(comp_run_dict)
        if comp_run_dict:
            rootdict[self.label] = comp_run_dict

    def serialize_canvas(self, canvasdict):
        compdict = {}
        compdict["x"] = self.x
        compdict["y"] = self.y
        compdict["preset"] = self.preset
        portdict = {}
        for port in self.ports:
            port.serialize_canvas(portdict)
        compdict["ports"] = portdict
        canvasdict[self.label] = compdict

    @classmethod
    def deserialize_canvas(cls, app, compsdict):
        for label, compdict in compsdict.items():
            comp = Component(app, compdict["x"], compdict["y"], compdict["preset"])
            comp.label = label
        for label, compdict in compsdict.items():
            comp = None
            for obj in CanvasObject.objects:
                if isinstance(obj, Component) and obj.label == label:
                    comp = obj
            if comp is None:
                print(f"Component {label} does not exist.")
                continue
            portdict = compdict["ports"]
            for label, conlist in portdict.items():
                port = None
                for p in comp.ports:
                    if p.label == label:
                        port = p
                        break
                if port is None:
                    print(f"Port {label} does not exist.")
                    continue
                for condict in conlist:
                    tcomp = None
                    for obj in CanvasObject.objects:
                        if isinstance(obj, Component) and obj.label == condict["target-component"]:
                            tcomp = obj
                            break
                    if tcomp is None:
                        print(f"Component {condict['target-component']} does not exist.")
                        continue
                    tport = None
                    for p in tcomp.ports:
                        if p.label == condict["target-port"]:
                            tport = p
                            break
                    if tport is None:
                        print(f"Port {condict['target-port']} does not exits.")
                        continue
                    port.connect(tport, curvex=condict["curve-x"], curvey=condict["curve-y"])


    @classmethod
    def loadPresets(cls,
                    compdict: str):
        for label, presetdict in compdict.items():
            cls.presets[label] = presetdict
            cls.preset_counter[label] = 1
