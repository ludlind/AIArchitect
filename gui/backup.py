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
        
        self.text = Label(parent, text = "Name", background="darkgray", font="Arial 15 bold")
        self.text.pack(side="top", padx=30, pady=10, fill=X)
        
        self.canvas = Canvas(self)
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.interior = Frame(self.canvas)
        self.interior.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.interior, anchor=N+W)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.pack()
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.interior.grid_rowconfigure(0,weight=1)
        self.interior.grid_columnconfigure(0,weight=1)
        self.interior.grid_columnconfigure(1,weight=1)

        self.widgets = []
        self.rowcol0 = 0
        self.rowcol1 = 0
        self.font = "Arial 12"

    def clear(self):
        for widget in self.widgets:
            widget.destroy()
        self.widgets.clear()
        self.rowcol0 = 0
        self.rowcol1 = 0

    def addLabel(self, text):
        lb = Label(self.interior, text=text, font=self.font)
        lb.grid(row=self.rowcol0, column=0, sticky=N+E+W, pady=1, padx=1)
        self.rowcol0 += 1
        self.widgets.append(lb)
    
    def addEntry(self, text, callback):
        sv = StringVar()
        en = Entry(self.interior, font=self.font, textvariable=sv)
        en.insert(0, text)
        en.bind("<Return>", (lambda event: callback(en.get())))
        en.bind('<FocusOut>', lambda event: callback(en.get()))
        en.grid(row=self.rowcol1, column=1, sticky=N+E+W, pady=1, padx=(1, 0))
        self.rowcol1 += 1
        self.widgets.append(en)

    def setTitle(self, text):
        self.text.config(text=text)

"""
class InfoDisplay(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.text = Label(parent, text = "Name", background="darkgray", font="Arial 15 bold")
        self.text.pack(side="top", padx=30, pady=10, fill=X)
        
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
        lb.grid(row=self.rowcol0, column=0, sticky=N+E+W, pady=1, padx=1)
        self.rowcol0 += 1
        self.widgets.append(lb)
    
    def addEntry(self, text, callback):
        sv = StringVar()
        en = Entry(self.interior, font=self.font, textvariable=sv)
        en.insert(0, text)
        en.bind("<Return>", (lambda event: callback(en.get())))
        en.bind('<FocusOut>', lambda event: callback(en.get()))
        en.grid(row=self.rowcol1, column=1, sticky=N+E+W, pady=1, padx=(1, 0))
        self.rowcol1 += 1
        self.widgets.append(en)

    def setTitle(self, text):
        self.text.config(text=text)
"""
