import tkinter as tk

class Port:

    currently_connecting = None

    def __init__(self, app, component, label, portdict, x, y):
        self.app = app
        self.canvas = app.canvas
        self.component = component
        self.label = label
        if self.label == "alert":
            self.fill = "red"
        elif self.label == "wake":
            self.fill = "red"
        else:
            self.fill = "blue"
        self.radius = 8
        self.direction = portdict["direction"]
        self.x, self.y = portdict["x"], portdict["y"]
        self.circle = self.canvas.create_oval(x + self.x - self.radius, y + self.y - self.radius,
                                              x + self.x + self.radius, y + self.y + self.radius,
                                              fill=self.fill, outline="")
        self.connected_lines = []
        self.canvas.tag_bind(self.circle, "<Button-1>", lambda event: self.on_left_click(event, self.canvas, self))


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
        for line, port, _ in self.connected_lines:
            port._remove_connection_to(self)

    @property
    def absx(self):
        return self.component.x + self.x

    @property
    def absy(self):
        return self.component.y + self.y

    def move(self):
        self.canvas.moveto(self.circle, self.absx - self.radius, self.absy - self.radius)
        for line, target, position  in self.connected_lines:
            if position == "from":
                self.canvas.coords(line, self.absx, self.absy, *self.canvas.coords(line)[2:])
            else:
                self.canvas.coords(line, *self.canvas.coords(line)[:2], self.absx, self.absy)

    def display_info(self):
        infodisp = self.app.infodisp
        infodisp.setTitle(self.label)
        infodisp.clear()
        infodisp.addLabel("Label")
        infodisp.addLabel("Direction")
        def set_label(txt, self=self):
            self.label = txt
            self.display_info()
        def set_dir(txt, self=self):
            self.direction = txt
            self.display_info()
        infodisp.addEntry(self.label, set_label)
        infodisp.addEntry(self.direction, set_dir)

    @classmethod
    def on_left_click(cls, event, canvas, port):
        if True:
            port.display_info()
            if cls.currently_connecting is None:
                cls.currently_connecting = port
                canvas.itemconfig(cls.currently_connecting.circle, fill = "cyan")
            else:
                if cls.currently_connecting is not port:
                    connection_exists = False
                    for conln in cls.currently_connecting.connected_lines:
                        if port is conln[1]:
                            cls.currently_connecting.remove_connection(port)
                            connection_exists = True
                    if not connection_exists:
                        line = canvas.create_line(cls.currently_connecting.absx, cls.currently_connecting.absy,
                                                  port.absx, port.absy,
                                                  width=3, fill="darkgrey")
                        cls.currently_connecting.connected_lines.append((line, port, "from"))
                        port.connected_lines.append((line, cls.currently_connecting, "to"))
                if cls.currently_connecting is not None:
                    canvas.itemconfig(cls.currently_connecting.circle, fill=cls.currently_connecting.fill)
                    cls.currently_connecting = None
