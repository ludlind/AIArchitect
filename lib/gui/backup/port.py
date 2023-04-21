import tkinter as tk

class Port:

    currently_connecting = None

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
        self.canvas.tag_bind(self.circle, "<Button-1>", lambda event: self.on_port_click(event, canvas, self))

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

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.canvas.move(self.circle, dx, dy)
        for line, target, position  in self.connected_lines:
            if position == "from":
                self.canvas.coords(line, self.x + dx, self.y + dy, *self.canvas.coords(line)[2:])
            else:
                self.canvas.coords(line, *self.canvas.coords(line)[:2], self.x + dx, self.y + dy)

    @classmethod
    def on_port_click(cls, event, canvas, port):
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
                    line = canvas.create_line(cls.currently_connecting.x, cls.currently_connecting.y,
                                              port.x, port.y,
                                              width=3, fill="darkgrey")
                    cls.currently_connecting.connected_lines.append((line, port, "from"))
                    port.connected_lines.append((line, cls.currently_connecting, "to"))
            if cls.currently_connecting is not None:
                canvas.itemconfig(cls.currently_connecting.circle, fill=cls.currently_connecting.fill)
                cls.currently_connecting = None
