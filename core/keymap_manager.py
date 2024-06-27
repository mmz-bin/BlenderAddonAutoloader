#This program is distributed under the MIT License.
#See the LICENSE file for details.

from dataclasses import dataclass
from typing import Self, List

from .proc_loader import ProcLoader

from bpy import context
from bpy.types import KeyMap, KeyMapItem

#ショートカットキーの情報
@dataclass
class Key:
    """Hold information for registering to the keymap
    """

    operator:     object         #オペレーターのクラスオブジェクト
    key:          str            #対象のキー
    key_modifier: str  = 'NONE'  #追加のキー
    trigger:      str  = 'PRESS' #実行するキーの状態(トリガー)
    #特殊キーの使用の有無
    any:          bool = False   #特殊キーをどれか
    shift:        bool = False
    ctrl:         bool = False
    alt:          bool = False
    oskey:        bool = False

#ショートカットキーを登録する
class KeymapManager:
    """Manage the keymap.
    """

    #シングルトンパターン
    def __new__(cls) -> Self:
        """Always return the same instance.
        """
        if not hasattr(cls ,'_instance'): cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self.__isInitialized: return
        self.__isInitialized = True

        self.__shortcut_keys: List[tuple[KeyMap, KeyMapItem]] = []

    #ショートカットキーを追加する
    def add(self, keys: List[Key] | Key,
            name: str = 'Window', space_type: str = 'EMPTY', region_type: str = 'WINDOW',
            modal: bool = False, tool: bool = False) -> List[tuple[KeyMap, KeyMapItem]]:
        """Add keymaps

        Args:
            keys (List[Key] | Key): Information of key to register.
            name (str, optional): keymap identifier. Defaults to 'Window'.
            space_type (str, optional): keymap's valid space and range. Defaults to 'EMPTY'.
            region_type (str, optional): _description_. Defaults to 'WINDOW'.
            modal (bool, optional): presence of modal modes. Defaults to False.
            tool (bool, optional): presence of tool modes. Defaults to False.

        Returns:
            List[tuple[KeyMap, KeyMapItem]]: Registered key's keymap and keymap items
        """
        if not isinstance(keys, List): keys = [keys] #リストでなければリストにする

        key_config = context.window_manager.keyconfigs.addon #キーコンフィグ

        if not key_config: return [] #キーコンフィグがなければ中止

        shortcut_keys: List[tuple[KeyMap, KeyMapItem]] = [] #今回追加したショートカットキーを入れるリスト

        #指定したロケーションでのキーマップを取得する
        keymap = key_config.keymaps.new(
            name=name, space_type=space_type, region_type=region_type, modal=modal, tool=tool
        )

        for k in keys:
            if ProcLoader.isDisabled(k.operator): continue

            #キーマップにアイテムを追加する
            keymap_item = keymap.keymap_items.new(
                k.operator.bl_idname, k.key, k.trigger, # type: ignore
                key_modifier=k.key_modifier, any=k.any, shift=k.shift, ctrl=k.ctrl, alt=k.alt, oskey=k.oskey
            )

            shortcut_keys.append((keymap, keymap_item))

        self.__shortcut_keys += shortcut_keys

        return shortcut_keys

    def delete(self, subject: tuple[KeyMap, KeyMapItem] | object) -> bool:
        """Delete the keymap.

        Args:
            subject (tuple[KeyMap, KeyMapItem] | object): Pair of keymap and item or operator to be deleted.

        Returns:
            bool: Whether the target for deletion existed or not.
        """

        if type(subject) == tuple:
            try:
                subject[0].keymap_items.remove(subject[1]) #type: ignore
                self.__shortcut_keys.remove(subject) #type: ignore
                return True
            except ValueError:
                return False
        else:
            is_deleted = False
            for keymap, keymap_item in self.__shortcut_keys:
                if not keymap_item.idname == subject.bl_idname: continue  # type: ignore
                keymap.keymap_items.remove(keymap_item)
                is_deleted = True
            return is_deleted

    def unregister(self):
        """Delete all keymaps registered in this class.
        """

        for kms in self.__shortcut_keys:
            self.delete(kms)

        self.__shortcut_keys.clear()

    __isInitialized = False
