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
        #self.interior = Frame(self.canvas)
        self.interior = PanedWindow(self.canvas, orient="horizontal")
        self.interior_labels = PanedWindow(self.interior, orient="vertical")
        self.interior_entries = PanedWindow(self.interior, orient="vertical")
        self.interior.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        canvas_frame = self.canvas.create_window((0, 0), window=self.interior, anchor=N+W)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        def at_resize(event):
            canvas = self.canvas
            min_width = self.interior.winfo_reqwidth()
            min_height = self.interior.winfo_reqheight()
            if min_width < event.width:
                canvas.itemconfigure(canvas_frame, width=event.width)
            if min_height < event.height:
                canvas.itemconfigure(canvas_frame, height=event.height)

            canvas.configure(scrollregion=canvas.bbox("all"))

        self.canvas.bind(
            "<Configure>",
            at_resize
        )

        self.pack()
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        #self.interior.grid_columnconfigure(0,weight=1)
        #self.interior.grid_columnconfigure(1,weight=1)

        self.interior.pack(side=TOP, fill=BOTH, expand=True)
        #self.interior.add(self.interior_labels)
        #self.interior.add(self.interior_entries)
        self.interior_labels.pack(side=LEFT, fill=Y)
        self.interior_entries.pack(side=RIGHT, fill=BOTH, expand=True)

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
        lb = Label(self.interior_labels, text=text, font=self.font)
        lb.pack(side=TOP, fill=X, padx=1, pady=1)
        self.rowcol0 += 1
        self.widgets.append(lb)
    
    def addEntry(self, text, callback):
        sv = StringVar()
        en = Entry(self.interior_entries, font=self.font, textvariable=sv)
        en.insert(0, text)
        en.bind("<Return>", (lambda event: callback(en.get())))
        en.bind('<FocusOut>', lambda event: callback(en.get()))
        en.pack(side=TOP, fill=X, padx=1, pady=1)
        self.rowcol1 += 1
        self.widgets.append(en)

    def setTitle(self, text):
        self.text.config(text=text)

"""
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
"""
