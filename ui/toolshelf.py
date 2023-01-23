from linecache import lazycache
import bpy 

from ..core import api, key, quickView
from .icons import icons_coll

prefsHeaderOld = None
prefsBodyOld = None
prefsSidebarOld = None
prefsOldHeaderCol = bpy.context.preferences.themes[0].preferences.space.header[:]

ic = icons_coll["icons"]
ic_logo = ic["logo"]

ic_auto_overlay = ic["auto_overlay"]
ic_bake_on_nths = ic["bake_on_nths"]
ic_copy_keys = ic["copy_keys"]
ic_key_timing = ic["copy_key_timing"]
ic_create_path = ic["create_path"]
ic_cursor_to_selected = ic["cursor_to_selected"]
ic_delete_keys = ic["delete_keys"]
ic_delete_path = ic["delete_path"]
ic_isolate_curves = ic["isolate_curves"]
ic_key_all_shapes = ic["key_all_shapes"]
ic_key_selected = ic["key_selected"]
ic_key_visible = ic["key_visible"]
ic_key_whole_armature = ic["key_whole_armature"]
ic_paste_keys = ic["paste_keys"]
ic_range_to_selection = ic["range_to_selection"]
ic_retime_scene = ic["retime_scene"]
ic_select_children = ic["select_children"]
ic_select_mirror = ic["select_mirror"]
ic_select_parent = ic["select_parent"]
ic_select_siblings = ic["select_siblings"]
ic_selection_sets = ic["selection_sets"]
ic_swap_rig_mode = ic["swap_rig_mode"]
ic_toggle_cursor_pivot = ic["toggle_cursor_pivot"]
ic_view_const = ic["view_const"]
ic_view_loc = ic["view_loc"]
ic_view_props = ic["view_props"]
ic_view_rot = ic["view_rot"]
ic_view_scale = ic["view_scale"]
ic_view_shapes = ic["view_shapes"]


class ABRA_OT_togglePrefs(bpy.types.Operator):
    bl_idname      = "at.toggleprefs"
    bl_label       = ""
    bl_description = "Toggles the AbraTools toolshelf"

    def execute(self, context):
        abraOn = bpy.context.preferences.addons["abTools"].preferences.abraon
        if abraOn == False:
            writeOnPrefs()
        else:  
            restorePrefs()

        return {'FINISHED'}

def writeOnPrefs():
    """Overrides preferences header for AbraTools usage."""
    
    prefs = bpy.context.preferences.addons["abTools"].preferences
    
    if prefs.abraon == True:
        return None

    
    # Store native prefs content while aT is in use.
    global prefsHeaderOld, prefsBodyOld, prefsSidebarOld
    
    prefsHeaderOld = bpy.types.USERPREF_HT_header.draw
    bpy.types.USERPREF_HT_header.draw = prefsHeaderWrite
    
    prefsBodyOld = bpy.types.USERPREF_PT_addons.draw
    bpy.types.USERPREF_PT_addons.draw = prefsBodyWrite
        
    prefsSidebarOld = bpy.types.USERPREF_PT_navigation_bar.draw
    bpy.types.USERPREF_PT_navigation_bar.draw = prefsSidebarWrite

    bpy.context.preferences.themes[0].preferences.space.header = prefs.header_col
    
    prefs.abraon = True
    
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if(area.type == 'PREFERENCES'):
                if not bpy.context.preferences.active_section == "ADDONS": ## This needs to check otherwise the interface wont draw
                    bpy.context.preferences.active_section = "ADDONS"
                area.tag_redraw()

    return None
    
def drawToggle(self, context):
    bpy.context.preferences.addons["abTools"].preferences.abraon = False
    self.layout.operator("at.toggleprefs",text="",icon_value=ic_logo.icon_id)

def updateHeader(self, context):
    bpy.context.preferences.themes[0].preferences.space.header = self.header_col

def restorePrefs():
    """Restores original preferences window when AbraTools is toggled off."""

    prefs = bpy.context.preferences.addons["abTools"].preferences
    if prefs.abraon == False:
        return None
    
    global prefsBodyOld, prefsSidebarOld, prefsHeaderOld
    bpy.types.USERPREF_PT_addons.draw = prefsBodyOld
    prefsBodyOld = None 

    bpy.types.USERPREF_PT_navigation_bar.draw = prefsSidebarOld
    prefsSidebarOld = None 

    bpy.types.USERPREF_HT_header.draw = prefsHeaderOld
    prefsHeaderOld = None 

    bpy.context.preferences.themes[0].preferences.space.header = bpy.context.preferences.themes[0].text_editor.space.header ## Temporary

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if(area.type == 'PREFERENCES'):
                area.tag_redraw()
                
    prefs.abraon=False
    return None

