import tkinter as tk

class Port:

    currently_connecting = None

    def __init__(self, app, component, label, portdict, x, y):
        self.app = app
        self.canvas = app.canvas
        self.component = component
        self.label = label
        self.value = ""
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
        for i, (line, port, position, _, _) in enumerate(self.connected_lines):
            if port is target_port:
                del self.connected_lines[i]
                if line in self.canvas.find_all():
                    self.canvas.delete(line)
    
    def remove_connection(self, target_port):
        self._remove_connection_to(target_port)
        target_port._remove_connection_to(self)

    def __del__(self):
        self.canvas.delete(self.circle)
        for line, port, _, _, _ in self.connected_lines:
            port._remove_connection_to(self)

    @property
    def absx(self):
        return self.component.x + self.x

    @property
    def absy(self):
        return self.component.y + self.y

    def move(self):
        self.canvas.moveto(self.circle, self.absx - self.radius, self.absy - self.radius)
        for line, target, position, curvex, curvey in self.connected_lines:
            if position == "from":
                self.canvas.coords(line,
                                   self.absx, self.absy,
                                   0.5*(target.absx + self.absx) + curvex, 0.5*(target.absy + self.absy) + curvey,
                                   target.absx, target.absy)
            else:
                self.canvas.coords(line,
                                   self.absx, self.absy,
                                   0.5*(target.absx + self.absx) + curvex, 0.5*(target.absy + self.absy) + curvey,
                                   target.absx, target.absy)
                #self.canvas.coords(line, target.absx, target.absy,
                #                   target.absx + curvex, target.absy + curvey,
                #                   self.absx, self.absy)

    def display_info(self):
        infodisp = self.app.infodisp
        infodisp.setTitle(self.label)
        infodisp.clear()
        infodisp.addLabel("Label")
        def set_label(txt, self=self):
            self.label = txt
            self.display_info()
        infodisp.addEntry(self.label, set_label)
        if self.label == "wake":
            infodisp.addLabel("Wake at start (1, 2, ...)")
            def set_run_order(txt, self=self):
                if txt == "" or txt.isnumeric():
                    self.value = txt
                else:
                    self.value = ""
                self.display_info()
            infodisp.addEntry(self.value, set_run_order)
        elif self.label != "alert":
            infodisp.addLabel("Value")
            def set_value(txt, self=self):
                self.value = txt
                self.display_info()
            infodisp.addEntry(self.value, set_value)

    def dictionary_setup_stage(self, rootdict):
        port_setup_dict = {}
        if not self.value == "":
            if self.label != "alert" and self.label != "wake":
                if "receive" in rootdict:
                    rootdict["receive"][self.label] = self.value
                else:
                    rootdict["receive"] = {self.label: self.value}

    def dictionary_struct_stage(self, rootdict):
        port_struct_dict = {}
        if self.direction == "out":
            if self.label == "alert":
                for (_, con_port, _, _, _) in self.connected_lines:
                    port_struct_dict[con_port.component.label] = ""
                if port_struct_dict:
                    rootdict["alert"] = port_struct_dict
            else:
                for (_, con_port, _, _, _) in self.connected_lines:
                    port_struct_dict[con_port.component.label] = con_port.label
                if port_struct_dict:
                    rootdict["bind"] = port_struct_dict
    
    def dictionary_run_stage(self, rootdict):
        if not self.value == "":
            if self.label == "wake":
                rootdict["act"] = ""

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
                                                  width=8, fill="darkgrey",
                                                  smooth=True)
                        cls.currently_connecting.canvas.tag_bind(line, "<B1-Motion>",
                                                                 lambda event: cls.line_on_left_hold(event,
                                                                                                     port=port,
                                                                                                     line=line))
                        cls.currently_connecting.connected_lines.append((line, port, "from", 0, 0))
                        port.connected_lines.append((line, cls.currently_connecting, "to", 0, 0))
                if cls.currently_connecting is not None:
                    canvas.itemconfig(cls.currently_connecting.circle, fill=cls.currently_connecting.fill)
                    cls.currently_connecting = None

    def line_on_left_hold(event, port, line):
        canvas = port.canvas
        for i, (ln, pt, lb, _, _) in enumerate(port.connected_lines):
            if ln is line:
                x = canvas.canvasx(event.x) - 0.5*(port.absx + pt.absx)
                y = canvas.canvasy(event.y) - 0.5*(port.absy + pt.absy)
                port.connected_lines[i] = (ln, pt, lb, x, y)
                for j, (ln2, pt2, lb2, _, _) in enumerate(pt.connected_lines):
                    if ln2 is line:
                        pt.connected_lines[j] = (ln2, pt2, lb2, x, y)
                port.move()
