from typing import Self, List, Any

from .exceptions import ContextError
from .proc_loader import ProcLoader

from bpy.props import PointerProperty # type: ignore

class PropertiesManager:
    #シングルトンパターン
    def __new__(cls) -> Self:
        if not hasattr(cls ,'_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self.__isInitialized: return
        self.__isInitialized = True

        self.__properties: List[tuple[str, object]] = ([])
        self.__name: str | None = None

    def set_name(self, name: str | None) -> None:
        if self.__name: return
        self.__name = name

    def add(self, prop_type: object, properties: List[tuple[str, object]] | tuple[str, object]) -> List[str]:
        if self.__name == None: raise ContextError('You must add a valid identifier with the "set_name()" method before you can use the "add()" method.')
        #if not issubclass(prop_type, PropertyGroup): raise ValueError('The property class must inherit from "bpy.types.PropertyGroup".')
        if not isinstance(properties, List): properties = [properties] #リストでなければリストにする

        register_name: List[str] = []
        for name, op in properties:
            if ProcLoader.isDisabled(op): continue

            name_with_prefix = f"{self.__name}_{name}"
            setattr(prop_type, name_with_prefix, PointerProperty(type=op)) # プロパティを追加

            register_name.append(name_with_prefix)
            self.__properties.append((name_with_prefix, prop_type))

        return register_name

    def get(self, context: object, attr: str, is_mangling: bool = True) -> Any:
        if self.__name == None: raise ContextError('You must add a valid identifier with the "set_name()" method before you can use the "get()" method.')

        register_name = ""
        if is_mangling and not attr.startswith(self.__name): register_name = f"{self.__name}_{attr}" #修正モードかつ接頭辞がなければ追加する
        else: register_name = attr

        if hasattr(context, register_name): return getattr(context, register_name)

        raise ValueError(f'Property "{attr}" does not exist in {context}.') #属性がないとき


    def delete(self, prop_name: str) -> bool:
        properties = self.__properties.copy() #ループ内でそのオブジェクトの要素数を変更できないのでコピーを作る
        for name, prop_type in properties:
            if not prop_name == name: continue
            delattr(prop_type, name) #プロパティを削除

            try: self.__properties.remove((name, prop_type))
            except ValueError: pass

            return True

        return False

    def unregister(self) -> None:
        for name, prop_type in self.__properties:
            delattr(prop_type, name)

        self.__properties.clear()

    __isInitialized = False # これを付けないとなぜか何回も初期化される