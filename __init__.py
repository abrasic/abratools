bl_info = {
    'name': 'AbraTools',
    'author': 'Abrasic',
    'version': (1, 0, 0),
    'blender': (2, 80, 0),
    'description': 'Blender Animator toolkit',
    'location' : 'Graph Editor > Header',
    'category': 'Animation',
    'warning': 'This is an alpha version of AbraTools',
    'tracker_url': 'https://github.com/abrasic/abratools',
}

import bpy, os
from .core import key, quickView
from .ui import prefs, panels, toolshelf
################################

classes = quickView.cls + key.cls + prefs.cls + panels.cls + toolshelf.cls
icons_coll = {}

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.USERPREF_HT_header.append(toolshelf.drawToggle)

    # This should always be false on boot
    bpy.context.preferences.addons["abTools"].preferences.abraon = False

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.USERPREF_HT_header.remove(toolshelf.drawToggle)

if __name__ == "__main__":
    register()