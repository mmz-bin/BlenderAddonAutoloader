class Report:
    ERROR: set[str] = {"ERROR"}
    INFO:  set[str] = {"INFO"}

class Mode:
    EDIT:   str = "EDIT"
    EDIT_MESH: str = "EDIT_MESH"
    EDIT_CURVE: str = "EDIT_CURVE"
    EDIT_SURFACE: str = "EDIT_SURFACE"
    EDIT_TEXT: str = "EDIT_TEXT"
    EDIT_METABALL: str = "EDIT_METABALL"
    EDIT_GPENCIL: str = "EDIT_GPENCIL"
    EDIT_ARMATURE: str = "EDIT_ARMATURE"
    EDIT_LATTICE: str = "EDIT_LATTICE"
    OBJECT: str = "OBJECT"
    SCULPT: str = "SCULPT"
    PAINT_VERTEX: str = "PAINT_VERTEX"
    PAINT_WEIGHT: str = "PAINT_WEIGHT"
    PAINT_TEXTURE: str = "PAINT_TEXTURE"

class ObjectType:
    MESH:     str = "MESH"
    CURVE:    str = "MESH"
    SURFACE:  str = "SURFACE"
    META:     str = "META"
    FONT:     str = "FONT"
    ARMATURE: str = "ARMATURE"
    LATTICE:  str = "LATTICE"
    EMPTY:    str = "EMPTY"
    CAMERA:   str = "CAMERA"
    LIGHT:    str = "LIGHT"
    SPEAKER:  str = "SPEAKER"

class Op:
    FINISHED:      set[str] = {"FINISHED"}
    CANCELLED:     set[str] = {"CANCELLED"}
    RUNNING_MODAL: set[str] = {"RUNNING_MODAL"}
    PASS_THROUGH:  set[str] = {"PASS_THROUGH"}
