bl_info = {
    'name': 'AbraTools',
    'author': 'Abrasic',
    'version': (1, 0, 0),
    'blender': (3, 0, 0),
    'description': 'Blender animation toolkit',
    'location' : '3D Viewport or Preferences > Header > aT',
    'category': 'Animation',
    'warning': 'beta1 | This is a beta version of AbraTools',
    'doc_url': 'https://docs.abx.gg/support/download-and-setup',
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
    bpy.types.VIEW3D_MT_editor_menus.append(toolshelf.vpToggleBtn)
    bpy.app.handlers.frame_change_post.append(quickView.overlay_func)
    bpy.types.Scene.set_selection = bpy.props.PointerProperty(type=panels.Set_Selector_Vars)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if(kc):
        km = kc.keymaps.new(name='Animation Channels', space_type='EMPTY')
        kmi = km.keymap_items.new(quickView.ABRA_OT_isolate_func.bl_idname, 'LEFTMOUSE', 'RELEASE')
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new(name='Animation Channels', space_type='EMPTY')
        kmi = km.keymap_items.new(quickView.ABRA_OT_isolate_func.bl_idname, 'LEFTMOUSE', 'RELEASE', shift=1)
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new(name='Frames', space_type='EMPTY')
        kmi = km.keymap_items.new(quickView.ABRA_OT_overlay_func.bl_idname, 'SPACE', 'RELEASE')
        addon_keymaps.append((km, kmi))

    print("[aT] AbraTools is now running")

def unregister():
    bpy.context.preferences.themes[0].preferences.space.header = toolshelf.prefsOldHeaderCol
    bpy.types.USERPREF_HT_header.remove(toolshelf.drawToggle)
    bpy.types.VIEW3D_MT_editor_menus.remove(toolshelf.vpToggleBtn)
    bpy.app.handlers.frame_change_pre.remove(quickView.overlay_func)

    del bpy.types.Scene.set_selection
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        
    addon_keymaps.clear()

    print("[aT] AbraTools is no longer running")

if __name__ == "__main__":
    register()