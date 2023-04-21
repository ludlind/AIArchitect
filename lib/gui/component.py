import tkinter as tk
from .port import Port

def mix_colors(root, color1, color2, mix):
    rgb1 = root.winfo_rgb(color1)
    rgb2 = root.winfo_rgb(color2)
    rgb_mix = (int(mix*rgb1[0] + (1-mix)*rgb2[0]),
               int(mix*rgb1[1] + (1-mix)*rgb2[1]),
               int(mix*rgb1[2] + (1-mix)*rgb2[2]))
    return "#%02x%02x%02x" % rgb_mix

class Component:

    presets = {}
    preset_counter = {}
    components = []
    selected_components = []

    def __init__(self, app, x, y, preset):
        self.app = app
        self.canvas = self.app.canvas
        self.x, self.y = x, y
        self.start_x, self.start_y = x, y
        self.width, self.height = 0, 0
        self.fill = ""
        self.label = ""
        self.type = ""
        self.args = ""
        self.ports = []
        self.rectangle = None
        self.loadPreset(preset)
        self.canvas.tag_bind(self.rectangle, "<ButtonPress-1>", self.on_left_click)
        self.canvas.tag_bind(self.rectangle, "<B1-Motion>", self.on_left_hold)
        self.canvas.tag_bind(self.rectangle, "<ButtonRelease-1>", self.on_left_release)
        self.canvas.tag_bind(self.rectangle, "<ButtonPress-3>", self.on_right_click)

    def __del__(self):
        self.canvas.delete(self.rectangle)
        for i, _ in enumerate(self.ports):
            self.ports[i].__del__()
        self.components.remove(self)

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

    def on_left_click(self, event):
        if not self.app.shift_pressed.get():
            if self.app.ctrl_pressed.get():
                if self.selected():
                    self.unselect(self)
                else:
                    self.select(self)
            else:
                if not self.selected():
                    self.select_only(self)
                self.display_info()

    def on_left_hold(self, event):
        if not self.app.shift_pressed.get():
            dx = self.canvas.canvasx(event.x) - self.app.click_x
            dy = self.canvas.canvasy(event.y) - self.app.click_y
            for comp in self.selected_components:
                comp.move(dx, dy)
    
    def on_left_release(self, event):
        for comp in self.selected_components:
            comp.start_x, comp.start_y = comp.x, comp.y

    def on_right_click(self, event):
        context_menu = self.app.context_menu
        if context_menu is not None:
            context_menu.destroy()
        context_menu = tk.Menu(self.canvas, tearoff=0)
        context_menu.add_command(label="Delete", command=lambda: self.delete_selected() )
        context_menu.post(event.x_root, event.y_root)
        self.app.context_menu = context_menu

    def move(self, dx, dy):
        self.x, self.y = self.start_x + dx, self.start_y + dy
        self.canvas.moveto(self.rectangle, self.x, self.y)
        for port in self.ports:
            port.move()

    def delete_selected(self):
        if self.selected_components and self.selected():
            self.unselect(self)
            for comp in self.selected_components:
                comp.__del__()
            self.clear_selection()
            self.__del__()
        elif not self.selected():
            self.__del__()
        
    def loadPreset(self,
                   label: str):
        preset = self.presets[label]
        self.preset = preset
        self.fill = preset["color"]
        self.label = label + f" {self.preset_counter[label]}"
        self.preset_counter[label] += 1
        self.type = preset["actortype"]
        self.args = preset["args"]
        self.width = preset["width"]
        self.height = preset["height"]
        self.rectangle = self.canvas.create_rectangle(self.x, self.y,
                                                      self.x + self.width, self.y + self.height,
                                                      fill=self.fill, outline="")
        for presetlabel, portdict in preset["ports"].items():
            port = Port(self.app, self, presetlabel, portdict, self.x, self.y)
            self.ports.append(port)

    def selected(self):
        return self in self.selected_components
    
    @classmethod
    def loadPresets(cls,
                    compdict: str):
        for label, presetdict in compdict["component-presets"].items():
            cls.presets[label] = presetdict
            cls.preset_counter[label] = 1
    
    @classmethod
    def select(cls, comp):
        cls.selected_components.append(comp)
        cls.update_selected()

    @classmethod
    def unselect(cls, comp):
        cls.selected_components.remove(comp)
        cls.update_selected()

    @classmethod
    def clear_selection(cls):
        cls.selected_components.clear()
        cls.update_selected()

    @classmethod
    def select_only(cls, comp):
        cls.selected_components.clear()
        cls.selected_components.append(comp)
        cls.update_selected()

    @classmethod
    def update_selected(cls):
        for comp in cls.components:
            if comp.selected():
                #comp.canvas.itemconfig(comp.rectangle, fill=mix_colors(comp.app, comp.fill, "green", 0.7))
                comp.canvas.itemconfig(comp.rectangle, outline="green")
                for port in comp.ports:
                    #comp.canvas.itemconfig(port.circle, fill=mix_colors(comp.app, port.fill, "green", 0.7))
                    comp.canvas.itemconfig(port.circle, outline="green")

            else:
                #comp.canvas.itemconfig(comp.rectangle, fill=comp.fill)
                comp.canvas.itemconfig(comp.rectangle, outline="")
                for port in comp.ports:
                    #comp.canvas.itemconfig(port.circle, fill=port.fill)
                    comp.canvas.itemconfig(port.circle, outline="")

    def dictionary_setup_stage(self, rootdict):
        comp_setup_dict = {}
        preset_dict = self.preset
        comp_setup_dict[preset_dict["actortype"]] = preset_dict["args"]
        for port in self.ports:
            port.dictionary_setup_stage(comp_setup_dict)
        if comp_setup_dict:
            rootdict[self.label] = comp_setup_dict

    def dictionary_struct_stage(self, rootdict):
        comp_struct_dict = {}
        for port in self.ports:
            port.dictionary_struct_stage(comp_struct_dict)
        if comp_struct_dict:
            rootdict[self.label] = comp_struct_dict

    def dictionary_run_stage(self, rootdict):
        comp_run_dict = {}
        for port in self.ports:
            port.dictionary_run_stage(comp_run_dict)
        if comp_run_dict:
            rootdict[self.label] = comp_run_dict

    @classmethod
    def dictionary_architecture(cls):
        archdict = {}
        setup_stage = {}
        struct_stage = {}
        run_stage = {}
        for comp in cls.components:
            comp.dictionary_setup_stage(setup_stage)
            comp.dictionary_struct_stage(struct_stage)
            comp.dictionary_run_stage(run_stage)
        if setup_stage:
            archdict["setup stage"] = setup_stage
        if struct_stage:
            archdict["structure stage"] = struct_stage
        if run_stage:
            archdict["run stage"] = run_stage
        return archdict
