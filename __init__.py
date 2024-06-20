from .ProcLoader import ProcLoader

from typing import List
from types import ModuleType

from bpy.utils import register_class, unregister_class # type: ignore

bl_info = {
    "name": "MMZ Add-on",
    "author": "MOMIZI",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Tools > MMZ Add-on",
    "description": "機能詰め合わせ",
    "category": "General",
}

class AddonRegister:

    def __init__(self, path: str, target_dirs: List[str]) -> None:
        self.__modules, self.__classes = ProcLoader(path).load(target_dirs)

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

addon = AddonRegister(__file__, [
    'operators',
    'panels'
])

def register() -> None:
    addon.register()

def unregister() -> None:
    addon.unregister()

if __name__ == '__main__':
    register()
