from typing import Sequence, List, Union, Dict
from types import ModuleType

import os
from os import walk
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

#このデコレータで読み込みの優先順位を付けられます。付けられなかった場合は最後になります。
def priority(pr: int): # type: ignore
    def _priority(cls): # type: ignore
        if (hasattr(cls, 'addon_proc_priority')): raise DuplicateAttributeError("The 'addon_proc_priority' attribute is used in the 'priority' decorator.") # type: ignore
        cls.addon_proc_priority = pr # type: ignore
        return cls # type: ignore
    return _priority # type: ignore

class ProcLoader:
    #登録対象のクラス
    TARGET_CLASSES: object = (
        Operator,
        Panel,
        Menu,
        Preferences,
        PropertyGroup
    )

    def __init__(self, path: str, target_classes: tuple[Union[object, None]]=(None, )) -> None:
        root = dirname(path) if isfile(path) else path #指定されたパスがファイルであれば最後のフォルダまでのパスを取得する
        self.__dir_name = basename(root) #アドオンのフォルダ名       例:addon_folder
        self.__path = dirname(root)      #アドオンフォルダまでのパス 例:path/to/blender/script/

        if target_classes[0] != None: self.TARGET_CLASSES = target_classes #type: ignore

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
        addon_path = join(self.__path, self.__dir_name)

        for dir in dirs:
            for root, _, files in walk(join(addon_path, dir)):
                print(basename(root))
                if basename(root) == '__pycache__': continue
                for file in files:
                    abs_path = join(root, file) #ファイルまでの絶対パスを取得する
                    if not isfile(abs_path) or not abs_path.endswith('.py'): continue #Pythonファイル以外は無視

                    rel_path = abs_path.replace(self.__path, '').lstrip(os.sep) #アドオンフォルダまでのパスを削除する

                    modules.append(splitext(rel_path)[0].replace(os.sep, '.')) #拡張子より左側だけをモジュールの形に変換する

        return modules

    #モジュールをインポートする
    @staticmethod
    def load_modules(paths: List[str]) -> List[ModuleType]:
        return [import_module(mdl) for mdl in paths]

    #モジュール内のクラスを取得する
    @staticmethod
    def load_classes(modules: List[ModuleType]) -> List[object]:
        cls_priority: Dict[object, int] = {}

        for mdl in modules:
            for cls in getmembers(mdl, isclass):
                cls = cls[1]
                #対象のクラスがアドオンのクラスかつ無効でない場合追加する
                if not any(issubclass(cls, c) and not cls == c for c in ProcLoader.TARGET_CLASSES): continue #type: ignore
                if hasattr(cls, 'addon_proc_disabled') and cls.addon_proc_disabled == True: continue # type: ignore

                #優先順位とクラスを辞書に追加する
                if hasattr(cls, 'addon_proc_priority'): cls_priority[cls] = cls.addon_proc_priority #type: ignore
                else: cls_priority[cls] = -1

        #優先順位を元にソートする(数が小さいほど先、-1(0以下)は最後)
        cls_priority = dict(sorted(cls_priority.items(), key=lambda item: float('inf') if item[1] == -1 else item[1]))

        return list(cls_priority.keys())
