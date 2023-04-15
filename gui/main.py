import tkinter as tk
from tkinter import ttk
from tkinter import Tk, BooleanVar, N, S, E, W, Y, X, BOTH, LEFT, RIGHT, TOP, Menu, Canvas, filedialog, Text
from tkinter import Frame, Label, Scrollbar, PanedWindow

from port import Port
from draggablecomp import DraggableComponent
import json
import sys

class Application(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.geometry("500x400+300+300")
        self.canvas = None
        self.text = None
        self.shift_pressed = None
        self.ctrl_pressed = None
        self.context_menu = None
        self.menubar = None
        self.compdict = {}
        self.selection = None
    
    def create(self):
        self.title("AI Architect")
        
        self.shift_pressed = BooleanVar(value=False)
        self.ctrl_pressed = BooleanVar(value=False)

        self.create_menubar()

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.paned_window = PanedWindow(self, orient="horizontal")
        self.paned_window.grid(row=0, column=0, columnspan=2, sticky=N+S+E+W)

        self.sideframe = Frame(self, background="darkgray")
        self.text = Label(self.sideframe, text = "Name", background="darkgray", font="Arial 15 bold")
        self.text.pack(side="top", padx=30, pady=10, fill=X)
        self.infoframe = Frame(self.sideframe)
        self.infoframe.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
        myscrollbar = Scrollbar(self.infoframe, orient="vertical")
        myscrollbar.pack(side=RIGHT, fill=Y)
        self.canvas = Canvas(self, bg="white", scrollregion=(0, 0, 2000, 2000))

        self.paned_window.add(self.sideframe)
        self.paned_window.add(self.canvas)

        #canvas.bind("<Motion>", lambda event: on_move(event, canvas, text))
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_left_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_left_release)
        self.canvas.bind("<B1-Motion>", self.on_canvas_left_hold)
        self.bind("<Control_L>", self.on_ctrl_key)
        self.bind("<KeyRelease-Control_L>", self.on_ctrl_key_release)
        self.bind("<Control_R>", self.on_ctrl_key)
        self.bind("<KeyRelease-Control_R>", self.on_ctrl_key_release)
        self.bind("<Shift_L>", self.on_shift_key)
        self.bind("<KeyRelease-Shift_L>", self.on_shift_key_release)
        self.bind("<Shift_R>", self.on_shift_key)
        self.bind("<KeyRelease-Shift_R>", self.on_shift_key_release)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_menubar(self):
        self.menubar = Menu(self)
        self.config(menu=self.menubar)
        fileMenu = Menu(self.menubar)
        fileMenu.add_command(label="Exit", command=self.on_closing)
        fileMenu.add_command(label="Open", command=self.open_file)
        fileMenu.add_command(label="Save", command=self.save_file)
        self.menubar.add_cascade(label="File", menu=fileMenu)

    #def destroy_info(self):
    #    for widget in self.infoframe.winfo_children():
    #        widget.destroy()

    def load_components_from_file(self, filename):
        with open(filename, "r") as f:
            self.compdict = json.load(f)
        DraggableComponent.loadPresets(self.compdict)

    def save_architecture_to_file(self, filename, archdict):
        with open(filename, "w") as f:
            json.dump(archdict, f, indent=4)

    def selection_destroy(self):
        self.canvas.delete(self.selection)
        self.selection = None

    def open_file(self):
        name = filedialog.askopenfilename()
        self.load_components_from_file(name)

    def save_file(self):
        name = filedialog.asksaveasfilename(initialfile = 'Untitled.json',
                                            defaultextension=".json",
                                            filetypes=[("All Files","*.*"),("JavaScript Object Notation","*.json")])
        archdict = self.generate_architecture_dictionary()
        self.save_architecture_to_file(name, archdict)

    def on_ctrl_key(self, event):
        self.ctrl_pressed.set(True)

    def on_ctrl_key_release(self, event):
        self.ctrl_pressed.set(False)

    def on_shift_key(self, event):
        self.shift_pressed.set(True)

    def on_shift_key_release(self, event):
        self.shift_pressed.set(False)

    def on_canvas_left_click(self, event):
        self.click_x, self.click_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        if self.context_menu is not None:
            self.context_menu.destroy()
            self.context_menu = None
        if self.shift_pressed.get():
            self.canvas.scan_mark(event.x,
                                  event.y)
        elif not self.canvas.find_overlapping(self.canvas.canvasx(event.x) - 1,
                                              self.canvas.canvasy(event.y) - 1,
                                              self.canvas.canvasx(event.x) + 1,
                                              self.canvas.canvasy(event.y) + 1):
            if self.selection is not None:
                self.selection_destroy()
            DraggableComponent.clear_selection()
            self.selection = self.canvas.create_rectangle(self.click_x, self.click_y,
                                                          self.click_x, self.click_y,
                                                          outline="red", fill="")
            
    def on_canvas_left_release(self, event):
        if self.selection is not None:
            DraggableComponent.clear_selection()
            for comp in DraggableComponent.components:
                inx = (self.click_x - comp.x)*(self.canvas.canvasx(event.x) - comp.x) < 0
                iny = (self.click_y - comp.y)*(self.canvas.canvasy(event.y) - comp.y) < 0
                if inx and iny:
                    DraggableComponent.select(comp)
            self.selection_destroy()

    def on_canvas_left_hold(self, event):
        if self.shift_pressed.get():
            self.canvas.scan_dragto(event.x,
                                    event.y,
                                    gain=1)
        if self.selection is not None:
            self.canvas.coords(self.selection,
                               self.click_x, self.click_y,
                               self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def on_canvas_right_click(self, event):
        if not self.canvas.find_overlapping(self.canvas.canvasx(event.x) - 1,
                                            self.canvas.canvasy(event.y) - 1,
                                            self.canvas.canvasx(event.x) + 1,
                                            self.canvas.canvasy(event.y) + 1):
            if self.context_menu is not None:
                self.context_menu.destroy()
                self.context_menu = None
            self.context_menu = Menu(self.canvas,
                                   tearoff=0)
            for label in DraggableComponent.presets.keys():
                def cmd(label=label):
                    DraggableComponent.components.append(
                        DraggableComponent(self,
                                           self.canvas.canvasx(event.x),
                                           self.canvas.canvasy(event.y),
                                           label)
                    )
                self.context_menu.add_command(label=label, command=cmd)
            self.context_menu.post(event.x_root,
                                   event.y_root)

    def on_closing(self):
        self.quit()

    def on_click_component(self, component):
        self.text.config(text=component.name)

    def generate_architecture_dictionary(self):
        archdict = {}
        setup_stage = {}
        struct_stage = {}
        for i, comp in enumerate(DraggableComponent.components):
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


def main():
    app = Application()
    app.create()
    app.mainloop()

if __name__ == "__main__":
    main()
