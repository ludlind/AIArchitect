import tkinter as tk
from port import Port

def mix_colors(root, color1, color2, mix):
    rgb1 = root.winfo_rgb(color1)
    rgb2 = root.winfo_rgb(color2)
    rgb_mix = (int(mix*rgb1[0] + (1-mix)*rgb2[0]),
               int(mix*rgb1[1] + (1-mix)*rgb2[1]),
               int(mix*rgb1[2] + (1-mix)*rgb2[2]))
    return "#%02x%02x%02x" % rgb_mix

class Component:

    presets = {}
    components = []
    selected_components = []

    def selected(self):
        return self in self.selected_components
    
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

    def __init__(self, app, x, y, preset):
        self.app = app
        self.canvas = self.app.canvas
        self.x, self.y = x, y
        self.start_x, self.start_y = x, y
        self.width, self.height = 0, 0
        self.fill = ""
        self.name = ""
        self.rectangle = None
        self.ports = []
        self.loadPreset(preset)
        self.canvas.tag_bind(self.rectangle, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.rectangle, "<ButtonRelease-1>", self.on_release)
        self.canvas.tag_bind(self.rectangle, "<ButtonPress-3>", self.on_right_click)
        self.canvas.tag_bind(self.rectangle, "<B1-Motion>", self.on_drag)

    def __del__(self):
        self.canvas.delete(self.rectangle)
        for i, _ in enumerate(self.ports):
            self.ports[i].__del__()
        self.components.remove(self)

    def on_press(self, event):
        if not self.app.shift_pressed.get():
            if self.app.ctrl_pressed.get():
                if self.selected():
                    self.unselect(self)
                else:
                    self.select(self)
            else:
                if not self.selected():
                    self.select_only(self)
                self.app.on_click_component(self)

    def display_info(self):
        infodisp = self.app.infodisp
        infodisp.clear()
        infodisp.addLabel("Name")
        def set_name(sv, self=self):
            self.name = sv.get()
        infodisp.addEntry(set_name)
        infodisp.addLabel("Type")
   
    

    def on_drag(self, event):
        if not self.app.shift_pressed.get():
            dx, dy = self.canvas.canvasx(event.x) - self.app.click_x, self.canvas.canvasy(event.y) - self.app.click_y
            for comp in self.selected_components:
                comp.move(dx, dy)
    
    def on_release(self, event):
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
        


    @classmethod
    def loadPresets(cls,
                    compdict: str):
        for label, presetdict in compdict["component-presets"].items():
            cls.presets[label] = presetdict

    def loadPreset(self,
                   label: str):
        preset = self.presets[label]
        self.fill = preset["color"]
        self.name = label
        self.width = preset["width"]
        self.height = preset["height"]
        self.rectangle = self.canvas.create_rectangle(self.x, self.y,
                                                      self.x + self.width, self.y + self.height,
                                                      fill=self.fill, outline="")
        for name, portdict in preset["ports"].items():
            port = Port(self.app, self, name, portdict, self.x, self.y)
            self.ports.append(port)
