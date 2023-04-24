import tkinter as tk
from tkinter import ttk
from tkinter import Tk, BooleanVar, N, S, E, W, Y, X, BOTH, LEFT, RIGHT, TOP, Menu, Canvas, filedialog, Text
from tkinter import Frame, Label, Scrollbar, PanedWindow, Entry, StringVar

from ..architecture import *
from ..architecture import LLMActor
from .serializer import serialize_architecture, serialize_canvas, deserialize_canvas

from .infodisplay import InfoDisplay
from .port import Port
from .component import Component
import json
import yaml
import sys

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class Application(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.geometry("500x400+300+300")
        self.include_files = ["presets/preset.yaml"]
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

        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        self.paned_window = PanedWindow(self, orient="horizontal")
        self.paned_window.grid(row=0, column=0, columnspan=1, sticky=N+S+E+W)
        #self.paned_window.pack(side=LEFT, fill=BOTH)

        self.sideframe = Frame(self, background="darkgray")
        self.infodisp = InfoDisplay(self.sideframe)
        self.infodisp.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
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
        runMenu = Menu(self.menubar)
        runMenu.add_command(label="Run", command=lambda: self.run_dictionary(False))
        runMenu.add_command(label="Debug", command=lambda: self.run_dictionary(True))
        self.menubar.add_cascade(label="Run", menu=runMenu)

    def load_from_file(self, filename):
        with open(filename, "r") as f:
            self.compdict = yaml.load(f, Loader=Loader)
            f.close()
        if "component-presets" in self.compdict:
            Component.loadPresets(self.compdict["component-presets"])
        if "canvas" in self.compdict:
            deserialize_canvas(self, self.compdict["canvas"])

    def save_dictionary_to_file(self, filename, dictionary):
        with open(filename, "w") as f:
            yaml.dump(dictionary, f, Dumper=Dumper)

    def selection_destroy(self):
        self.canvas.delete(self.selection)
        self.selection = None

    def open_file(self):
        name = filedialog.askopenfilename()
        self.load_from_file(name)

    def save_file(self):
        name = filedialog.asksaveasfilename(initialfile = 'Untitled.yaml',
                                            defaultextension=".yaml",
                                            filetypes=[("All Files","*.*"),("YAML","*.yaml")])
        dictionary = {}
        dictionary["architecture"] = serialize_architecture()
        dictionary["include"] = self.include_files
        dictionary["canvas"] = serialize_canvas()
        self.save_dictionary_to_file(name, dictionary)

    def run_dictionary(self, debug):
        for incfilename in self.include_files:
            archiload.loadFile(incfilename, debug)
        dictionary = {}
        dictionary["architecture"] = serialize_architecture()
        dictionary["include"] = self.include_files
        if "llmactor-presets" in dictionary:
            LLMActor.loadPresets(dictionary)
        if "architecture" in dictionary:
            archiload.debugmes("\nBuild Order:", 0, debug)
            archiload.loadArch(dictionary, debug=debug)

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
            Component.clear_selection()
            self.selection = self.canvas.create_rectangle(self.click_x, self.click_y,
                                                          self.click_x, self.click_y,
                                                          outline="red", fill="")
            
    def on_canvas_left_release(self, event):
        if self.selection is not None:
            Component.clear_selection()
            for comp in Component.objects:
                inx = (self.click_x - comp.x)*(self.canvas.canvasx(event.x) - comp.x) < 0
                iny = (self.click_y - comp.y)*(self.canvas.canvasy(event.y) - comp.y) < 0
                if inx and iny:
                    Component.select(comp)
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
            categories = {}
            for presetdict in Component.presets.values():
                if presetdict["type"] in categories:
                    if categories[presetdict["type"]] is self.context_menu:
                        submenu = Menu(self.context_menu, tearoff=0)
                        categories[presetdict["type"]] = submenu
                        self.context_menu.add_cascade(label=presetdict["type"], menu=submenu)
                else:
                    categories[presetdict["type"]] = self.context_menu
            for label, presetdict in Component.presets.items():
                def cmd(label=label):
                    Component(self,
                              self.canvas.canvasx(event.x),
                              self.canvas.canvasy(event.y),
                              label)
                categories[presetdict["type"]].add_command(label=label, command=cmd)
            self.context_menu.post(event.x_root,
                                   event.y_root)

    def on_closing(self):
        self.quit()

def main():
    app = Application()
    for filename in app.include_files:
        app.load_from_file(filename)
    app.create()
    app.mainloop()

if __name__ == "__main__":
    main()
