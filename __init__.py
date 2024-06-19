from .ProcLoader import ProcLoader

from typing import List
from types import ModuleType

from bpy.utils import register_class, unregister_class # type: ignore

bl_info = {
    "name": "Add-on",
    "author": "MOMIZI",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Tools > Add-on",
    "description": "",
    "category": "General",
}

print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

class RegisterAddon:
    TARGET_DIRS: List[str] = [
        'operators',
        'panels'
    ]

    def __init__(self, path: str) -> None:
        self.__modules, self.__classes = ProcLoader(path).load(RegisterAddon.TARGET_DIRS)

    def register(self) -> None:
        for cls in self.__classes:
            register_class(cls)

        self.__call('register')

    def unregister(self) -> None:
        for cls in self.__classes:
            unregister_class(cls)

        self.__call('unregister')

    def __call(self, identifier: str) -> None:
        for mdl in self.__modules:
            self.__invoke(mdl, identifier)

    def __invoke(self, mdl: ModuleType | object, identifier: str) -> None:
        if hasattr(mdl, identifier): getattr(mdl, identifier)()

addon = RegisterAddon(__file__)

def register() -> None:
    addon.register()

def unregister() -> None:
    addon.unregister()

if __name__ == '__main__':
    register()