def prefsHeaderWrite(self, context):
    """Draw aT header and tools"""
    prefs = bpy.context.preferences.addons["abTools"].preferences
    layout = self.layout

    row = layout.row()
    row.template_header()
    layout = self.layout
    layout.scale_x = prefs.button_width

    ## QUICK VIEW ##
    if (prefs.vis_isolate):
        layout.operator(quickView.ABRA_OT_isolate_curves.bl_idname, text='', depress=prefs.isolate_curves, icon_value=ic_isolate_curves.icon_id)
    if (prefs.vis_overlay):
        layout.operator(quickView.ABRA_OT_auto_overlay.bl_idname, text='', depress=prefs.auto_overlay, icon_value=ic_auto_overlay.icon_id)
    if (prefs.vis_viewloc):
        layout.operator(quickView.ABRA_OT_visible_loc.bl_idname, text='', icon_value=ic_view_loc.icon_id)
    if (prefs.vis_viewrot):
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator(quickView.ABRA_OT_visible_rot.bl_idname, text='', icon_value=ic_view_rot.icon_id)
        layout.operator_context = "EXEC_DEFAULT"
    if (prefs.vis_viewscl):
        layout.operator(quickView.ABRA_OT_visible_scl.bl_idname, text='', icon_value=ic_view_scale.icon_id)
    if (prefs.vis_viewshkey):
        layout.operator(quickView.ABRA_OT_visible_keys.bl_idname, text='', icon_value=ic_view_shapes.icon_id)
    if (prefs.vis_viewprops):
        layout.operator(quickView.ABRA_OT_visible_props.bl_idname, text='', icon_value=ic_view_props.icon_id)
    if (prefs.vis_viewinfl):
        layout.operator(quickView.ABRA_OT_visible_const.bl_idname, text='', icon_value=ic_view_const.icon_id)

    ## KEYING ##
    if (prefs.vis_keysel):  
        layout.operator(key.ABRA_OT_key_selected.bl_idname, text='', icon_value=ic_key_selected.icon_id)
    if (prefs.vis_keyvis): 
        layout.operator(key.ABRA_OT_key_visible.bl_idname, text='', icon_value=ic_key_visible.icon_id)
    if (prefs.vis_keycopy):
        layout.operator(key.ABRA_OT_key_copy.bl_idname, text='', icon_value=ic_copy_keys.icon_id)
    if (prefs.vis_keypaste): 
        layout.operator(key.ABRA_OT_key_paste.bl_idname, text='', icon_value=ic_paste_keys.icon_id)
    if (prefs.vis_keydelete): 
        layout.operator(key.ABRA_OT_key_delete.bl_idname, text='', icon_value=ic_delete_keys.icon_id)
    if (prefs.vis_keybake): 
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator(key.ABRA_OT_bake_keys.bl_idname, text='', icon_value=ic_bake_on_nths.icon_id)
        layout.operator_context = "EXEC_DEFAULT"
    if (prefs.vis_keytiming): 
        layout.operator(key.ABRA_OT_key_timing.bl_idname, text='', icon_value=ic_key_timing.icon_id)
    if (prefs.vis_keyshape): 
        layout.operator(key.ABRA_OT_key_shapekeys.bl_idname, text='', icon_value=ic_key_all_shapes.icon_id)
    if (prefs.vis_keyarmature): 
        layout.operator(key.ABRA_OT_key_armature.bl_idname, text='', icon_value=ic_key_whole_armature.icon_id)
    if (prefs.vis_keyretime): 
        layout.operator(key.ABRA_OT_key_retime.bl_idname, text='', icon_value=ic_retime_scene.icon_id)

    ## TANGENTS ## 
    if (prefs.vis_tanfree): 
        layout.operator(key.ABRA_OT_tangent_free.bl_idname, text='', icon="HANDLE_FREE")
    if (prefs.vis_tanaligned): 
        layout.operator(key.ABRA_OT_tangent_aligned.bl_idname, text='', icon="HANDLE_ALIGNED")
    if (prefs.vis_tanvector): 
        layout.operator(key.ABRA_OT_tangent_vector.bl_idname, text='', icon="HANDLE_VECTOR")
    if (prefs.vis_tanauto): 
        layout.operator(key.ABRA_OT_tangent_auto.bl_idname, text='', icon="HANDLE_AUTO")
    if (prefs.vis_tanautoclamp): 
        layout.operator(key.ABRA_OT_tangent_autoclamp.bl_idname, text='', icon="HANDLE_AUTOCLAMPED")

    ## SELECTION ##
    layout.operator_context = "INVOKE_DEFAULT"
    if (prefs.vis_selchild): 
        layout.operator(key.ABRA_OT_select_children.bl_idname, text='', icon_value=ic_select_children.icon_id)
    if (prefs.vis_selparent): 
        layout.operator(key.ABRA_OT_select_parent.bl_idname, text='', icon_value=ic_select_parent.icon_id)
    if (prefs.vis_selsiblings): 
        layout.operator(key.ABRA_OT_select_siblings.bl_idname, text='', icon_value=ic_select_siblings.icon_id)
    if (prefs.vis_selmirror): 
        layout.operator(key.ABRA_OT_select_mirror.bl_idname, text='', icon_value=ic_select_mirror.icon_id)
    if (prefs.vis_cursortosel): 
        layout.operator(key.ABRA_OT_cursor_to_selected.bl_idname, text='', icon_value=ic_cursor_to_selected.icon_id)
    if (prefs.vis_toggle_cursor): 
        layout.operator(key.ABRA_OT_toggle_cursor_pivot.bl_idname, text='', icon_value=ic_toggle_cursor_pivot.icon_id)
    if (prefs.vis_selsets): 
        layout.operator(key.ABRA_OT_selection_sets.bl_idname, text='', icon_value=ic_selection_sets.icon_id)
    if (prefs.vis_selswaprigmode): 
        layout.operator(key.ABRA_OT_swap_rig_mode.bl_idname, text='', icon_value=ic_swap_rig_mode.icon_id)
    layout.operator_context = "EXEC_DEFAULT"

    ## OTHER ##
    if (prefs.vis_rangesel): 
        layout.operator(key.ABRA_OT_range_to_selection.bl_idname, text='', icon_value=ic_range_to_selection.icon_id)
    if (prefs.vis_keypath): 
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator(key.ABRA_OT_tangent_keypath.bl_idname, text='', icon_value=ic_create_path.icon_id)
        layout.operator(key.ABRA_OT_tangent_keypathclear.bl_idname, text='', icon_value=ic_delete_path.icon_id)
        layout.operator_context = "EXEC_DEFAULT"

    layout.separator_spacer()
    
    toggle = layout.column()
    toggle.alert = True
    toggle.operator("at.toggleprefs",text="",icon='PANEL_CLOSE')

    return 
    
