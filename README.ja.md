This library uses English that has been machine-translated from Japanese.



# BlenderAddonLoader
Blenderアドオンの動的な登録・解除を実現するスクリプトです。
クラスの登録・解除・無効化・優先順位付け・ショートカットキーの登録といった面倒な作業を自動で行うことができます。

__注意：coreディレクトリ内部にある3つのファイル(register_addon.py, register_shortcuts.py, proc_loader.py)は同じディレクトリに配置してください。__

このreadmeでは以下のディレクトリ構成としてサンプルコードを記述します：
```
.
└── your_addon_folder/
    ├── __init__.py
    ├── core/
    │   ├── register_addon.py
    │   ├── register_shortcuts.py
    │   └── proc_loader.py
    ├── operators/
    │   ├── __init__.py
    │   └── your_operator.py
    └── panels/
        └── your_panel.py
```

## register_addon.py
- AddonRegister クラス
  - アドオンの登録を行う中心的なクラスです。
  - コンストラクタの第一引数にはアドオンフォルダ(通常は`__init__.py`ファイルの`__file__`変数)、第二引数には各機能のファイルが含まれるフォルダ名をリストで渡してください。第三引数はオプションで、翻訳テーブルを渡すことで自動で登録・解除します。
    - 例
    ```
    
    ```
  - `__init__.py`ファイルでインスタンスを生成し、`register()`関数と`unregister()`関数をラップしてください。
    - ルートディレクトリにある`__init__.py`ファイルはサンプルです。
