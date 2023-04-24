import tkinter as tk
from abc import ABC, abstractmethod

class CanvasObject(ABC):

    objects = []
    selected_objects = []

    def __init__(self, app, x, y):
        self.app = app
        self.canvas = self.app.canvas
        self.x, self.y = x, y
        self.start_x, self.start_y = x, y
        self.shapes = []
        self.objects.append(self)

    def add_shape(self, param, setTag=None):
        shapetype = param["shape"]
        x = param["x"]
        y = param["y"]
        fill = param["color"] if "color" in param else ""
        if shapetype == "rectangle":
            width = param["width"]
            height = param["height"]
            shape = self.canvas.create_rectangle(
                    self.x + x, self.y + x,
                    self.x + x + width, self.y + x + height,
                    fill=fill, outline="")
        elif shapetype == "circle":
            radius = param["radius"]
            shape = self.canvas.create_oval(
                    self.x + x, self.y + y,
                    self.x + x + 2*radius, self.y + y + 2*radius,
                    fill=fill, outline="")
        else:
            return None
        if setTag is not None:
            self.canvas.addtag_withtag(setTag, shape)
        self.shapes.append((shape, x, y))
        self.canvas.tag_bind(shape, "<ButtonPress-1>", self.on_left_click)
        self.canvas.tag_bind(shape, "<B1-Motion>", self.on_left_hold)
        self.canvas.tag_bind(shape, "<ButtonRelease-1>", self.on_left_release)
        self.canvas.tag_bind(shape, "<ButtonPress-3>", self.on_right_click)
        return shape


    def __del__(self):
        for (shape, _, _) in self.shapes:
            self.canvas.delete(shape)
        self.objects.remove(self)

    @abstractmethod
    def display_info(self):
        pass

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
            for obj in self.selected_objects:
                obj.move(dx, dy)
    
    def on_left_release(self, event):
        for obj in self.selected_objects:
            obj.start_x, obj.start_y = obj.x, obj.y

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
        for (shape, x, y) in self.shapes:
            self.canvas.moveto(shape, self.x + x, self.y + y)

    def delete_selected(self):
        if self.selected_objects and self.selected():
            self.unselect(self)
            for obj in self.selected_objects:
                obj.__del__()
            self.clear_selection()
            self.__del__()
        elif not self.selected():
            self.__del__()

    def selected(self):
        return self in self.selected_objects
    
    @classmethod
    def select(cls, obj):
        cls.selected_objects.append(obj)
        cls.update_selected()

    @classmethod
    def unselect(cls, obj):
        cls.selected_objects.remove(obj)
        cls.update_selected()

    @classmethod
    def clear_selection(cls):
        cls.selected_objects.clear()
        cls.update_selected()

    @classmethod
    def select_only(cls, obj):
        cls.selected_objects.clear()
        cls.selected_objects.append(obj)
        cls.update_selected()

    @classmethod
    def update_selected(cls):
        for obj in cls.objects:
            if obj.selected():
                for (shape, _, _) in obj.shapes:
                    obj.canvas.itemconfig(shape, outline="green")

            else:
                for (shape, _, _) in obj.shapes:
                    obj.canvas.itemconfig(shape, outline="")
