from .core.AddonRegister import AddonRegister

bl_info = {
    "name": "NAME",
    "author": "NAME",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Tools > NAME",
    "description": "機能詰め合わせ",
    "category": "General",
}

addon = AddonRegister(__file__, [
    'operators',
    'panels'
])

def register() -> None:
    addon.register()

def unregister() -> None:
    addon.unregister()

if __name__ == '__main__':
    register()
