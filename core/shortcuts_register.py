from dataclasses import dataclass

from typing import Self, Any, List, Union

from bpy import context
from bpy.types import KeyMap, KeyMapItem

#ショートカットキーの情報
@dataclass
class Key:
    bl_idname:    str            #オペレーターのbl_idname
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
class ShortcutsRegister:
    #シングルトンパターン
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        if not hasattr(cls ,'_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs) # type: ignore
        return cls._instance

    def __init__(self):
        self.__shortcut_keys: List[tuple[KeyMap, KeyMapItem]] = []

    #ショートカットキーを追加する
    def add(self, keys: Union[List[Key], Key],
            name: str = 'Window', space_type: str = 'EMPTY', region_type: str = 'WINDOW',
            modal: bool = False, tool: bool = False) -> List[tuple[KeyMap, KeyMapItem]]:
        if not isinstance(keys, List): keys = [keys] #リストでなければリストにする

        key_config = context.window_manager.keyconfigs.addon #キーコンフィグ

        if not key_config: return [] #キーコンフィグがなければ中止

        shortcut_keys: List[tuple[KeyMap, KeyMapItem]] = [] #今回追加したショートカットキーを入れるリスト

        #指定したロケーションでのキーマップを取得する
        keymap = key_config.keymaps.new(
            name=name, space_type=space_type, region_type=region_type, modal=modal, tool=tool
        )

        for k in keys:
            #キーマップにアイテムを追加する
            keymap_item = keymap.keymap_items.new(
                k.bl_idname, k.key, k.trigger,
                key_modifier=k.key_modifier, any=k.any, shift=k.shift, ctrl=k.ctrl, alt=k.alt, oskey=k.oskey
            )

            shortcut_keys.append((keymap, keymap_item))

        self.__shortcut_keys += shortcut_keys

        return shortcut_keys


    def delete(self, km: KeyMap, kmi: KeyMapItem) -> bool:
        try:
            km.keymap_items.remove(kmi)
            self.__shortcut_keys.remove((km, kmi))
        except ValueError:
            return False

        return True

    def unregister(self):
        for keymap, keymap_item in self.__shortcut_keys:
            self.delete(keymap, keymap_item)

        self.__shortcut_keys.clear()
