from typing import List, Union, Any, Dict
from types import ModuleType

from .proc_loader import ProcLoader
from .register_shortcuts import RegisterShortcut

from bpy.utils import register_class, unregister_class # type: ignore
from bpy.app import translations

class AddonRegister:
    def __init__(self, path: str, target_dirs: List[str], name: Union[str, None] = None, translation_table: Union[Dict[str, Dict[Any, str]], None] = None) -> None:
        self.__name = name
        self.__modules, self.__classes = ProcLoader(path).load(target_dirs)
        self.__translation_table = translation_table

    def register(self) -> None:
        for cls in self.__classes:
            register_class(cls)

        self.__call('register')

        if self.__translation_table and self.__name: translations.register(self.__name, self.__translation_table) #type: ignore

    def unregister(self) -> None:
        for cls in self.__classes:
            unregister_class(cls)

        self.__call('unregister')

        RegisterShortcut().unregister()
        if self.__translation_table and self.__name: translations.unregister(self.__name)

    def __call(self, identifier: str) -> None:
        for mdl in self.__modules:
            self.__invoke(mdl, identifier)

    def __invoke(self, mdl: ModuleType | object, identifier: str) -> None:
        if hasattr(mdl, identifier): getattr(mdl, identifier)()
