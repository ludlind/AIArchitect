from .canvasobject import CanvasObject
from .component import Component

def serialize_architecture():
    archdict = {}
    setup = {}
    struct = {}
    run = {}
    for obj in CanvasObject.objects:
        if isinstance(obj, Component):
            obj.serialize_setup(setup)
            obj.serialize_struct(struct)
            obj.serialize_run(run)
        else:
            pass
    if setup:
        archdict["setup"] = setup
    if struct:
        archdict["structure"] = struct
    if run:
        archdict["run"] = run
    return archdict

def serialize_canvas():
    canvasdict = {}
    for obj in CanvasObject.objects:
        obj.serialize_canvas(canvasdict)
    return {"component": canvasdict}

def deserialize_canvas(app, canvasdict):
    for label, compdict in canvasdict.items():
        if label == "component":
            Component.deserialize_canvas(app, compdict)
