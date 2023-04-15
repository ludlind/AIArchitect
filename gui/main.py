import tkinter as tk
from tkinter import ttk
from tkinter import Tk, Frame, Menu, Canvas, Label, filedialog, Text, Scrollbar

from port import Port
from draggablecomp import DraggableComponent
import json
import sys
import argparse

class Application(Frame):

    def __init__(self):
        super().__init__()
        self.canvas = None
        self.text = None
        self.shift_pressed = None
        self.ctrl_pressed = None
        self.context_menu = None
        self.menubar = None
        self.compdict = {}
        self.selection = None
    
    def create(self):
        self.master.title("AI Architect")
        
        self.shift_pressed = tk.BooleanVar(value=False)
        self.ctrl_pressed = tk.BooleanVar(value=False)

        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=2)

        self.sideframe = Frame(self.master, background="darkgray", width=300)
        self.sideframe.pack(fill=tk.Y, side=tk.LEFT)
        self.text = Label(self.sideframe, text = "Name", background="darkgray", font="Arial 15 bold")
        self.text.pack(side="top", padx=30, pady=10, fill=tk.X)
        #self.text.place(relx=0.5,anchor=tk.N)
        self.infoframe = Frame(self.sideframe)
        self.infoframe.pack(side=tk.TOP, fill=tk.BOTH, padx=5, pady=5, expand=True)
        myscrollbar = Scrollbar(self.infoframe, orient="vertical")
        myscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        #text= Label(frame, text= "Register", font= ('Helvetica bold', 14))
        #text.pack(pady=20)
        #self.sideframe.pack(fill=tk.BOTH, side=tk.LEFT)

        self.canvas = Canvas(self.master, bg="white", scrollregion=(0, 0, 2000, 2000))
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.create_menubar()

        #canvas.bind("<Motion>", lambda event: on_move(event, canvas, text))
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_left_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_left_release)
        self.canvas.bind("<B1-Motion>", self.on_canvas_left_hold)
        self.master.bind("<Control_L>", self.on_ctrl_key)
        self.master.bind("<KeyRelease-Control_L>", self.on_ctrl_key_release)
        self.master.bind("<Control_R>", self.on_ctrl_key)
        self.master.bind("<KeyRelease-Control_R>", self.on_ctrl_key_release)
        self.master.bind("<Shift_L>", self.on_shift_key)
        self.master.bind("<KeyRelease-Shift_L>", self.on_shift_key_release)
        self.master.bind("<Shift_R>", self.on_shift_key)
        self.master.bind("<KeyRelease-Shift_R>", self.on_shift_key_release)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_menubar(self):
        self.menubar = Menu(self.master)
        self.master.config(menu=self.menubar)
        fileMenu = Menu(self.menubar)
        fileMenu.add_command(label="Exit", command=self.on_closing)
        fileMenu.add_command(label="Open", command=self.open_file)
        self.menubar.add_cascade(label="File", menu=fileMenu)

    def load_file(self, filename):
        with open(filename, "r") as f:
            self.compdict = json.load(f)
        DraggableComponent.loadPresets(self.compdict)

    def selection_destroy(self):
        self.canvas.delete(self.selection)
        self.selection = None

    def open_file(self):
        name = filedialog.askopenfilename()
        self.load_file(name)

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
            print(DraggableComponent.selected_components)

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
            self.context_menu = tk.Menu(self.canvas,
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
        #for comp in DraggableComponent.components.copy():
        #    comp.__del__()
        #self.canvas.destroy()
        self.quit()

    def context_menu_callback(self, set=None):
        if set is not None:
            self.context_menu = set
        return self.context_menu

    def on_click_component(self, component):
        self.text.config(text=component.name)

def main():
    root = tk.Tk()
    root.geometry("500x400+300+300")
    app = Application()
    app.create()
    root.mainloop()

if __name__ == "__main__":
    main()
