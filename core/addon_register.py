from typing import List, Union, Any, Dict
from types import ModuleType

from importlib import reload

from .proc_loader import ProcLoader
from .shortcuts_register import ShortcutsRegister

from bpy.utils import register_class, unregister_class # type: ignore
from bpy.app import translations

class AddonRegister:
    def __init__(self, path: str, target_dirs: List[str], name: Union[str, None] = None,
                 translation_table: Union[Dict[str, Dict[tuple[Any, Any], str]], None] = None, is_debug_mode: bool = False) -> None:
        self.__name = name
        self.__is_debug_mode = is_debug_mode
        self.__modules, self.__classes = ProcLoader(path, is_debug_mode=self.__is_debug_mode).load(target_dirs)
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

        ShortcutsRegister().unregister()
        if self.__translation_table and self.__name: translations.unregister(self.__name)

    def reload(self) -> None:
        if not self.__is_debug_mode or not 'bpy' in locals(): return

        for mdl in self.__modules:
            reload(mdl) # type: ignore

    def __call(self, identifier: str) -> None:
        for mdl in self.__modules:
            self.__invoke(mdl, identifier)

    def __invoke(self, mdl: ModuleType | object, identifier: str) -> None:
        if hasattr(mdl, identifier): getattr(mdl, identifier)()
