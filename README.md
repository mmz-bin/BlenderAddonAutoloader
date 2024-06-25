This library uses English that has been machine-translated from Japanese.

__[日本語のreadmeはこちらから](README.ja.md)__

# __Due to ongoing development, this script is subject to potentially disruptive changes.__

# Blender_Add-on_Autoloader
This script allows for the dynamic registration and unregistration of files that make up the Blender addon. It automates the tedious tasks of registering, unregistering, disabling, prioritizing classes, and registering shortcut keys. Verified to work with Blender 4.1.

The classes to be loaded are written in the `TARGET_CLASSES` class variable within the `ProcLoader` class in [`/core/proc_loader.py`](/core/proc_loader.py).

I believe I have covered all the basic classes, but if there are any missing, please let me know.

It is also possible to specify any class you want.

__Note: The three files inside the core directory (addon_manager.py, keymap_manager.py, proc_loader.py) should be placed in the same directory.__

## Features
- Registers and unregisters all addon classes within a specified directory, including subdirectories.
- Define a list named `ignore` in the `__init__.py` of each directory to specify module names that should be ignored.
    - The module path is relative to the directory where the `__init__.py` file defining the list is located.
        - Example (in the `__init__.py` file of the `opera`tors`folder`): `ignore = ['your_operator']`
