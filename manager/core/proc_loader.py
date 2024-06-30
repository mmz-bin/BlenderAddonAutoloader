#This program is distributed under the MIT License.
#See the LICENSE file for details.

# pyright: reportAttributeAccessIssue = false
# pyright: reportUnknownMemberType = false

from typing import Sequence, List, Dict, Set
from types import ModuleType

import os
from os import walk
from os.path import dirname, basename, join, splitext, isfile, exists
from importlib import import_module
from inspect import getmembers, isclass
import sys

from .utils.gen_msg import MsgType, gen_msg
from .exceptions import DuplicateAttributeError

from bpy import types

#このデコレータが付いている場合、そのクラスは無視されます。
def disable(cls: object) -> object:
    if hasattr(cls, 'addon_proc_is_disabled'): raise DuplicateAttributeError("The 'addon_proc_is_disabled' attribute is used in the 'disable' decorator.")
    cls.addon_proc_is_disabled = True
    return cls

#このデコレータで読み込みの優先順位を付けられます。付けられなかった場合は最後になります。
def priority(pr: int):
    def _priority(cls: object):
        if (hasattr(cls, 'addon_proc_priority')): raise DuplicateAttributeError("The 'addon_proc_priority' attribute is used in the 'priority' decorator.")
        cls.addon_proc_priority = pr
        return cls
    return _priority

