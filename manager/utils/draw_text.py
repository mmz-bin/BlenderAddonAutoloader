# pyright: reportUnknownMemberType=false

from typing import Any

from os.path import exists
from bpy.path import abspath # type: ignore
from ..core.utils.gen_msg import MsgType, gen_msg

import bpy
import blf
from bpy.types import SpaceView3D

class DrawText():
    def __init__(self, font_id: int | str | None=None) -> None:
        self.__handler: object | None = None
        self.__font_id: int = 0

        self.__func: object | None = None
        self.__args: tuple[Any, ...] | None = None
        self.__region_type: str | None = None
        self.__draw_type: str | None = None

        if font_id is not None: self.font_id = font_id

    @property
    def font_id(self) -> int: return self.__font_id
    @font_id.setter
    def font_id(self, id_or_path: int | str) -> None:
        if isinstance(id_or_path, int):
            self.__font_id = id_or_path
        else:
            abs_path: str = abspath(id_or_path)
            if not exists(abs_path): raise ValueError(gen_msg(DrawText, MsgType.ERROR, f'Font "{abs_path}" not found.'))
            self.__font_id = blf.load(abs_path)

    @property
    def func(self) -> object | None: return self.__func
    @property
    def args(self) -> tuple[Any, ...] | None: return self.__args
    @property
    def region_type(self) -> str | None: return self.__region_type
    @property
    def draw_type(self) -> str | None: return self.__draw_type

    def is_registered(self) -> bool: return self.__func is not None
    def is_drawing(self) -> bool: return self.__handler is not None

    def draw(self, text: str, pos: tuple[float, float, float], color: tuple[float, float, float, float]=(0.0, 0.0, 0.0, 0.0), size: float=10) -> None:
        """Set the text to use the drawing function.

        Args:
            text (str): Characters to display.
            pos (tuple[float, float, float]): Coordinates to display(x, y, z).
            color (tuple[float, float, float, float], optional): Color to display(red, green, blue, alpha). Defaults to (0.0, 0.0, 0.0, 0.0).
            size (float, optional): Size to display. Defaults to 10.
        """
        blf.position(self.__font_id, pos[0], pos[1], pos[2])
        blf.color(self.__font_id, color[0], color[1], color[2], color[3])
        blf.size(self.__font_id, size)
        blf.draw(self.__font_id, text)


    def display(self, func: object | None=None, args: tuple[Any, ...] | None=None, region_type: str="WINDOW", draw_type: str="POST_PIXEL") -> object | None:
        """Add a drawing function. If previously registered, arguments can be omitted."""
        if func is None:
            if self.__func is None:
                return None
        else:
            self.__func = func
        if args is not None: self.__args = args
        if self.__region_type is None or region_type != self.__region_type: self.__region_type = region_type
        if self.__draw_type is None or draw_type != self.__draw_type: self.__draw_type = draw_type

        self.__handler = SpaceView3D.draw_handler_add(self.__func, (self, ) + self.__args, self.__region_type, self.__draw_type) # type: ignore
        bpy.context.area.tag_redraw()
        return self.__handler

    def erase(self) -> None:
        """Unregister the drawing function."""
        if self.__handler is None: return
        SpaceView3D.draw_handler_remove(self.__handler, self.__region_type)
        self.__handler = None
        bpy.context.area.tag_redraw()

    def clear(self) -> None:
        """Clear saved content."""
        self.erase()
        self.__args = (None, )
        self.__region_type = None
        self.__draw_type = None
