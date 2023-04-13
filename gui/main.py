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



def on_ctrl_key(event, canvas, ctrl_pressed):
    ctrl_pressed.set(True)

def on_ctrl_key_release(event, canvas, ctrl_pressed):
    ctrl_pressed.set(False)

def on_canvas_left_click(event, canvas, ctrl_pressed):
    global context_menu
    if context_menu is not None:
        context_menu.destroy()
        context_menu = None
    if ctrl_pressed.get():
        canvas.scan_mark(event.x, event.y)

def on_canvas_left_hold(event, canvas, ctrl_pressed):
    if ctrl_pressed.get():
        canvas.scan_dragto(event.x, event.y, gain=1)

def on_canvas_right_click(event, canvas, ctrl_pressed, on_move):
    global context_menu
    if not canvas.find_overlapping(event.x - 1, event.y - 1, event.x + 1, event.y + 1):
        if context_menu is not None:
            context_menu.destroy()
            context_menu = None
        context_menu = tk.Menu(canvas, tearoff=0)
        for label, Component in component_types.items():
            def cmd(Cmp=Component):
                DraggableComponent.components.append(Cmp(canvas, event.x, event.y, ctrl_pressed, context_menu_callback, on_move))
            context_menu.add_command(label=label, command=cmd)
        context_menu.post(event.x_root, event.y_root)

def on_closing(root, canvas):
    for comp in DraggableComponent.components.copy():
        comp.__del__()
    canvas.destroy()
    root.destroy()

def main():
    root = tk.Tk()
    root.title("Flow-Based Problem Solver")

    ctrl_pressed = tk.BooleanVar(value=False)

    canvas = tk.Canvas(root, bg="white", scrollregion=(0, 0, 2000, 2000))
    canvas.pack(fill=tk.BOTH, expand=True)
    
    text = canvas.create_text(30,10,fill="Black",font="Arial 15 bold", text="Text")

    #canvas.bind("<Motion>", lambda event: on_move(event, canvas, text))
    canvas.bind("<Button-3>", lambda event: on_canvas_right_click(event, canvas, ctrl_pressed, lambda event, name: on_move(event, canvas, text, name)))
    canvas.bind("<ButtonPress-1>", lambda event: on_canvas_left_click(event, canvas, ctrl_pressed))
    canvas.bind("<B1-Motion>", lambda event: on_canvas_left_hold(event, canvas, ctrl_pressed))
    root.bind("<Control_L>", lambda event: on_ctrl_key(event, canvas, ctrl_pressed))
    root.bind("<KeyRelease-Control_L>", lambda event: on_ctrl_key_release(event, canvas, ctrl_pressed))
    root.bind("<Control_R>", lambda event: on_ctrl_key(event, canvas, ctrl_pressed))
    root.bind("<KeyRelease-Control_R>", lambda event: on_ctrl_key_release(event, canvas, ctrl_pressed))

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, canvas))

    root.mainloop()

if __name__ == "__main__":
    main()