class ProcLoader:
    """Loads modules and addon classes.

    Attributes:
        DEFAULT_TARGET_CLASSES (object): Default classes for loading

    Raises:
        NotADirectoryError: Throws if the add-on module path is not a folder.
    """

    DEFAULT_TARGET_CLASSES: List[object] = ( # type: ignore
        types.Operator, types.Panel, types.Menu, types.Header, types.UIList, types.PropertyGroup, types.AddonPreferences, types.RenderEngine, types.Node, types.NodeSocket,
        types.NodeTree, types.Gizmo, types.GizmoGroup, types.Macro, types.OperatorFileListElement, types.OperatorProperties, types.Space, types.Region, types.KeyMap, types.KeyMapItem,
        types.RenderSettings, types.Scene, types.Object, types.Mesh, types.Curve, types.MetaBall, types.Text, types.Sound, types.WindowManager, types.Screen,
        types.Brush, types.DynamicPaintSurface, types.DynamicPaintBrushSettings, types.DynamicPaintCanvasSettings, types.ParticleSettings, types.ClothSettings, types.PointCache, types.KeyingSet, types.KeyingSetPath, types.TransformOrientation,
        types.ViewLayer, types.ToolSettings, types.GPencilLayer, types.GPencilFrame, types.GPencilStroke, types.CompositorNode, types.ShaderNode, types.TextureNode, types.NodeLink, types.Material,
        types.World, types.Armature, types.Camera, types.Lattice, types.Texture, types.Histogram, types.Scopes, types.Constraint, types.Modifier, types.RenderLayer,
        types.RenderPass, types.Image, types.MovieClip, types.Mask, types.MaskLayer, types.MovieTrackingSettings, types.MovieTrackingObject, types.MovieTrackingMarker, types.MovieTrackingTrack,
        types.MovieTrackingPlaneMarker, types.MovieTrackingPlaneTrack, types.MovieTrackingStabilization, types.MovieTrackingReconstruction, types.MovieTrackingCamera, types.MovieTrackingDopesheet, types.FCurve, types.Action, types.TimelineMarker, types.Area, types.RegionView3D,
        types.SpaceView3D, types.SpaceImageEditor, types.SpaceUVEditor, types.SpaceTextEditor, types.SpaceGraphEditor, types.SpaceNLA, types.SpaceFileBrowser, types.SpaceProperties, types.SpaceInfo, types.SpaceOutliner,
        types.SpaceSequenceEditor, types.SpaceClipEditor, types.SpaceNodeEditor, types.SpaceConsole, types.SpacePreferences, types.Event, types.Timer, types.AnimData, types.NlaStrip, types.NlaTrack, types.FModifier,
        types.FCurveSample, types.FCurveModifiers, types.CompositorNodeTree, types.ShaderNodeTree, types.TextureNodeTree, types.GeometryNodeTree, types.OperatorMacro
    )

    def __init__(self, path: str, target_classes: List[object] | None = None, is_debug_mode: bool = False) -> None:
        """Initialize and add addon folder to module search path

        Args:
            path (str): Path to the add-on folder
            target_classes (object | None, optional): Type of class to load. Defaults to None.
            is_debug_mode (bool, optional): Presence of debug mode. Defaults to False.
        """
        root = dirname(path) if isfile(path) else path #指定されたパスがファイルであれば最後のフォルダまでのパスを取得する
        self.__dir_name = basename(root) #アドオンのフォルダ名       例:addon_folder
        self.__path = dirname(root)      #アドオンフォルダまでのパス 例:path/to/blender/script/
        self.__is_debug_mode = is_debug_mode

        if target_classes == None: self.__TARGET_CLASSES = self.DEFAULT_TARGET_CLASSES
        else: self.__TARGET_CLASSES = target_classes # type: ignore

        #モジュールの検索パスに登録する
        if self.__path not in sys.path:
            sys.path.append(self.__path)

    @staticmethod
    def isDisabled(clazz: object) -> bool:
        """Check for the presence and value of 'addon_proc_is_disabled' attribute in the target class

        Args:
            clazz (object): Target class

        Returns:
            bool: Whether the target class is marked as disabled
        """
        return hasattr(clazz, 'addon_proc_is_disabled') and clazz.addon_proc_is_disabled == True # type: ignore

    #モジュールとクラスを取得する
    def load(self, dirs: List[str], cat_name: str | None = None) -> List[Sequence[ModuleType | object]]:
        """Load addon's modules and classes

        Args:
            dirs (List[str]): Directory to search
            cat_name (str | None, optional): Default category name applied to the panel. Defaults to None.

        Returns:
            List[Sequence[ModuleType | object]]: Loaded modules and classes(Module in column 0, class in column 1)
        """
        modules = self.load_modules(self.load_files(dirs))
        return [modules, self.load_classes(modules, cat_name)]

    #[アドオン名].[フォルダ名].[ファイル名]の形でモジュール名を取得する
    def load_files(self, dirs: List[str]) -> List[str]:
        """Get path of module to load

        Args:
            dirs (List[str]): Directory to load from

        Returns:
            List[str]: Path of retrieved module
        """
        addon_path = join(self.__path, self.__dir_name) #アドオンへの絶対パス
        return self.__search_target_dirs(dirs, addon_path)

    #モジュールをインポートする
    @staticmethod
    def load_modules(paths: List[str]) -> List[ModuleType]:
        """Load a module based on its path

        Args:
            paths (List[str]): Path to the module

        Returns:
            List[ModuleType]: Loaded module
        """
        for path in paths:
            try:
                import_module(path)
            except (ImportError, ModuleNotFoundError) as e:
                print(gen_msg(ProcLoader, MsgType.ERROR, f'Failed to load "{path}" module. \n {e}'))

        return [import_module(mdl) for mdl in paths]

    #モジュール内のクラスを取得する
    def load_classes(self, modules: List[ModuleType], cat_name: str | None = None) -> List[object]:
        """Retrieve addon class within a module

        Args:
            modules (List[ModuleType]): Target module
            cat_name (str | None, optional): Default category name applied to the panel. Defaults to None.

        Returns:
            List[object]: Loaded classes
        """
        cls_priority: Dict[object, int] = {}

        for mdl in modules:
            for clazz in getmembers(mdl, isclass):
                clazz = clazz[1]
                #対象のクラスがアドオンのクラスかつ無効でない場合追加する
                if not any(issubclass(clazz, c) and not clazz == c for c in self.__TARGET_CLASSES): continue # type: ignore
                if hasattr(clazz, 'addon_proc_is_disabled') and clazz.addon_proc_is_disabled == True: continue

                #優先順位とクラスを辞書に追加する
                if hasattr(clazz, 'addon_proc_priority'): cls_priority[clazz] = clazz.addon_proc_priority
                else: cls_priority[clazz] = -1

        #優先順位を元にソートする(数が小さいほど先、-1(0以下)は最後)
        sorted_classes = sorted(cls_priority.items(), key=lambda item: float('inf') if item[1] < 0 else item[1])

        return self.__add_attribute(sorted_classes, cat_name)

    #検索対象のすべてのフォルダのモジュールを読み込む処理を行う
    def __search_target_dirs(self, dirs: List[str], addon_path: str) -> List[str]:
        """Search sub-folders in all target folders

        Args:
            dirs (List[str]): Target directory
            addon_path (str): Path to the addon folder

        Raises:
            NotADirectoryError: Throws when the target path is not a directory

        Returns:
            List[str]: Loaded modules
        """
        modules: List[str] = []

        for dir in dirs:
            cur_path = join(addon_path, dir)
            if not exists(cur_path) or isfile(cur_path): raise NotADirectoryError(f'"{cur_path}" is not a folder or does not exist.')

            ignore_mdl = self.__read_module_attr(cur_path, 'ignore') #指定したフォルダからの相対パスの形
            if not self.__is_debug_mode: ignore_mdl = ignore_mdl.union(set(('debug', )))
            mdl_root = join(self.__dir_name, dir)            #[アドオンフォルダ]/[現在のフォルダ]

            modules += self.__search_all_sub_dirs(cur_path, mdl_root, dir, ignore_mdl)

        return modules

    #指定したフォルダのサブフォルダをすべて読み込み、無視リストとモジュールを取得する
    def __search_all_sub_dirs(self, cur_path: str, mdl_root: str, dir: str, ignore_mdl: Set[str]) -> List[str]:
        """Recursively search sub-folders of specified folder and retrieve modules

        Args:
            cur_path (str): Path of current directory
            mdl_root (str): Absolute path to [addon folder]/[specified directory]
            dir (str): Parent folder
            ignore_mdl (Set[str]): Modules to ignore in the target folder

        Returns:
            List[str]: Loaded modules
        """
        modules: List[str] = []

        for root, sub_dirs, files in walk(cur_path):
            if basename(root) == '__pycache__': continue #キャシュフォルダはスキップする
            if self.__is_ignore_module(root, dir, ignore_mdl): continue #モジュールが無視リストに入っている場合はスキップ

            ignore_local = self.__get_sub_ignore_folder(root, mdl_root, sub_dirs)

            modules += self.__get_all_modules(root, mdl_root, files, ignore_mdl.union(ignore_local))

        return modules

    #対象のすべてのファイルのモジュールパスを取得する
    def __get_all_modules(self, root: str, mdl_root: str, files: List[str], ignore_mdl: Set[str]) -> List[str]:
        """Retrieve modules in sub-folders.

        Args:
            root (str): Parent directory of file
            mdl_root (str): Absolute path to [addon folder]/[specified directory]
            files (List[str]): Files existing in sub-folders
            ignore_global (Set[str]): Modules to ignore in the target folder
            ignore_local (Set[str]): Modules to ignore in sub-folders only

        Returns:
            List[str]: _description_
        """
        modules: List[str] = []
        for file in files:
            abs_path = join(root, file) #ファイルまでの絶対パスを取得する
            if not isfile(abs_path) or not abs_path.endswith('.py'): continue #Pythonファイル以外は無視
            if file == '__init__.py': continue #初期化ファイルも無視

            mdl = self.__get_module_path(abs_path) #拡張子より左側だけをモジュールの形に変換する

            #アドオンフォルダ名と指定したフォルダ名を削除し、無視リストと比較する
            rel_mdl_path = self.__get_relative_module_path(mdl_root, mdl)
            if not rel_mdl_path in ignore_mdl: modules.append(mdl)

        return modules

    #サブフォルダの__init__.pyファイルから無視リストを取得する
    def __get_sub_ignore_folder(self, root: str, mdl_root: str, sub_dirs: List[str]) -> Set[str]:
        """Get ignore list from subdirectories of specified directory

        Args:
            root (str): Absolute path of parent directory to search
            mdl_root (str): Absolute path to [addon folder]/[specified directory]
            sub_dirs (List[str]): List of subdirectories

        Returns:
            Set[str]: Ignore list (module path)
        """
        ignore_list: Set[str] = set([])
        for sub in sub_dirs:
            abs_path = join(root, sub)
            ignore = set([self.__get_relative_path(join(abs_path, item.replace('.', os.sep))) for item in self.__read_module_attr(abs_path, 'ignore')]) #モジュールパスから相対パスを生成する
            ignore = set([self.__sep_to_period(item) for item in ignore if not basename(item.rstrip(os.sep)) == '__pycache__'])                  #相対パスをモジュールパスに変換し、システムフォルダを除外する
            ignore = set([self.__get_relative_module_path(mdl_root, item) for item in ignore])                                                   #相対モジュールパスを取得する

            ignore_list = ignore_list.union(ignore)

        return set(ignore_list)

    #各ディレクトリの__init__.pyファイルから無視リストを取得する
    def __read_module_attr(self, cur_path: str, identifier: str) -> Set[str]:
        """Retrieve list if 'init.py' exists in sub-folder

        Args:
            cur_path (str): Directory with 'init.py' file

        Returns:
            Set[str]: Modules list
        """
        init_path = join(cur_path, '__init__.py')

        if not exists(init_path): return set([])

        init_mdl = import_module(self.__get_module_path(init_path))
        if hasattr(init_mdl, identifier): return set(init_mdl.ignore)

        return set([])

    def __get_module_path(self, abs_path: str):
        """Convert absolute path to module path"""
        return self.__conv_module_path(self.__get_relative_path(abs_path)) #import_module()関数に使えるモジュールパスを生成する(例：AddonName.operators.mdl)
    def __get_relative_path(self, abs_path: str):
        """Get relative path from add-on folder"""
        return abs_path.replace(self.__path, '').lstrip(os.sep)          #絶対パスを受け取り、アドオンフォルダからの相対パスを取得する
    def __conv_module_path(self, path: str):
        """Transform file path into module path format"""
        return self.__sep_to_period(splitext(path)[0])                        #ファイルパスをモジュールパスの形に変換する

    def __add_attribute(self, classes: List[tuple[object, int]], cat_name: str | None) -> List[object]:
        """Add necessary attributes to the add-on

        Args:
            classes (List[tuple[object, int]]): Target class
            cat_name (str | None): Default category name applied to the panel

        Returns:
            List[object]: Class with added elements
        """
        for cls in classes:
            cls = cls[0]
            if not hasattr(cls, 'bl_idname'): cls.bl_idname = cls.__name__
            if cat_name and issubclass(cls, types.Panel) and not hasattr(cls, 'bl_category'): cls.bl_category = cat_name # type: ignore

        return [item[0] for item in classes]

    @staticmethod
    def __sep_to_period(string: str) -> str:
        """Replace path separators with periods"""
        return string.replace(os.sep, '.')

    @staticmethod
    def __get_relative_module_path(root: str ,path: str):
        """Remove 'root' path from 'path'"""
        return path.lstrip(root.replace(os.sep, '.')).lstrip('.') #アドオンフォルダ名と指定したフォルダ名を削除したモジュールパスを生成する

    #フォルダパスを整形して無視リストと比較する
    def __is_ignore_module(self, root: str, dir: str, ignore_module: Set[str]) -> bool:
        """Transform folder path to module path, compare with ignore list

        Args:
            root (str): Path to the add-on folder
            dir (str): Current parent folder
            ignore_module (Set[str]): Modules to ignore

        Returns:
            bool: Whether to ignore or not
        """
        rel = self.__get_relative_path(root)
        rel_parts = rel.split(os.sep)
        try:
            rel = '.'.join(rel_parts[rel_parts.index(dir)+1:])
        except IndexError:
            rel = ""

        return not rel == "" and rel in ignore_module
