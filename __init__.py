bl_info = {
    'name': 'AbraTools',
    'author': 'Abrasic',
    'version': (0, 2, 4),
    'blender': (3, 0, 0),
    'description': 'Blender animation toolkit',
    'location' : '3D Viewport or Preferences > Header > aT',
    'category': 'Animation',
    'warning': 'beta2 | This is a beta version of AbraTools',
    'doc_url': 'https://docs.abx.gg/',
    'tracker_url': 'https://github.com/abrasic/abratools',
}

import bpy, os, importlib.util, time
from .core import key, quickView, customScripts
from .ui import prefs, panels, toolshelf
from .update import addon_updater_ops
################################

classes = quickView.cls + key.cls + prefs.cls + panels.cls + toolshelf.cls + customScripts.cls
icons_coll = {}
addon_keymaps = []

def register():
    addon_updater_ops.register(bl_info)

    atime = time.time()
    bpy.context.preferences.themes[0].preferences.space.header = bpy.context.preferences.themes[0].text_editor.space.header ## Temporary
    
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.USERPREF_HT_header.append(toolshelf.drawToggle)
    bpy.types.VIEW3D_MT_editor_menus.append(toolshelf.vpToggleBtn)

    bpy.app.handlers.frame_change_post.append(quickView.overlay_func)
    bpy.app.handlers.depsgraph_update_post.append(key.gizmo_func)

    bpy.types.Scene.set_selection = bpy.props.PointerProperty(type=panels.Set_Selector_Vars)
    bpy.types.Scene.at_time_clipboard = bpy.props.CollectionProperty(type=key.clipboard)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if(kc):
        km = kc.keymaps.new(name='Animation Channels', space_type='EMPTY')
        kmi = km.keymap_items.new(quickView.ABRA_OT_isolate_func.bl_idname, 'LEFTMOUSE', 'RELEASE')
        addon_keymaps.append((km, kmi))

        # These would have CLICK type but it causes selection of channels to cease entirely in 3.6.2
        km = kc.keymaps.new(name='Animation Channels', space_type='EMPTY')
        kmi = km.keymap_items.new(quickView.ABRA_OT_isolate_func.bl_idname, 'LEFTMOUSE', 'DOUBLE_CLICK', shift=1, head=False)
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new(name='Animation Channels', space_type='EMPTY')
        kmi = km.keymap_items.new(quickView.ABRA_OT_isolate_func.bl_idname, 'LEFTMOUSE', 'DOUBLE_CLICK', ctrl=1)
        addon_keymaps.append((km, kmi))

        km = kc.keymaps.new(name='Frames', space_type='EMPTY')
        kmi = km.keymap_items.new(quickView.ABRA_OT_overlay_func.bl_idname, 'SPACE', 'RELEASE')
        addon_keymaps.append((km, kmi))

    print(f"[aT] AbraTools started in {(time.time() - atime)} seconds")

def unregister():
    bpy.context.preferences.themes[0].preferences.space.header = toolshelf.prefsOldHeaderCol

    bpy.types.USERPREF_HT_header.remove(toolshelf.drawToggle)
    bpy.types.VIEW3D_MT_editor_menus.remove(toolshelf.vpToggleBtn)

    bpy.app.handlers.frame_change_post.remove(quickView.overlay_func)
    bpy.app.handlers.depsgraph_update_post.remove(key.gizmo_func)

    try:
        bpy.app.handlers.depsgraph_update_post.remove(key.global_offset_func)
    except ValueError:
        pass

    from .core import api
    api.remove_text()

    del bpy.types.Scene.set_selection
    del bpy.types.Scene.at_time_clipboard
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        
    addon_keymaps.clear()

    print("[aT] AbraTools is no longer running")

if __name__ == "__main__":
    register()