- Use the [`disable`](#proc_loaderpy) decorator to ignore specific classes.
    - Example: `@disable`
- Use the [`priority`](#proc_loaderpy) decorator to control the loading order of specific classes.
    - Example: `@priority(42)`
- Use the [`KeymapManager`](#keymap_managerpy) class to register shortcut keys.
    - Example: `KeymapManager().add(Key(HOGE_OT_YourOperator, 'A'))`
- You can register, reference, unregister property groups using the [`PropertiesManager`](#properties_managerpy) class.(The initial configuration requires the `addon_name` argument of the `AddonManager` class.)
    - Example
        - Registering a property: `PropertiesManager().add(Scene, [("your_properties", YourPropertyGroupClass)])`
        - Referencing a property: `prop = PropertiesManager().get(bpy.context.scene, "your_properties")`
- You can omit `bl_idname`, and if omitted, the class name will be automatically assigned. (Please set it explicitly if there is a conflict with the class name.)
- For classes inheriting from `bpy.types.Panel`, you can omit the `bl_category` attribute by setting an arbitrary name in the constructor of [`AddonManager`](#addon_managerpy).
- Several debugging features are also included.
    - These can be enabled using the `is_debug_mode` argument of the [`AddonManager`](#addon_managerpy) class.
        - When disabled, if a `debug` directory exists directly under each directory, the modules within it are ignored.
        - When enabled, modules in the `debug` directory are loaded, and the addon reloading feature ([`reload()`](#addon_managerpy) method) becomes available.

Would you like me to explain or elaborate on any part of this translation?
- You can make it multilingual by using the [translation table](#addon_managerpy) in the standard Blender format.

- If there are register() functions and unregister() functions in each module to be loaded, they will be called when registering and unregistering the add-on.

In this readme, the sample code is written with the following directory structure:
```
.
└── your_addon_folder/
    ├── __init__.py
    ├── core/
    │   ├── addon_manager.py
    │   ├── keymap_manager.py
    │   ├── proc_loader.py
    │   └── properties_manager.py
    ├── operators/
    │   ├── __init__.py
    │   └── your_operator.py
    └── panels/
        └── your_panel.py
```

## addon_manager.py
- __AddonManager__ class
    - **`__init__(path, target_dirs, addon_name, translation_table, cat_name, is_debug_mode)` method**
        - Arguments:
            - `path`: The path to the addon folder (usually the `__file__` variable in the `__init__.py` file).
            - `target_dirs`: The directories to be loaded (must be directly under the addon folder).
            - `addon_name` (optional): The addon name (usually the `__name__` variable in the `__init__.py` file) is required when using the translation table and properties.
            - `translation_table` (optional): The translation table (Blender standard format).
            - `cat_name` (optional): Used to automatically set the `bl_category` of classes inheriting from `bpy.types.Panel`.(If you set it explicitly it will take precedence.)
            - `is_debug_mode` (optional): Specifies debug mode.
                - If `False` is specified, the `debug` folder directly under the directories specified in `target_dirs` will be ignored.
                - If `True` is specified, the `reload()` method becomes available.
    - Create an instance in the `__init__.py` file, and wrap the `register()` and `unregister()` methods with global functions of the same name.

    **`reload()` Method**
    - When the Blender's `script.reload` operator is executed, it reloads the entire add-on.
    - This is a debugging feature and only works if the `is_debug_mode` argument in the constructor is set to `True`. It does nothing if `False`.
    - It is called automatically, so you normally don't need to call it explicitly.

    - Example
    ```
        addon = AddonManager(__file__, ['operators', 'panels']) # Instance creation
        def register() -> None: addon.register()                 # Wrap register() function
        def unregister() -> None: addon.unregister()             # Wrap unregister() function
    ```
    - Example of registering a translation dictionary
    ```
    # Definition of translation table
    translation_dict = {
        "en_US": { ('*', 'hoge') : 'English' },
        "ja_JP" : { ('*', 'hoge') : '日本語' }
    }

    addon = AddonManager(__file__, ['operators', 'panels'], __name__, translation_dict) # Instance creation
    def register() -> None: addon.register()                                             # Wrap register() method
    def unregister() -> None: addon.unregister()                                         # Wrap unregister() method
    ```
    - Example of using debug mode
    ```
    addon = AddonManager(__file__, ['operators', 'panels'], is_debug_mode=True) # Instance creation
    def register() -> None: addon.register()                 # Wrap the register() method
    def unregister() -> None: addon.unregister()             # Wrap the unregister() method
    ```

## keymap_manager.py
- __Key__ class
    - This is a data class for storing shortcut key information.
        - `operator`: The class object that is the target of the shortcut key.
        - `key`: The shortcut key

        __The following attributes are optional.__

        - `key_modifier`: Additional shortcut key (default is `'NONE'`)
        - `trigger`: The action of the trigger key (default is `'PRESS'`)

            _Settings for special keys (keys pressed simultaneously)_

        - `any`: Any special key (default is `False`)
        - `shift`: Shift key (default is `False`)
        - `ctrl`: Control key (default is `False`)
        - `alt`: Alt key (default is `False`)
        - `oskey`: OS key (default is `False`)
    - Example: `Key(HOGE_OT_YourOperator, 'A')`

- __KeymapManager__ class
    - This class registers shortcut keys.
    - It adopts the singleton pattern.

    **`add(keys, name, space_type, region_type, modal, tool) -> List[tuple[KeyMap, KeyMapItem]]` method**

    - Registers one or multiple shortcut keys and returns a list of registered keymaps and items.
    - Classes with the `disable` decorator will be skipped.
    - Arguments
        - `keys`
            - One or multiple Key objects
            - If multiple, pass them as a list

        _The following arguments are optional and correspond to the arguments of the bpy.context.window_manager.keyconfigs.addon.keymaps.new() function._

        - `name`: Identifier for the shortcut (default is `'Window'`)
        - `space_type`: Specifies the area where the shortcut key operates (default is `'EMPTY'`)
        - `region_type`: Specifies the range where the shortcut key operates (default is `'WINDOW'`)
        - `modal`: Specifies whether it is in modal mode (default is `False`)
        - `tool`: Specifies whether it is in tool mode (default is `False`)

    - Example: `KeymapManager().add(Key(HOGE_OT_YourOperator, 'A'))`

    **`delete(subject) -> bool` method**
    - Receives a tuple of keymap and keymap item or an operator class where shortcut keys are registered, and deletes the shortcut keys.
    - It accepts a keymap and keymap item as a tuple and deletes the shortcut key.
    - It returns `True` if it is correctly deleted, and `False` if a non-existent value is specified.

    - Example: `KeymapManager().delete(kms)`

    **`unregister()` method**

    - Deletes all shortcut keys.
    - It is automatically called within the unregister() method of the AddonManager class, so it usually does not need to be explicitly called.

    - Example: `KeymapManager().unregister()`

## properties_manager.py
- __PropertiesManager__ Class
    - It adopts the singleton pattern.
    - It registers, unregisters, and references property groups (classes that inherit `bpy.types.PropertyGroup`).
    - Classes with the `disable` decorator are ignored.
    - To avoid name collisions with other addons, it automatically adds a prefix to the property name. (You don't need to be aware of this when using the `get()` method.)

    - **`set_name(name)` Method**
        - Specifies the prefix to be attached to the property.
        - Once a value is specified, it cannot be re-specified.
        - In the initial configuration, it is set as the `__name__` variable in the `__init__.py` file (the `addon_name` argument of the [`AddonManager`] constructor).
    - **`add(prop_type, properties) -> List[str]` Method**
        - Adds a property.
        - The prefix specified by the `set_name()` method is attached (`[prefix]_[property name]` form).
            - Arguments
                - `prop_type`: Specifies the class to which the property will be added.
                - `properties`: Accepts a tuple or list of tuples in the form `(property name, operator to register)`.
            - Return value: The name of the added property (already renamed)
            - Example: `PropertiesManager().add(Scene, [("your_properties", YourPropertyGroupClass)])`
    - **`get(context, attr, is_mangling) -> Any` Method**
        - Retrieves the property name.
        - If the specified property name does not exist, a `ValueError` occurs.
        - By default, if the prefix specified by the `set_name()` method is attached, it retrieves it as is, and if it is not attached, it adds it and retrieves it.
            - Arguments
                - `context`: The object from which the property will be retrieved
                - `attr`: The attribute name to retrieve
                - `is_mangling` (optional): Specifies whether to enable name modification if the `attr` argument does not have the standard prefix. (Default is `True`)
            - Return value
                - The retrieved property
            - Example: `prop = PropertiesManager().get(bpy.context.scene, "your_properties")`
    - **`delete(prop_name) -> bool` Method**
        - Deletes the property with the specified name.
        - Returns `True` if the property exists and `False` if it does not.
            - Argument: `prop_name`: The name of the property you want to delete
        - Example: `PropertiesManager().delete("your_properties")`
    - **`unregister()` Method**
        - Deletes all registered properties.
        - Normally, it is automatically called by `AddonManager`, so there is no need to call it explicitly.
    - Example
        - Registering a property
        ```
        from ..core.properties_manager import PropertiesManager

        from bpy.types import PropertyGroup
        from bpy.props import BoolProperty

        from bpy.types import Scene

        class Hoge_Properties(PropertyGroup):
            bl_idname = "Hoge_Properties"
            bl_label = "sample"

            fuga: BoolProperty(name="piyo", default=False)

        def register() -> None:
            PropertiesManager().add(Scene, [("hoge", Hoge_Properties)])

        ```
        - Referencing a property
        ```
        from bpy.types import Panel, Context, Scene

        from ..core.properties_manager import PropertiesManager

        class MMZ_PT_Prop(Panel):
            bl_label = "Property Test"
            bl_space_type = "VIEW_3D"
            bl_region_type = "UI"

            def draw(self, context: Context):
                prop = PropertiesManager().get(context.scene, "hoge")
                self.layout.label(text= f"fuga = {prop.fuga}")
        ```

## proc_loader.py
- __DuplicateAttributeError__ class
    - This is an exception class raised when an attribute used by the decorator already exists in the target class.

- __disable__ decorator
    - A class with this decorator will be ignored and not loaded by ProcLoader.
    - The target class must not have the `addon_proc_disabled` attribute.
    - Example
        ```
        @disable
        class HOGE_OT_YourOperator(bpy.types.Operator): pass
        ```
- __priority__ decorator
    - This decorator allows you to control the loading order of classes by specifying a number.
    - The number must be 0 or higher, and the smaller the number, the earlier it is loaded.
    - If this decorator is not attached or a value of 0 or less is specified, it will be loaded last.
    - If this decorator is not attached or the same number is specified, the loading order is not guaranteed.
    - The target class must not have the `addon_proc_priority` attribute.
    - Example
        ```
        @priority(42)
        class HOGE_OT_YourOperator(bpy.types.Operator): pass
        ```

- __ProcLoader__ class
    - This class loads addon files and registers them with Blender.
    - It retrieves all modules below the specified folder, including subfolders.
    - Define a list named `ignore` in the `__init__.py` of each directory and list the module names to ignore those modules.
        - The module path is a relative path from the directory where the `__init__.py` file defining the list is located.
            - Example (`__init__.py` file in the `operators` folder): `ignore = ['your_operator']`
    - There are no restrictions on the number of modules or classes.
    - It is usually manipulated by the AddonManager class, so there is no need to explicitly manipulate it.

    - **`__init__(path, target_classes)` method**
        - Arguments
            - `path`: Absolute path to the addon (usually the `__file__` variable in the addon's `__init__.py` file)
            - `target_classes` (optional): Specifies the target classes to load.
                - If not specified, the classes included in `TARGET_CLASSES` within the `ProcLoader` class in [`/core/proc_loader.py`](/core/proc_loader.py) will be targeted.
            - `is_debug_mode` (optional)
                - Specifies the debug mode. (The default is `False`)
                    - If `False`, it ignores the `debug` folder directly under the specified directory.
        - Example: `pl = ProcLoader(__file__)`

    - **`load(dirs, cat_name) -> List[Sequence[Union[ModuleType, object]]]` method**
        - Returns a list of loaded modules and classes.
        - Arguments
            - `dirs`: Specifies the directories to load.
            - `cat_name`(optional): Sets the initial value of `bl_category` for classes inheriting from `bpy.types.Panel`.
        - Example: `modules, classes = pl.load(['operators', 'panels'])`

    - **`load_files(dirs) -> List[str]` method**
        - Obtains the module paths in the form of `[addon name].[folder name].[file name]`.
        - Excludes modules specified in the `ignore` list.
        - Argument: `dirs`: Specifies the directories to load.
        - Example: `modules_path = pl.load_files(['operators', 'panels'])`

    - **`load_modules(paths) -> List[ModuleType]` method**
        - Imports modules based on the given paths.
        - Argument: `paths`: Specifies the paths to the modules to load.
        - Example: `modules = pl.load_module(module_path)`

    - **`load_classes(modules, cat_name) -> List[object]` method**
        - Loads the classes within the given modules.
        - Sorts the class objects based on the `disable` and `priority` decorators.
        - Arguments
            - `modules`: Specifies the target modules.
            - `cat_name`(optional): Sets the initial value of `bl_category` for classes inheriting from `bpy.types.Panel`.
        - Example: `classes = pl.load_classes(modules)`

# Sample

`__init__.py`
```
from .core.register_addon import AddonManager

bl_info = {
    "name": "Addon_name",
    "author": "your_name",
    "version": (1, 0, 0),
    "blender": (4, 1, 0),
    "location": "View3D > Tools > Addon_name",
    "description": "",
    "category": "General",
}

addon = AddonManager(__file__, [
    'operators',
    'panels'
])

def register() -> None: addon.register()

def unregister() -> None: addon.unregister()

if __name__ == '__main__':
    register()
```

An example of an add-on that displays a notification when the F1 key is pressed (if the file structure is the same as the sample, place a `.py` file with an appropriate name in the `operators` folder and copy and paste into it).

```
from typing import Set

from bpy.types import Context, Operator

from ..core.keymap_manager import Key, KeymapManager

class HOGE_OT_Report(Operator):
    bl_idname = "hoge.report_operator"
    bl_label = "Report Operator"
    bl_description = "Send information"

    def execute(self, context: Context) -> Set[str]:
        self.report({'INFO'}, "HOGE_OT_Report!!!!!!!!!!!!!!")

        return {"FINISHED"}

def register() -> None:
    KeymapManager().add(Key(HOGE_OT_Report, 'F1'))

```
