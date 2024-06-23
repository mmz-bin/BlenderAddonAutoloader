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
