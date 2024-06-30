This library uses English that has been machine-translated from Japanese.

__[The English readme is here](README.md)__

# __このスクリプトは開発中のため、破壊的な変更が加えられる可能性があります。__

# Blender_Add-on_Manager
Blenderアドオンを構成するファイルの動的な登録・解除を実現するスクリプトです。
クラスの登録・解除・無効化・優先順位付け・ショートカットキーの登録といった面倒な作業を自動で行うことができます。
Blender 4.1で動作確認しています。

読み込み対象のクラスは[`/manager/core/proc_loader.py`](/manager/core/proc_loader.py)の`ProcLoader`クラス内にある`TARGET_CLASSES`クラス変数に書いてあります。

基本的なクラスは網羅しているつもりですが、抜けているものがあったらお知らせください。

任意のクラスを指定することも可能です。

__注意：coreディレクトリ内部にある3つのファイル(addon_manager.py, keymap_manager.py, proc_loader.py)は同じディレクトリに配置してください。__

## クイックスタート
1. あなたのアドオンフォルダ内に[`manager`](/manager/)フォルダを配置
2. `__init__.py`ファイル内で[`AddonManager`](#addon_managerpy)クラスのインスタンスを生成
3. `AddonManager`インスタンスの`register()`メソッドと`unregister()`メソッドを同じ名前のグローバル関数でラップする
4. 指定したフォルダ内に使いたいオペレーターを含むファイルを配置する

### サンプルコード

`__init__.py`
```
from .manager.core.register_addon import AddonManager #AddonManagerクラスをインポートする

#アドオンの情報
bl_info = {
    "name": "Addon_name",
    "author": "your_name",
    "version": (1, 0, 0),
    "blender": (4, 1, 0),
    "location": "View3D > Tools > Addon_name",
    "description": "",
    "category": "General",
}

#読み込み対象のフォルダ名
load_folder = [
    'operators',
]

addon = AddonManager(__file__, load_folder) #AddonManagerクラスのインスタンスを生成する

#'register()'メソッドと'unregister()'メソッドをラップする
def register(): addon.register()
def unregister(): addon.unregister()
```
`operators/hoge.py`
```
'''F1キーが押されたときに通知を表示するスクリプト'''

from bpy.types import Operator

#ショートカットキーを登録するための`Key`データクラスと`keymapManagerクラスをインポートする`
from ..manager.core.keymap_manager import Key, KeymapManager

class HOGE_OT_Sample(Operator):
    bl_idname = "hoge.sample_operator"
    bl_label = "Test Operator"
    bl_description = "Test."

    def execute(self, context):
        self.report({'INFO'}, "HOGE_OT_Sample!!!!!!!!!!!!!!")

        return {"FINISHED"}

def register():
    KeymapManager().add(Key(HOGE_OT_Sample, 'F1')) #F1キーが押されたときに'HOGE_OT_Sample'オペレーターが実行されるように設定する
```


## 機能
- サブディレクトリを含めて、指定したディレクトリ内のすべてのアドオンのクラスを登録・解除します。
- 各ディレクトリの`__init__.py`に`ignore`という名前のリストを定義し、モジュール名を記述することでそのモジュールを無視します。
    - モジュールのパスはリストが定義されている`__init__.py`ファイルが存在するディレクトリから見た相対パスです。
        - 例(`operators`フォルダ内の`__init__.py`ファイルの場合): `ignore = ['your_operator']`
- [`disable`](#proc_loaderpy)デコレータを使うことで特定のクラスを無視することができます。
    - 例: `@disable`
- [`priority`](#proc_loaderpy)デコレータを使うことで特定のクラスの読み込み順を制御することができます。
    - 例: `@priority(42)`
- [`KeymapManager`](#keymap_managerpy)クラスを使用することでショートカットキーを登録することができます。
    - 例: `KeymapManager().add(Key(HOGE_OT_YourOperator, 'A'))`
- [`PropertiesManager`](#properties_managerpy)クラスを使用することでプロパティグループを登録・参照・解除することができます。(初期の構成では`AddonManager`クラスの`addon_name`引数が必要になります。)
    - 例
        - プロパティの登録: `PropertiesManager().add(Scene, [("your_properties", YourPropertyGroupClass)])`
        - プロパティの参照: `prop = PropertiesManager().get(bpy.context.scene, "your_properties")`
- `bl_idname`を省略でき、省略した場合は自動的にクラス名が割り当てられます。(クラス名が競合する際は明示的に設定してください。)
- `bpy.types.Panel`を継承したクラスの場合、[`AddonManager`](#addon_managerpy)のコンストラクタで任意の名前を設定することで`bl_category`属性を省略できます。(明示的に設定した場合はそれが優先されます。)
- デバッグ向けの機能もいくつか搭載されています。
    - [`AddonManager`](#addon_managerpy)クラスの`is_debug_mode`引数によって有効化できます。
        - 無効にすると、各ディレクトリ直下に`debug`ディレクトリが存在する場合、その中にあるモジュールが無視されます。
        - 有効にすると`debug`ディレクトリ内のモジュールが読み込まれ、アドオンの再読み込み機能([`reload()`](#addon_managerpy)メソッド)が使えるようになります。

- 読み込み対象の各モジュールにregister()関数やunregister()関数がある場合、アドオンの登録・解除の際に呼び出されます。
- Blender標準形式の[翻訳テーブル](#addon_managerpy)を使用して多言語に対応させることができます。
- [`constants.py`](#constantspy)にオペレーターの戻り値やモード名などいくつかの定数が用意されているため、入力の手間とタイプミスを減らすことができます。
- `DrawText`クラスを使ってテキストの描画を簡素化できます。(ドキュメント未作成)

このreadmeでは以下のディレクトリ構成としてサンプルコードを記述します：
```
.
└── your_addon_folder/
    ├── __init__.py
    ├── manager/
    │   ├── core/
    │   │   ├── addon_manager.py
    │   │   ├── keymap_manager.py
    │   │   ├── properties_manager.py
    │   │   └── proc_loader.py
    │   └── constants.py
    ├── operators/
    │   ├── __init__.py
    │   └── your_operator.py
    └── panels/
        └── your_panel.py
```

## addon_manager.py
- __AddonManager__ クラス
  - アドオンの登録を行う中心的なクラスです。
    - **`__init__(path, target_dirs, addon_name, translation_table, cat_name, is_debug_mode)` メソッド**
        - 引数
            - `path`: アドオンフォルダへのパス(通常は`__init__.py`ファイルの`__file__`変数)
            - `target_dirs`: 読み込みの対象となるディレクトリ(アドオンフォルダの直下にある必要があります。)
            - `addon_name`(オプション): アドオン名(通常は`__init__.py`ファイルの`__name__変数`)翻訳テーブルやプロパティを使用する際に必要になります。
            - `translation_table`(オプション): 翻訳テーブル(Blenderの標準形式)
            - `cat_name`(オプション): `bpy.types.Panel`を継承したクラスの`bl_category`を自動で設定したい場合に使用します。
            - `is_debug_mode`(オプション): デバッグモードを指定します。(デフォルトは`False`)
                - `False`を指定すると`target_dirs`で指定したディレクトリの直下にある`debug`フォルダが無視されるようになります。
                - `True`を指定すると`reload()`メソッドが使えるようになります。
    - `__init__.py`ファイルでインスタンスを生成し、`register()`メソッドと`unregister()`メソッドを同名のグローバル関数でラップしてください。

    **`reload()`メソッド**
    - Blenderの`script.reload`オペレータが実行された際に、アドオン全体を再読込します。
    - デバッグ用の機能で、コンストラクタの`is_debug_mode`引数が`True`に設定されている場合のみ動作します。`False`の場合は何もしません。
    - 自動的に呼び出されるため、通常は明示的に呼び出す必要はありません。

    - 例
    ```
    addon = AddonManager(__file__, ['operators', 'panels']) #インスタンス生成
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

    addon = AddonManager(__file__, ['operators', 'panels'], __name__, translation_dict) #インスタンス生成
    def register() -> None: addon.register()                                             #register()関数をラップ
    def unregister() -> None: addon.unregister()                                         #unregister()関数をラップ
    ```

    - デバッグモードを使用する例
    ```
    addon = AddonManager(__file__, ['operators', 'panels'], is_debug_mode=True) #インスタンス生成
    def register() -> None: addon.register()                 #register()メソッドをラップ
    def unregister() -> None: addon.unregister()             #unregister()メソッドをラップ
    ```

## keymap_manager.py
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

- __KeymapManager__ クラス
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

    - 例: `KeymapManager().add(Key(HOGE_OT_YourOperator, 'A'))`

    **`delete(subject) -> bool`メソッド**
    - キーマップとキーマップアイテムのタプルまたはショートカットキーが登録されているオペレータークラスを受け取り、ショートカットキーを削除します。
    - 正しく削除されたら`True`、存在しない値を指定すると`False`が返ります。

    - 例: `KeymapManager().delete(kms)`

    **`unregister()`メソッド**

    - すべてのショートカットキーを削除します。
    - AddonManagerクラスのunregister()メソッド内で自動的に呼び出されるため、通常は明示的に呼び出す必要はありません。

    - 例: `KeymapManager().unregister()`

## properties_manager.py
- __PropertiesManager__ クラス
    - シングルトンパターンを採用しています。
    - プロパティグループ(`bpy.types.PropertyGroup`を継承しているクラス)の登録・解除・参照を行います。
    - `disable`デコレータが着いているクラスは無視されます。
    - 他のアドオンとの名前の衝突を避けるため、自動でプロパティ名に接頭辞を追加します。(`get()`メソッドを使う場合は意識する必要はありません。)

    - **`set_name(name)` メソッド**
        - プロパティにつける接頭辞を指定します。
        - 一度値を指定すると、再指定できなくなります。
        - 初期の構成では`__init__.py`ファイルの`__name__`変数([`AddonManager`](#addon_managerpy)のコンストラクタの`addon_name`引数)として設定されます。
    - **`add(prop_type, properties) -> List[str]` メソッド**
        - プロパティを追加します。
        - `set_name()`メソッドで指定した接頭辞(`[接頭辞]_[プロパティ名]`の形)が付けられます。
            - 引数
                - `prop_type`: プロパティを追加する対象のクラスを指定します。
                - `properties`: `(プロパティ名, 登録するオペレーター)`の形式のタプルもしくはタプルのリストを受け取ります。
            - 戻り値: 追加したプロパティ名(リネーム済みのもの)
            - 例: `PropertiesManager().add(Scene, [("your_properties", YourPropertyGroupClass)])`
    - **`get(context, attr, is_mangling) -> Any` メソッド**
        - プロパティ名を取得します。
        - 指定した名前のプロパティが存在しない場合は`ValueError`が発生します。
        - デフォルトでは、`set_name()`メソッドで指定した接頭辞がついている場合はそのまま、ついていない場合は追加して取得します。
            - 引数
                - `context`: プロパティを取得する対象のオブジェクト
                - `attr`: 取得する属性名
                - `is_mangling`(オプション): `attr`引数に規定の接頭辞がない場合の名前の修正を有効にするかを指定します。(デフォルトは`True`)
            - 戻り値
                - 取得したプロパティ
            - 例: `prop = PropertiesManager().get(bpy.context.scene, "your_properties")`
    - **`delete(prop_name) -> bool` メソッド**
        - 指定した名前のプロパティを削除します。
        - プロパティが存在すれば`True`、存在しなければ`False`を返します
            - 引数: `prop_name`: 削除したいプロパティ名
        - 例: - 例: `PropertiesManager().delete("your_properties")`
    - **`unregister()` メソッド**
        - 登録されているすべてのプロパティを削除します。
        - 通常は`AddonManager`によって自動的に呼び出されるため、明示的に呼び出す必要はありません。
    - 例
        - プロパティを登録する
        ```
        from ..manager.core.properties_manager import PropertiesManager

        from bpy.types import PropertyGroup
        from bpy.props import BoolProperty

        from bpy.types import Scene

        class Hoge_Properties(PropertyGroup):
            bl_idname = "Hoge_Properties"
            bl_label = "sample"

            fuga: BoolProperty(name="piyo", default=False)

        def register() -> None:
            PropertiesManager().add(Scene, ("hoge", Hoge_Properties))

        ```
        - プロパティを参照する
        ```
        from bpy.types import Panel, Context, Scene

        from ..manager.core.properties_manager import PropertiesManager

        class MMZ_PT_Prop(Panel):
            bl_label = "Property Test"
            bl_space_type = "VIEW_3D"
            bl_region_type = "UI"

            def draw(self, context: Context):
                prop = PropertiesManager().get(context.scene, "hoge")
                self.layout.label(text= f"fuga = {prop.fuga}")
        ```

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
    - AddonManagerクラスにより操作されるため通常は明示的に操作する必要はありません。

    - **`__init__(path, target_classes)` メソッド**
        - 引数
            - `path`: アドオンへの絶対パス(通常はアドオンの__init__.pyファイルの`__file__`変数)
            - `target_classes`(オプション): 読み込み対象のクラスを指定します。
                - 指定しなかった場合、[`/manager/core/proc_loader.py`](/manager/core/proc_loader.py)の`ProcLoader`クラス内にある`TARGET_CLASSES`に含まれるクラスが対象になります。
            - `is_debug_mode`(オプション)
                - デバッグモードを指定します。(デフォルトは`False`)
                    - `False`の場合、指定したディレクトリ直下にある`debug`フォルダを無視します。
        - 例: `pl = ProcLoader(__file__)`

    - **`load(dirs, cat_name) -> List[Sequence[Union[ModuleType, object]]]`メソッド**
        - 読み込んだモジュールとクラスをリストで返します。
        - 引数
            - `dirs`: 読み込み対象のディレクトリを指定します。
            - `cat_name`(オプション): `bpy.types.Panel`を継承したクラスの`bl_category`の初期値を設定します。
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

    - **`load_classes(modules, cat_name) -> List[object]`メソッド**
        - 渡されたモジュール内に存在するクラスを読み込みます。
        - `disable`や`priority`デコレータを元に、クラスオブジェクトをソートします。
        - 引数
            - `modules`: 対象のモジュールを指定します。
            - `cat_name`(オプション): `bpy.types.Panel`を継承したクラスの`bl_category`の初期値を設定します。
        - 例: `classes = pl.load_classes(modules)`

## constants.py
- いくつかの定数がクラスとして用意されています。
- __Report__ クラス
    - オペレーター内の`report()`メソッドの第一引数に指定する値が`set[str]`型で用意されています。
        - ERROR
        - INFO
- __Mode__ クラス
    - モードの値が`str`型で用意されています。
        - EDIT
        - EDIT_MESH
        - EDIT_CURVE
        - EDIT_SURFACE
        - EDIT_TEXT
        - EDIT_METABALL
        - EDIT_GPENCIL
        - EDIT_ARMATURE
        - EDIT_LATTICE
        - OBJECT
        - SCULPT
        - PAINT_VERTEX
        - PAINT_WEIGHT
        - PAINT_TEXTURE
- __ObjectType__ クラス
    - オブジェクトの種類が`str`型で用意されています。
        - MESH
        - CURVE
        - SURFACE
        - META
        - FONT
        - ARMATURE
        - LATTICE
        - EMPTY
        - CAMERA
        - LIGHT
        - SPEAKER

- __Op__ クラス
    - オペレーターが返す戻り値が`set[str]`型で用意されています。
        - FINISHED
        - CANCELLED
        - RUNNING_MODAL
        - PASS_THROUGH
