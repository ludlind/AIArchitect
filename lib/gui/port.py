import tkinter as tk
from .canvasobject import CanvasObject
#from .component import Component

class Port:

    currently_connecting = None

    def __init__(self, component, label, portdict):
        self.app = component.app
        self.canvas = component.canvas
        self.component = component
        self.label = label
        self.value = ""
        self.direction = portdict["direction"]
        self.fill = portdict["color"]
        self.x, self.y = portdict["x"], portdict["y"]
        self.radius = portdict["radius"]
        self.circle =  component.add_shape(portdict, setTag="port")
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

    def connect(self, target_port, curvex=0, curvey=0):
        line = self.canvas.create_line(self.absx, self.absy,
                                       target_port.absx, target_port.absy,
                                       width=8, fill="darkgrey",
                                       smooth=True, tags="connection")
        self.canvas.tag_lower("connection", "port")
        self.canvas.tag_lower("body", "connection")
        self.canvas.tag_bind(line, "<B1-Motion>", lambda event: cls.line_on_left_hold(event, port=port, line=line))
        self.connected_lines.append((line, target_port, "from", curvex, curvey))
        target_port.connected_lines.append((line, self, "to", curvex, curvey))
        self.update()

    def __del__(self):
        for line, port, _, _, _ in self.connected_lines:
            port._remove_connection_to(self)

    @property
    def absx(self):
        return self.component.x + self.x + self.radius

    @property
    def absy(self):
        return self.component.y + self.y + self.radius

    def update(self):
        for line, target, position, curvex, curvey in self.connected_lines:
            if position == "from":
                self.canvas.coords(line,
                                   self.absx, self.absy,
                                   0.5*(target.absx + self.absx) + curvex,
                                   0.5*(target.absy + self.absy) + curvey,
                                   target.absx, target.absy)
            else:
                self.canvas.coords(line,
                                   self.absx, self.absy,
                                   0.5*(target.absx + self.absx) + curvex,
                                   0.5*(target.absy + self.absy) + curvey,
                                   target.absx, target.absy)

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

    def serialize_setup(self, rootdict):
        port_setup_dict = {}
        if not self.value == "":
            if self.label != "alert" and self.label != "wake":
                if "receive" in rootdict:
                    rootdict["receive"][self.label] = self.value
                else:
                    rootdict["receive"] = {self.label: self.value}

    def serialize_struct(self, rootdict):
        port_struct_dict = {}
        if self.direction == "out":
            if self.label == "alert":
                for (_, con_port, _, _, _) in self.connected_lines:
                    port_struct_dict[con_port.component.label] = ""
                if port_struct_dict:
                    rootdict["alert"] = port_struct_dict
            else:
                for (_, con_port, _, _, _) in self.connected_lines:
                    port_struct_dict[con_port.component.label] = [con_port.label, self.label]
                if port_struct_dict:
                    rootdict["bind"] = port_struct_dict
    
    def serialize_run(self, rootdict):
        if not self.value == "":
            if self.label == "wake":
                rootdict["act"] = ""

    def serialize_canvas(self, portdict):
        conlist = []
        for (_, port, direction, curvex, curvey) in self.connected_lines:
            if direction == "from":
                condict = {}
                condict["target-component"] = port.component.label
                condict["target-port"] = port.label
                condict["curve-x"] = curvex
                condict["curve-y"] = curvey
                conlist.append(condict)
        if conlist:
            portdict[self.label] = conlist
    """
    @classmethod
    def deserailize_canvas(cls, comp, portdict):
        for label, conlist in portdict.items():
            port = None
            for p in comp.ports:
                if p.label == label:
                    port = p
                    break
            if port is None:
                print(f"Port {label} does not exist.")
                continue
            for condict in conlist:
                tcomp = None
                for obj in CanvasObject:
                    if isinstance(obj, Component) and obj.label == condict["target-component"]:
                        tcomp = obj
                        break
                if tcomp is None:
                    print(f"Component {condict['target-component']} does not exist.")
                    continue
                tport = None
                for p in tcomp.ports:
                    if p.label == condict["target-port"]:
                        tport = p
                        break
                if tport is None:
                    print(f"Port {condict['target-port']} does not exits.")
                    continue
                port.connect(tport, curvex=condict["curve-x"], curvey=condict["curve-y"])
    """

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
                        cls.currently_connecting.connect(port)
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
                port.update()
