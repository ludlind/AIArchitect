import tkinter as tk

currently_connecting = None
components = []
context_menu = None

def on_port_click(event, canvas, port):
    global currently_connecting
    if currently_connecting is None:
        currently_connecting = port
        canvas.itemconfig(currently_connecting.circle, fill = "cyan")
    else:
        if currently_connecting is not port:
            line = canvas.create_line(currently_connecting.x, currently_connecting.y,
                                      port.x, port.y,
                                      width=3, fill="darkgrey")
            currently_connecting.connected_lines.append((line, port, "from"))
            port.connected_lines.append((line, currently_connecting, "to"))
        if currently_connecting is not None:
            canvas.itemconfig(currently_connecting.circle, fill=currently_connecting.fill)
            currently_connecting = None

class Port:
    def __init__(self, canvas, label, x, y, radius=8, fill="red"):
        self.canvas = canvas
        self.label = label
        self.x, self.y = x, y
        self.radius = radius
        self.fill = fill
        self.circle = self.canvas.create_oval(self.x - self.radius, self.y - self.radius,
                                              self.x + self.radius, self.y + self.radius,
                                              fill=self.fill, outline="")
        self.connected_lines = []
        self.canvas.tag_bind(self.circle, "<Button-1>", lambda event: on_port_click(event, canvas, self))

    def _remove_connection_to(self, target_port):
        for i, (line, port, position) in enumerate(self.connected_lines):
            if port is target_port:
                del self.connected_lines[i]
                if line in self.canvas.find_all():
                    self.canvas.delete(line)
    
    def remove_connection(self, target_port):
        self._remove_connection_to(target_port)
        target_port._remove_connection_to(self)

    def __del__(self):
        self.canvas.delete(self.circle)
        
        for line, port in self.connected_lines:
            port._remove_connection_to(self)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.canvas.move(self.circle, dx, dy)
        for line, target, position  in self.connected_lines:
            if position == "from":
                self.canvas.coords(line, self.x + dx, self.y + dy, *self.canvas.coords(line)[2:])
            else:
                self.canvas.coords(line, *self.canvas.coords(line)[:2], self.x + dx, self.y + dy)

class DraggableComponent:
    def __init__(self, canvas, x, y, width, height, fill, ctrl_pressed):
        self.canvas = canvas
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.fill = fill
        self.rectangle = self.canvas.create_rectangle(self.x, self.y,
                                                      self.x + self.width, self.y + self.height,
                                                      fill=self.fill, outline="")
        self.ctrl_pressed = ctrl_pressed
        self.ports = []
        self.canvas.tag_bind(self.rectangle, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.rectangle, "<ButtonPress-3>", self.on_right_click)
        self.canvas.tag_bind(self.rectangle, "<B1-Motion>", self.on_drag)

    def __del__(self):
        global components
        self.canvas.delete(self.rectangle)
        for i in range(len(self.ports)):
            del self.ports[i]
        del self.ports
        components.remove(self)

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
        global context_menu
        if context_menu is not None:
            context_menu.destroy()
            context_menu = None
        context_menu = tk.Menu(self.canvas, tearoff=0)
        context_menu.add_command(label="Delete", command=lambda: self.__del__() )
        context_menu.post(event.x_root, event.y_root)

class InputComponent(DraggableComponent):
    def __init__(self, canvas, x, y, ctrl_pressed):
        super().__init__(canvas, x, y, 100, 70, "lightgrey", ctrl_pressed)
        self.ports.append(Port(canvas, "Out", self.x + self.width, self.y + self.height / 2))
        
class TestComponent(DraggableComponent):
    def __init__(self, canvas, x, y, ctrl_pressed):
        super().__init__(canvas, x, y, 50, 50, "blue", ctrl_pressed)
        self.ports.append(Port(canvas, "In", self.x, self.y + self.height / 2))
        self.ports.append(Port(canvas, "Out", self.x + self.width, self.y + self.height / 2))

component_types = {
        "Test": TestComponent,
        "Input": InputComponent,
}

def on_ctrl_key(event, canvas, ctrl_pressed):
    ctrl_pressed.set(True)
def on_ctrl_key_release(event, canvas, ctrl_pressed):
    ctrl_pressed.set(False)
def on_canvas_pan_start(event, canvas, ctrl_pressed):
    if ctrl_pressed.get():
        canvas.scan_mark(event.x, event.y)
def on_canvas_pan_move(event, canvas, ctrl_pressed):
    if ctrl_pressed.get():
        canvas.scan_dragto(event.x, event.y, gain=1)
def on_canvas_right_click(event, canvas, ctrl_pressed):
    global context_menu
    global components
    if not canvas.find_overlapping(event.x - 1, event.y - 1, event.x + 1, event.y + 1):
        if context_menu is not None:
            context_menu.destroy()
            context_menu = None
        context_menu = tk.Menu(canvas, tearoff=0)
        for label, Component in component_types.items():
            def cmd(Cmp=Component):
                components.append(Cmp(canvas, event.x, event.y, ctrl_pressed))
            context_menu.add_command(label=label, command=cmd)
        context_menu.post(event.x_root, event.y_root)

def main():
    root = tk.Tk()
    root.title("Flow-Based Problem Solver")

    ctrl_pressed = tk.BooleanVar(value=False)

    canvas = tk.Canvas(root, bg="white", scrollregion=(0, 0, 2000, 2000))
    canvas.pack(fill=tk.BOTH, expand=True)

    canvas.bind("<Button-3>", lambda event: on_canvas_right_click(event, canvas, ctrl_pressed))
    canvas.bind("<ButtonPress-1>", lambda event: on_canvas_pan_start(event, canvas, ctrl_pressed))
    canvas.bind("<B1-Motion>", lambda event: on_canvas_pan_move(event, canvas, ctrl_pressed))
    root.bind("<Control_L>", lambda event: on_ctrl_key(event, canvas, ctrl_pressed))
    root.bind("<KeyRelease-Control_L>", lambda event: on_ctrl_key_release(event, canvas, ctrl_pressed))
    root.bind("<Control_R>", lambda event: on_ctrl_key(event, canvas, ctrl_pressed))
    root.bind("<KeyRelease-Control_R>", lambda event: on_ctrl_key_release(event, canvas, ctrl_pressed))

    root.mainloop()

if __name__ == "__main__":
    main()

