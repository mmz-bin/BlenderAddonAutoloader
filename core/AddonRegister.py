from typing import List
from types import ModuleType

from .ProcLoader import ProcLoader

from bpy.utils import register_class, unregister_class # type: ignore

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
