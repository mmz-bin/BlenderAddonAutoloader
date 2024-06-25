from typing import List, Any, Dict
from types import ModuleType

from importlib import reload

from .proc_loader import ProcLoader
from .keymap_manager import KeymapManager
from .properties_manager import PropertiesManager

from bpy.utils import register_class, unregister_class # type: ignore
from bpy.app import translations

class AddonManager:
    """This class in charge of registering and deregistering add-ons.
    """

    def __init__(self, path: str, target_dirs: List[str], addon_name: str | None = None,
                 translation_table: Dict[str, Dict[tuple[Any, Any], str]] | None = None, cat_name: str | None = None, is_debug_mode: bool = False) -> None:
        """Initialize

        Args:
            path (str): Path to the add-on folder or '__init__.py' file.
            target_dirs (List[str]): The name of the directory to be read.
            addon_name (str | None, optional): Add-on name. Required when using translation tables or properties. Defaults to None.
            translation_table (Dict[str, Dict[tuple[Any, Any], str]] | None, optional): Standard format translation table of Blender. Defaults to None.
            cat_name (str | None, optional): 'bl_category' attribute that is assigned by default to subclasses of 'bpy.types.Panel'. Defaults to None.
            is_debug_mode (bool, optional): Presence or absence of debug mode. Defaults to False.
        """
        self.__addon_name = addon_name
        self.__is_debug_mode = is_debug_mode
        self.__modules, self.__classes = ProcLoader(path, is_debug_mode=self.__is_debug_mode).load(target_dirs, cat_name)
        PropertiesManager().set_name(self.__addon_name)
        self.__translation_table = translation_table

        self.reload()

    def register(self) -> None:
        """Perform registration of the add-on class and each function
        """
        for cls in self.__classes:
            register_class(cls)

        self.__call('register')

        if self.__translation_table and self.__addon_name: translations.register(self.__addon_name, self.__translation_table) #type: ignore

    def unregister(self) -> None:
        """Unregister the add-on class and each function
        """
        for cls in self.__classes:
            unregister_class(cls)

        self.__call('unregister')

        KeymapManager().unregister()
        PropertiesManager().unregister()
        if self.__translation_table and self.__addon_name: translations.unregister(self.__addon_name)

    def reload(self) -> None:
        """ Reload the add-on class when the 'script.reload' operator is called
        """
        if not self.__is_debug_mode or not 'bpy' in locals(): return

        for mdl in self.__modules:
            reload(mdl) # type: ignore

    def __call(self, identifier: str) -> None:
        """Invoke the function specified by 'identifier' for all add-on modules.

        Args:
            identifier (str): The name of the function you want to call
        """
        for mdl in self.__modules:
            self.__invoke(mdl, identifier)

    def __invoke(self, mdl: ModuleType | object, identifier: str) -> None:
        """If 'mdl' module has a function named 'identifier', invoke it.

        Args:
            mdl (ModuleType | object): Module from which to call function
            identifier (str): Name of the function to call
        """
        if hasattr(mdl, identifier): getattr(mdl, identifier)()
