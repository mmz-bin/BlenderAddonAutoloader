from typing import Sequence, List, Union
from types import ModuleType

from os import listdir
from os.path import dirname, basename, join, splitext, isfile
from importlib import import_module
from inspect import getmembers, isclass
import sys

from bpy.types import Operator, Panel, Menu, Preferences, PropertyGroup

class DuplicateAttributeError(Exception):
    pass

#このデコレータが付いている場合、そのクラスは無視されます。
def disable(cls: object) -> object:
    if hasattr(cls, 'addon_proc_disabled'): raise DuplicateAttributeError("The 'addon_proc_disabled' attribute is used in the 'disable' decorator.")
    cls.addon_proc_disabled = True # type: ignore
    return cls

class ProcLoader:
    #登録対象のクラス
    TARGET_CLASSES = (
        Operator,
        Panel,
        Menu,
        Preferences,
        PropertyGroup
    )

    def __init__(self, path: str) -> None:
        root = dirname(path) if isfile(path) else path #指定されたパスがファイルであれば最後のフォルダまでのパスを取得する
        self.__dir_name = basename(root) #アドオンフォルダまでのパス 例:path/to/blender/script/addon_folder
        self.__path = dirname(root)      #アドオンのフォルダ名       例:addon_folder

        #モジュールの検索パスに登録する
        if self.__path not in sys.path:
            sys.path.append(self.__path)

    #モジュールとクラスを取得する
    def load(self, dirs: List[str]) -> List[Sequence[Union[ModuleType, object]]]:
        modules = self.load_modules(self.load_files(dirs))
        return [modules, self.load_classes(modules)]

    #[アドオン名].[フォルダ名].[ファイル名]の形でモジュール名を取得する
    def load_files(self, dirs: List[str]) -> List[str]:
        modules: List[str] = []

        for dir in dirs:
            path = join(self.__path, self.__dir_name, dir)
            for mdl in listdir(path):
                #パスがファイルかつ.pyファイルの場合、文字列を整形してリストに追加する
                if not isfile(join(path, mdl)) or not mdl.endswith('.py'): continue
                modules.append(f"{self.__dir_name}.{dir}.{splitext(mdl)[0]}")

        return modules

    #モジュールをインポートする
    @staticmethod
    def load_modules(paths: List[str]) -> List[ModuleType]:
        return [import_module(mdl) for mdl in paths]

    #モジュール内のクラスを取得する
    @staticmethod
    def load_classes(modules: List[ModuleType]) -> List[object]:
        classes: List[object] = []

        for mdl in modules:
            for cls in getmembers(mdl, isclass):
                cls = cls[1]
                #対象のクラスがアドオンのクラスかつ無効でない場合追加する
                if not any(issubclass(cls, c) and not cls == c for c in ProcLoader.TARGET_CLASSES): continue
                if hasattr(cls, 'addon_proc_disabled') and cls.addon_proc_disabled == True: continue # type: ignore
                classes.append(cls)

        return classes
