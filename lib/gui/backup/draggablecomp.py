import tkinter as tk
from port import Port

class DraggableComponent:
    
    components = []
    
    def __init__(self, canvas, x, y, width, height, fill, ctrl_pressed, context_menu_callback, on_move):
        self.canvas = canvas
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.fill = fill
        self.rectangle = self.canvas.create_rectangle(self.x, self.y,
                                                      self.x + self.width, self.y + self.height,
                                                      fill=self.fill, outline="")
        self.ctrl_pressed = ctrl_pressed
        self.context_menu_callback = context_menu_callback
        self.ports = []
        self.canvas.tag_bind(self.rectangle, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.rectangle, "<ButtonPress-3>", self.on_right_click)
        self.canvas.tag_bind(self.rectangle, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.rectangle, "<Motion>", lambda event: on_move(event, "draggable"))

    def __del__(self):
        self.canvas.delete(self.rectangle)
        for i, _ in enumerate(self.ports):
            self.ports[i].__del__()
        self.components.remove(self)

    def on_press(self, event):
        if not self.ctrl_pressed.get():
            self.x, self.y = event.x, event.y
    
    def on_drag(self, event):
        if not self.ctrl_pressed.get():
            dx, dy = event.x - self.x, event.y - self.y
            self.canvas.move(self.rectangle, dx, dy)
            
            for port in self.ports:
                port.move(dx, dy)
            
            self.x, self.y = event.x, event.y

    def on_right_click(self, event):
        context_menu = self.context_menu_callback()
        if context_menu is not None:
            context_menu.destroy()
            context_menu = None
        context_menu = tk.Menu(self.canvas, tearoff=0)
        context_menu.add_command(label="Delete", command=lambda: self.__del__() )
        context_menu.post(event.x_root, event.y_root)
        self.context_menu_callback(set=context_menu)

class InputComponent(DraggableComponent):
    def __init__(self, canvas, x, y, *args):
        super().__init__(canvas, x, y, 100, 70, "lightgrey", *args)
        self.ports.append(Port(canvas, "Out", self.x + self.width, self.y + self.height / 2))
        
class TestComponent(DraggableComponent):
    def __init__(self, canvas, x, y, *args):
        super().__init__(canvas, x, y, 50, 50, "blue", *args)
        self.ports.append(Port(canvas, "In", self.x, self.y + self.height / 2))
        self.ports.append(Port(canvas, "Out", self.x + self.width, self.y + self.height / 2))