def prefsBodyWrite(self, context):
    """Draw aT body (visibility options and settings)"""

    layout = self.layout
    prefs = bpy.context.preferences.addons["abTools"].preferences
    row = layout.box()
    fill = row.split(factor=0.75)
    col = fill.column()
    if (prefs.toolshelf_pages == "home"):
        col.label(text="Welcome to the AbraTools Toolshelf!")
        col.label(text="Here you can access header tools and change how the header looks!")
        col.label(text="To utilize AbraTools, shrink this panel so you only see the header!")

        col.separator()

        col.operator("wm.url_open", text="Documentation").url = "https://docs.abx.gg"
        col.operator("wm.url_open", text="GitHub").url = "https://github.com/abrasic/abratools"
    if (prefs.toolshelf_pages == "quickview"):
        col.prop(prefs, "vis_isolate", icon_value=ic_isolate_curves.icon_id)
        col.prop(prefs, "vis_overlay", icon_value=ic_auto_overlay.icon_id)
        col.prop(prefs, "vis_viewloc", icon_value=ic_view_loc.icon_id)
        col.prop(prefs, "vis_viewrot", icon_value=ic_view_rot.icon_id)
        col.prop(prefs, "vis_viewscl", icon_value=ic_view_scale.icon_id)
        col.prop(prefs, "vis_viewshkey", icon_value=ic_view_shapes.icon_id)
        col.prop(prefs, "vis_viewprops", icon_value=ic_view_props.icon_id)
        col.prop(prefs, "vis_viewinfl", icon_value=ic_view_const.icon_id)
    if (prefs.toolshelf_pages == "fastkey"):
        col.prop(prefs, "vis_keysel", icon_value=ic_key_selected.icon_id)
        col.prop(prefs, "vis_keyvis", icon_value=ic_key_visible.icon_id)
        col.prop(prefs, "vis_keycopy", icon_value=ic_copy_keys.icon_id)
        col.prop(prefs, "vis_keypaste", icon_value=ic_paste_keys.icon_id)
        col.prop(prefs, "vis_keydelete", icon_value=ic_delete_keys.icon_id)
        col.prop(prefs, "vis_keybake", icon_value=ic_bake_on_nths.icon_id)
        col.prop(prefs, "vis_keytiming", icon_value=ic_key_timing.icon_id)
        col.prop(prefs, "vis_keyshape", icon_value=ic_key_all_shapes.icon_id)
        col.prop(prefs, "vis_keyarmature", icon_value=ic_key_whole_armature.icon_id)
        col.prop(prefs, "vis_keyretime", icon_value=ic_retime_scene.icon_id)
    if (prefs.toolshelf_pages == "tangents"):
        col.prop(prefs, "vis_tanfree", icon="HANDLE_FREE")
        col.prop(prefs, "vis_tanaligned", icon="HANDLE_ALIGNED")
        col.prop(prefs, "vis_tanvector", icon="HANDLE_VECTOR")
        col.prop(prefs, "vis_tanauto", icon="HANDLE_AUTO")
        col.prop(prefs, "vis_tanautoclamp", icon="HANDLE_AUTOCLAMPED")
    if (prefs.toolshelf_pages == "selection"):
        col.prop(prefs, "vis_selchild", icon_value=ic_select_children.icon_id)
        col.prop(prefs, "vis_selparent", icon_value=ic_select_parent.icon_id)
        col.prop(prefs, "vis_selsiblings", icon_value=ic_select_siblings.icon_id)
        col.prop(prefs, "vis_selmirror", icon_value=ic_select_parent.icon_id)
        col.prop(prefs, "vis_cursortosel", icon_value=ic_cursor_to_selected.icon_id)
        col.prop(prefs, "vis_toggle_cursor", icon_value=ic_toggle_cursor_pivot.icon_id)
        col.prop(prefs, "vis_selsets", icon_value=ic_selection_sets.icon_id)
        col.prop(prefs, "vis_selswaprigmode", icon_value=ic_swap_rig_mode.icon_id)
    if (prefs.toolshelf_pages == "other"):
        col.prop(prefs, "vis_rangesel", icon_value=ic_range_to_selection.icon_id)
        col.prop(prefs, "vis_keypath", icon_value=ic_create_path.icon_id)
    if (prefs.toolshelf_pages == "settings"):
        col.prop(prefs, "header_col")
        col.prop(prefs, "button_width")
        col.separator()
        col.label(text="Third-party Addons:")
        addon = col.grid_flow(columns=2)
        if api.is_addon_enabled("Copy_Timing_and_Ease"):
            addon.label(text="Copy Timing and Ease (INSTALLED)", icon="CHECKBOX_HLT")
        else:
            addon.label(text="Copy Timing and Ease", icon="CHECKBOX_DEHLT")
        addon.operator("wm.url_open", text="By Blastframe | Click to Buy", icon="URL").url = "https://blendermarket.com/products/copy-timing-and-ease"

        addon = col.grid_flow(columns=2)
        if api.is_addon_enabled("copy_global_transform"):
            addon.label(text="Copy Global Transform (INSTALLED)", icon="CHECKBOX_HLT")
        else:
            addon.label(text="Copy Global Transform", icon="CHECKBOX_DEHLT")
        addon.label(text="Native Add-on")

        addon = col.grid_flow(columns=2)
        if api.is_addon_enabled("bone_selection_sets"):
            addon.label(text="Bone Selection Sets (INSTALLED)", icon="CHECKBOX_HLT")
        else:
            addon.label(text="Bone Selection Sets", icon="CHECKBOX_DEHLT")
        addon.label(text="Native Add-on")

        col.separator()
        col.label(text="Some tools require third-party addons in order to use", icon="INFO")
        col.label(text="We are not affiliated nor endorsed by these addons", icon="INFO")

        col.separator()
        col.prop(prefs, "dev_debug")

    layout.label(text="aT | alpha6")

    return 
    
def prefsSidebarWrite(self, context):
    """Draw sidebar tabs"""
    layout = self.layout
    prefs = bpy.context.preferences.addons["abTools"].preferences

    if not context.space_data.show_region_header:
        exit = layout.column()
        exit.alert = True
        exit.operator("at.toggleprefs",text="Exit",icon='PANEL_CLOSE')
        layout.separator()

    tabs = layout.column()
    tabs.scale_y = 1.3
    tabs.prop(prefs, "toolshelf_pages", expand=True)
    return 
    
cls = (ABRA_OT_togglePrefs,)