"""
    @classmethod
    def generate_dictionary(cls):
        archdict = {}
        setup_stage = {}
        struct_stage = {}
        for i, comp in enumerate(cls.components):
            comp_setup_dict = {}
            comp_struct_dict = {}

            preset_dict = comp.presets[comp.name]
            comp_setup_dict[preset_dict["actortype"]] = preset_dict["args"]

            for port in comp.ports:
                if port.direction == "out":
                    if port.label == "alert":
                        comp_struct_dict["alert"] = {}
                        for (_, con_port, _) in port.connected_lines:
                            comp_struct_dict["alert"][con_port.component.name + f" {i}"] = ""
                        if not comp_struct_dict["alert"]:
                            del comp_struct_dict["alert"]
                    else:
                        comp_struct_dict["bind"] = {}
                        for (_, con_port, _) in port.connected_lines:
                            comp_struct_dict["bind"][con_port.component.name + f" {i}"] = con_port.label
                        if not comp_struct_dict["bind"]:
                            del comp_struct_dict["bind"]
            if comp_setup_dict:
                setup_stage[comp.name + f" {i}"] = comp_setup_dict
            if comp_struct_dict:
                struct_stage[comp.name + f" {i}"] = comp_struct_dict
        if setup_stage:
            archdict["setup_stage"] = setup_stage
        if struct_stage:
            archdict["structure_stage"] = struct_stage
        return archdict
"""
