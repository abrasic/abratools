bl_info = {
    'name': 'AbraTools',
    'author': 'Abrasic',
    'version': (1, 0, 0),
    'blender': (2, 80, 0),
    'description': 'Blender Animator toolkit',
    'location' : 'Preferences > Header > aT',
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
addon_keymaps = []

def register():
    bpy.context.preferences.themes[0].preferences.space.header = bpy.context.preferences.themes[0].text_editor.space.header ## Temporary
    
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.USERPREF_HT_header.append(toolshelf.drawToggle)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if(kc):
        km = kc.keymaps.new(name='Animation Channels', space_type='EMPTY')
        kmi = km.keymap_items.new(quickView.ABRA_OT_isolate_func.bl_idname, 'LEFTMOUSE', 'RELEASE')
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new(name='Animation Channels', space_type='EMPTY')
        kmi = km.keymap_items.new(quickView.ABRA_OT_isolate_func.bl_idname, 'LEFTMOUSE', 'RELEASE', shift=True)
        addon_keymaps.append((km, kmi))
        

def unregister():

    bpy.context.preferences.themes[0].preferences.space.header = toolshelf.prefsOldHeaderCol
    bpy.types.USERPREF_HT_header.remove(toolshelf.drawToggle)
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        
    addon_keymaps.clear()

if __name__ == "__main__":
    register()