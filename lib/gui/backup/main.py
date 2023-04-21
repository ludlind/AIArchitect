import tkinter as tk

from port import Port
from draggablecomp import DraggableComponent, TestComponent, InputComponent

context_menu = None
def context_menu_callback(set=None):
    global context_menu
    if set is not None:
        context_menu = set
    return context_menu

def on_move(event, canvas, text, name):
    canvas.itemconfigure(text, text=name)

component_types = {
        "Test": TestComponent,
        "Input": InputComponent,
}




class Application:

    def __init__(self):
        self.root = None
        self.canvas = None
        self.text = None
        self.ctrl_pressed = None
    
    def create(self):
        self.root = tk.Tk()
        self.root.title("Flow-Based Problem Solver")
        
        self.ctrl_pressed = tk.BooleanVar(value=False)

        self.canvas = tk.Canvas(self.root, bg="white", scrollregion=(0, 0, 2000, 2000))
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.text = self.canvas.create_text(30,10,fill="Black",font="Arial 15 bold", text="Text")

        #canvas.bind("<Motion>", lambda event: on_move(event, canvas, text))
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_left_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_left_hold)
        self.root.bind("<Control_L>", self.on_ctrl_key)
        self.root.bind("<KeyRelease-Control_L>", self.on_ctrl_key_release)
        self.root.bind("<Control_R>", self.on_ctrl_key)
        self.root.bind("<KeyRelease-Control_R>", self.on_ctrl_key_release)

        self.root.protocol("WM_DELETE_WINDOW", lambda: self.on_closing())

        self.root.mainloop()

    def on_ctrl_key(self, event):
        self.ctrl_pressed.set(True)

    def on_ctrl_key_release(self, event):
        self.ctrl_pressed.set(False)

    def on_canvas_left_click(self, event):
        global context_menu
        if context_menu is not None:
            context_menu.destroy()
            context_menu = None
        if self.ctrl_pressed.get():
            self.canvas.scan_mark(event.x,
                                  event.y)

    def on_canvas_left_hold(self, event):
        if self.ctrl_pressed.get():
            self.canvas.scan_dragto(event.x,
                                    event.y,
                                    gain=1)

    def on_canvas_right_click(self, event):
        global context_menu
        if not self.canvas.find_overlapping(event.x - 1,
                                            event.y - 1,
                                            event.x + 1,
                                            event.y + 1):
            if context_menu is not None:
                context_menu.destroy()
                context_menu = None
            context_menu = tk.Menu(self.canvas,
                                   tearoff=0)
            for label, Component in component_types.items():
                def cmd(Cmp=Component):
                    DraggableComponent.components.append(Cmp(self.canvas,
                                                             event.x,
                                                             event.y,
                                                             self.ctrl_pressed,
                                                             context_menu_callback,
                                                             lambda event, name: on_move(event, self.canvas, self.text, name)))
                context_menu.add_command(label=label,
                                         command=cmd)
            context_menu.post(event.x_root,
                              event.y_root)

    def on_closing(self):
        for comp in DraggableComponent.components.copy():
            comp.__del__()
        self.canvas.destroy()
        self.root.destroy()

if __name__ == "__main__":
    app = Application()
    app.create()

