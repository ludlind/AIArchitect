import tkinter as tk

currently_connecting = None

def on_port_click(event, canvas, port):
    global currently_connecting
    if currently_connecting is None and isinstance(port, OutputPort):
        currently_connecting = port
        currently_connecting.fill = "cyan"
        canvas.itemconfig(currently_connecting.circle, fill = "cyan")
    else:
        if isinstance(currently_connecting, OutputPort) and isinstance(port, InputPort):
            line = canvas.create_line(currently_connecting.x, currently_connecting.y,
                                      port.x, port.y,
                                      width=3, fill="darkgrey")
            currently_connecting.connected_lines.append((line, "start"))
            port.connected_lines.append((line, "end"))
        if currently_connecting is not None:
            currently_connecting.fill = "green"
            canvas.itemconfig(currently_connecting.circle, fill = "green")
            currently_connecting = None

class InputPort:
    def __init__(self, canvas, x, y, radius=8, fill="red"):
        self.canvas = canvas
        self.x, self.y = x, y
        self.radius = radius
        self.fill = fill
        self.circle = self.canvas.create_oval(self.x - self.radius, self.y - self.radius,
                                              self.x + self.radius, self.y + self.radius,
                                              fill=self.fill, outline="")
        self.connected_lines = []

        self.canvas.tag_bind(self.circle, "<Button-1>", lambda event: on_port_click(event, canvas, self))

class OutputPort:
    def __init__(self, canvas, x, y, radius=8, fill="green"):
        self.canvas = canvas
        self.x, self.y = x, y
        self.radius = radius
        self.fill = fill
        self.circle = self.canvas.create_oval(self.x - self.radius, self.y - self.radius,
                                              self.x + self.radius, self.y + self.radius,
                                              fill=self.fill, outline="")
        self.connected_lines = []

        self.canvas.tag_bind(self.circle, "<Button-1>", lambda event: on_port_click(event, canvas, self))


class DraggableComponent:
    def __init__(self, canvas, x, y, width, height, fill, ctrl_pressed):
        self.canvas = canvas
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.fill = fill
        self.rectangle = self.canvas.create_rectangle(self.x, self.y,
                                                      self.x + self.width, self.y + self.height,
                                                      fill=self.fill, outline="")
        self.input_port = InputPort(canvas, self.x, self.y + self.height / 2)
        self.output_port = OutputPort(canvas, self.x + self.width, self.y + self.height / 2)
        self.ctrl_pressed = ctrl_pressed

        self.canvas.tag_bind(self.rectangle, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.rectangle, "<B1-Motion>", self.on_drag)

    def on_press(self, event):
        if not self.ctrl_pressed.get():
            self.x, self.y = event.x, event.y

    def on_drag(self, event):
        if not self.ctrl_pressed.get():
            dx, dy = event.x - self.x, event.y - self.y
            self.canvas.move(self.rectangle, dx, dy)
            
            if self.input_port is not None:
                self.input_port.x += dx
                self.input_port.y += dy
                self.canvas.move(self.input_port.circle, dx, dy)
                
                for line, position in self.input_port.connected_lines:
                    if position == "start":
                        self.canvas.coords(line, self.input_port.x + dx, self.input_port.y + dy, *self.canvas.coords(line)[2:])
                    else:
                        self.canvas.coords(line, *self.canvas.coords(line)[:2], self.input_port.x + dx, self.input_port.y + dy)
            
            if self.output_port is not None:
                self.output_port.x += dx
                self.output_port.y += dy
                self.canvas.move(self.output_port.circle, dx, dy)
            
                for line, position in self.output_port.connected_lines:
                    if position == "start":
                        self.canvas.coords(line, self.output_port.x + dx, self.output_port.y + dy, *self.canvas.coords(line)[2:])
                    else:
                        self.canvas.coords(line, *self.canvas.coords(line)[:2], self.output_port.x + dx, self.output_port.y + dy)

            self.x, self.y = event.x, event.y

class InputComponent(DraggableComponent):
    def __init__(self, canvas, x, y, width, height, fill, ctrl_pressed):
        self.canvas = canvas
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.fill = "lightgrey"
        self.rectangle = self.canvas.create_rectangle(self.x, self.y,
                                                      self.x + self.width, self.y + self.height,
                                                      fill=self.fill, outline="")
        self.input_port = None
        self.output_port = OutputPort(canvas, self.x + self.width, self.y + self.height / 2)
        self.ctrl_pressed = ctrl_pressed

        self.canvas.tag_bind(self.rectangle, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.rectangle, "<B1-Motion>", self.on_drag)

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

def create_component(canvas, x, y, component_type, fill, ctrl_pressed):
    if component_type == "Input":
        component = InputComponent(canvas, x, y, 100, 70, fill, ctrl_pressed)
    else:
        component = DraggableComponent(canvas, x, y, 50, 50, fill, ctrl_pressed)
    #component.component_type = component_type

def on_canvas_right_click(event, canvas, ctrl_pressed):
    context_menu = tk.Menu(canvas, tearoff=0)
    context_menu.add_command(label="Component", command=lambda: create_component(canvas, event.x, event.y, "Component", "blue", ctrl_pressed))
    context_menu.add_command(label="Input", command=lambda: create_component(canvas, event.x, event.y, "Input", "", ctrl_pressed))

    # Display the context menu
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

