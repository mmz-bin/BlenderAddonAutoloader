This library uses English that has been machine-translated from Japanese.

__[The English readme is here](README.md)__

# __このスクリプトは開発中のため、破壊的な変更が加えられる可能性があります。__

# Blender_Add-on_Autoloader
Blenderアドオンを構成するファイルの動的な登録・解除を実現するスクリプトです。
クラスの登録・解除・無効化・優先順位付け・ショートカットキーの登録といった面倒な作業を自動で行うことができます。
Blender 4.1で動作確認しています。

__注意：coreディレクトリ内部にある3つのファイル(addon_register.py, shortcuts_register.py, proc_loader.py)は同じディレクトリに配置してください。__

## 機能
- サブディレクトリを含めて、指定したディレクトリ内のすべてのアドオンのクラスを登録・解除します。
- 各ディレクトリの`__init__.py`に`ignore`という名前のリストを定義し、モジュール名を記述することでそのモジュールを無視します。
    - モジュールのパスはリストが定義されている`__init__.py`ファイルが存在するディレクトリから見た相対パスです。
        - 例(`operators`フォルダ内の`__init__.py`ファイルの場合): `ignore = ['your_operator']`
- [`disable`](#proc_loaderpy)デコレータを使うことで特定のクラスを無視することができます。
    - 例: `@disable`
- [`priority`](#proc_loaderpy)デコレータを使うことで特定のクラスの読み込み順を制御することができます。
    - 例: `@priority(42)`
- [`ShortcutsRegister`](#shortcuts_registerpy)クラスを使用することでショートカットキーを登録することができます。
    - 例: `ShortcutsRegister().add(Key(HOGE_OT_YourOperator, 'A'))`
- デバッグ向けの機能もいくつか搭載されています。
    - [`AddonRegister`](#addon_registerpy)クラスの`is_debug_mode`引数によって有効化できます。
        - 無効にすると、各ディレクトリ直下に`debug`ディレクトリが存在する場合、その中にあるモジュールが無視されます。
        - 有効にすると`debug`ディレクトリ内のモジュールが読み込まれ、アドオンの再読み込み機能([`reload()`](#addon_registerpy)メソッド)が使えるようになります。

- 読み込み対象の各モジュールにregister()関数やunregister()関数がある場合、アドオンの登録・解除の際に呼び出されます。
- Blender標準形式の[翻訳テーブル](#addon_registerpy)を使用して多言語に対応させることができます。

このreadmeでは以下のディレクトリ構成としてサンプルコードを記述します：
```
.
└── your_addon_folder/
    ├── __init__.py
    ├── core/
    │   ├── addon_register.py
    │   ├── shortcuts_register.py
    │   └── proc_loader.py
    ├── operators/
    │   ├── __init__.py
    │   └── your_operator.py
    └── panels/
        └── your_panel.py
```

## addon_register.py
- __AddonRegister__ クラス
  - アドオンの登録を行う中心的なクラスです。
    - コンストラクタの第一引数にはアドオンフォルダ(通常は`__init__.py`ファイルの`__file__`変数)、第二引数には各機能のファイルが含まれるフォルダ名をリストで渡してください。
    - 第三・第四引数はオプションで、モジュール名とBlenderの標準形式の翻訳テーブルを渡すことで自動で登録・解除します。
        - 第三引数にはモジュール名(通常は`__init__.py`ファイルの`__name__`変数)、第四引数には翻訳テーブルの辞書を渡してください
    - 第五引数(is_debug_mode)もオプションで、デバッグモードの有効と無効を設定します。(デフォルトは`False`)
        - デバッグモードが`False`の場合、指定した各ディレクトリ直下の`debug`フォルダが無視されます。(存在する場合)
        - デバッグモードが`True`の場合、reload()メソッドが使用できるようになります。
        - 例: `addon = AddonRegister(__file__, ['operators', panels], is_debug_mode=True)`
    - `__init__.py`ファイルでインスタンスを生成し、`register()`メソッドと`unregister()`メソッドを同名のグローバル関数でラップしてください。

    **`reload()`メソッド**
    - Blenderの`script.reload`オペレータが実行された際に、アドオン全体を再読込します。
    - デバッグ用の機能で、コンストラクタの`is_debug_mode`引数が`True`に設定されている場合のみ動作します。`False`の場合は何もしません。
    - 使用する場合、`__init__.py`ファイル内でこのメソッドを呼び出すようにしてください。

    - 例
    ```
    addon = AddonRegister(__file__, ['operators', 'panels']) #インスタンス生成
    def register() -> None: addon.register()                 #register()メソッドをラップ
    def unregister() -> None: addon.unregister()             #unregister()メソッドをラップ
    ```
    - 翻訳辞書を登録する例
    ```
    #翻訳テーブルの定義
    translation_dict = {
        "en_US": { ('*', 'hoge') : 'English' },
        "ja_JP" : { ('*', 'hoge') : '日本語' }
    }

    addon = AddonRegister(__file__, ['operators', 'panels'], __name__, translation_dict) #インスタンス生成
    def register() -> None: addon.register()                                             #register()関数をラップ
    def unregister() -> None: addon.unregister()                                         #unregister()関数をラップ
    ```
    - デバッグモードを使用する例
    ```
    addon = AddonRegister(__file__, ['operators', 'panels'], is_debug_mode=True) #インスタンス生成
    addon.reload()                                           #アドオンを再読込する
    def register() -> None: addon.register()                 #register()メソッドをラップ
    def unregister() -> None: addon.unregister()             #unregister()メソッドをラップ
    ```

## shortcuts_register.py
- __Key__ クラス
    - ショートカットキーの情報を保存するデータクラスです。
        - `operator`: ショートカットキーの対象となるオペレーター
        - `key`: ショートカットキー

        __これ以降のアトリビュートはオプションです。__

        - `key_modifier`: 追加のショートカットキー(デフォルトは`'NONE'`)
        -  `trigger`: トリガーとなるキーの動作(デフォルトは`'PRESS'`)

            _特殊キー類の設定(同時押しキー)_

        - `any`: いずれかの特殊キー(デフォルトは`False`)
        - `shift`: シフトキー(デフォルトは`False`)
        -  `ctrl`: コントロールキー(デフォルトは`False`)
        - `alt`: オルトキー(デフォルトは`False`)
        - `oskey`: OSのキー(デフォルトは`False`)
    - 例: `Key(HOGE_OT_YourOperator, 'A')`

- __ShotrcutsRegister__ クラス
    - ショートカットキーを登録します。
    - シングルトンパターンを採用しています。

    **`add(keys, name, space_type, region_type, modal, tool) -> List[tuple[KeyMap, KeyMapItem]]`メソッド**

    - 一つまたは複数のショートカットキーを登録し、登録したキーマップとアイテムをリストで返します。
    - `disable`デコレータが付けられたクラスはスキップされます。
    - 引数
        - `keys`
            - 一つまたは複数のKeyオブジェクト
            - 複数の場合はリストとして渡してください

        _これ以降の引数はオプションであり、bpy.context.window_manager.keyconfigs.addon.keymaps.new()関数の引数に対応しています。_

        - `name`: ショートカットの識別子です。(デフォルトは`'Window'`)
        - `space_type`: ショートカットキーが動作する領域を指定します。(デフォルトは`'EMPTY'`)
        - `region_type`: ショートカットキーが動作する範囲を指定します。(デフォルトは`'WINDOW'`)
        - `modal`: モーダルモードかを指定します。(デフォルトは`False`)
        - `tool`: ツールモードかを指定します。(デフォルトは`False`)

    - 例: `ShortcutsRegister().add(Key(HOGE_OT_YourOperator, 'A'))`

    **`delete(kms) -> bool`メソッド**
    - キーマップとキーマップアイテムをタプルとして受け取り、ショートカットキーを削除します。
    - 正しく削除されたら`True`、存在しない値を指定すると`False`が返ります。

    - 例: `ShortcutsRegister().delete(kms)`

    **`unregister()`メソッド**

    - すべてのショートカットキーを削除します。
    - AddonRegisterクラスのunregister()メソッド内で自動的に呼び出されるため、通常は明示的に呼び出す必要はありません。

    - 例: `ShortcutsRegister().unregister()`

## proc_loader.py
- __DuplicateAttributeError__ クラス
    - デコレータによって使用される属性がすでに対象のクラスに存在している場合に送出される例外クラスです。

- __disable__ デコレータ
    - このデコレータを付けたクラスはProcLoaderによって無視され、読み込まれません。
    - 対象のクラスに`addon_proc_disabled`属性が存在していない必要があります。
    - 例
        ```
        @disable
        class HOGE_OT_YourOperator(bpy.types.Operator): pass
        ```
- __priority__ デコレータ
    - このデコレータに数値を指定することで、クラスの読み込み順を制御することができます。
    - 数値は0以上で、小さいほど先に読み込まれます。
    - このデコレータを付けないか0以下の値を指定すると最後に読み込まれます。
    - このデコレータを付けないか同じ数値が指定された場合の読み込み順は保証されません。
    - 対象のクラスに`addon_proc_priority`属性が存在していない必要があります。
    - 例
        ```
        @priority(42)
        class HOGE_OT_YourOperator(bpy.types.Operator): pass
        ```

- __ProcLoader__ クラス
    - アドオンのファイルを読み込み、Blenderに登録するクラスです。
    - サブフォルダも含めて、指定したフォルダ以下のすべてのモジュールを取得します。
    - 各ディレクトリの`__init__.py`に`ignore`という名前のリストを定義し、モジュール名を記述することでそのモジュールを無視します。
        - モジュールのパスはリストが定義されている`__init__.py`ファイルが存在するディレクトリから見た相対パスです。
            - 例(`operators`フォルダ内の`__init__.py`ファイルの場合): `ignore = ['your_operator']`
    - モジュール数やクラス数に制限はありません。
    - AddonRegisterクラスにより操作されるため通常は明示的に操作する必要はありません。

    - **`__init__(path, target_classes)` メソッド**
        - 引数
            - `path`: アドオンへの絶対パス(通常はアドオンの__init__.pyファイルの`__file__`変数)
            - `target_classes`(オプション): 読み込み対象のクラスを指定します。
                - 指定しなかった場合、bpy.types下の`Operator`, `Panel`, `Menu`, `Preferences`, `PropertyGroup`クラスが対象になります。
            - `is_debug_mode`(オプション)
                - デバッグモードを指定します。(デフォルトは`False`)
                    - `False`の場合、指定したディレクトリ直下にある`debug`フォルダを無視します。
        - 例: `pl = ProcLoader(__file__)`

    - **`load(dirs) -> List[Sequence[Union[ModuleType, object]]]`メソッド**
        - 読み込んだモジュールとクラスをリストで返します。
        - 引数: `dirs`: 読み込み対象のディレクトリを指定します。
        - 例: `modules, classes = pl.load(['operators', 'panels'])`

    - **`load_files(dirs) -> List[str]`メソッド**
        - `[アドオン名].[フォルダ名].[ファイル名]`の形でモジュールのパスを取得します。
        - `ignore`リストに指定されたモジュールは除外します・
        - 引数: `dirs`: 読み込み対象のディレクトリを指定します。
        - 例: `modules_path = pl.load_files(['operators', 'panels'])`

    - **`load_modules(paths) -> List[ModuleType]`メソッド**
        - 渡されたモジュールへのパスを元に、モジュールをインポートします。
        - 引数: `paths`: 読み込むモジュールへのパスを指定します。
        - 例: `modules = pl.load_module(module_path)`

    - **`load_classes(modules) -> List[object]`メソッド**
        - 渡されたモジュール内に存在するクラスを読み込みます。
        - `disable`や`priority`デコレータを元に、クラスオブジェクトをソートします。
        - 引数: `modules`: 対象のモジュールを指定します。
        - 例: `classes = pl.load_classes(modules)`

# サンプル

`__init__.py`
```
from .core.register_addon import AddonRegister

bl_info = {
    "name": "Addon_name",
    "author": "your_name",
    "version": (1, 0, 0),
    "blender": (4, 1, 0),
    "location": "View3D > Tools > Addon_name",
    "description": "",
    "category": "General",
}

addon = AddonRegister(__file__, [
    'operators',
    'panels'
])

def register() -> None: addon.register()

def unregister() -> None: addon.unregister()

if __name__ == '__main__':
    register()
```

F1キーが押されたときに通知を表示するアドオンの例(サンプルと同じファイル構成の場合、`operators`フォルダ内に適当な名前をつけた`.py`ファイルを配置し、その中にコピペしてください)

```
from typing import Set

from bpy.types import Context, Operator

from ..core.shortcuts_register import Key, ShortcutsRegister

class HOGE_OT_ToggleLang(Operator):
    bl_idname = "hoge.toggle_lang_operator"
    bl_label = "Toggle Lang Operator"
    bl_description = "Toggle Language."

    def execute(self, context: Context) -> Set[str]:
        self.report({'INFO'}, "HOGE_OT_Report!!!!!!!!!!!!!!")

        return {"FINISHED"}

def register() -> None:
    ShortcutsRegister().add(Key(HOGE_OT_ToggleLang.bl_idname, 'F1'))
```
