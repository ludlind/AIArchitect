import tkinter as tk
from tkinter import ttk
from tkinter import Tk, BooleanVar, N, S, E, W, Y, X, BOTH, LEFT, RIGHT, TOP, Menu, Canvas, filedialog, Text
from tkinter import Frame, Label, Scrollbar, PanedWindow, Entry, StringVar

from port import Port
from component import Component
import json
import sys

class InfoDisplay(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.scrollbar = Scrollbar(self, orient="vertical")
        self.canvas = Canvas(self, bd=0, highlightthickness=0,
                             yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.canvas.yview)
        self.canvas.grid_rowconfigure(0,weight=1)
        self.canvas.grid_columnconfigure(0,weight=1)
        self.canvas.grid_columnconfigure(1,weight=1)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        self.interior = interior = Frame(self.canvas)
        interior_id = self.canvas.create_window(0, 0, window=interior, anchor=N+W)

        self.widgets = []
        self.rowcol0 = 0
        self.rowcol1 = 0
        self.font = "Arial 12"

        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                self.canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                self.canvas.itemconfigure(interior_id, width=self.canvas.winfo_width())
        self.canvas.bind('<Configure>', _configure_canvas)
    
    def clear(self):
        for widget in self.widgets:
            widget.destroy()
        self.widgets.clear()
        self.rowcol0 = 0
        self.rowcol1 = 0

    def addLabel(self, text):
        lb = Label(self.interior, text=text, font=self.font)
        lb.grid(row=self.rowcol0, column=0)
        self.rowcol0 += 1
        self.widgets.append(lb)
    
    def addEntry(self, callback):
        sv = StringVar()
        en = Entry(self.interior, font=self.font, textvariable=sv)
        en.bind('<FocusOut>', lambda: callback(sv))
        en.grid(row=self.rowcol0, column=1)
        self.rowcol1 += 1
        self.widgets.append(en)

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

        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        self.paned_window = PanedWindow(self, orient="horizontal")
        self.paned_window.grid(row=0, column=0, columnspan=2, sticky=N+S+E+W)

        self.sideframe = Frame(self, background="darkgray")
        self.text = Label(self.sideframe, text = "Name", background="darkgray", font="Arial 15 bold")
        self.text.pack(side="top", padx=30, pady=10, fill=X)
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

    def load_components_from_file(self, filename):
        with open(filename, "r") as f:
            self.compdict = json.load(f)
        Component.loadPresets(self.compdict)

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
            Component.clear_selection()
            self.selection = self.canvas.create_rectangle(self.click_x, self.click_y,
                                                          self.click_x, self.click_y,
                                                          outline="red", fill="")
            
    def on_canvas_left_release(self, event):
        if self.selection is not None:
            Component.clear_selection()
            for comp in Component.components:
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
            for label in Component.presets.keys():
                def cmd(label=label):
                    Component.components.append(
                        Component(self,
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
        component.display_info()

    def generate_architecture_dictionary(self):
        archdict = {}
        setup_stage = {}
        struct_stage = {}
        for i, comp in enumerate(Component.components):
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
