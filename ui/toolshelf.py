import bpy 

from ..core import key, quickView
from .icons import icons_coll

prefsHeaderOld = None
prefsBodyOld = None
prefsSidebarOld = None
prefsOldHeaderCol = bpy.context.preferences.themes[0].preferences.space.header[:]

class ABRA_OT_togglePrefs(bpy.types.Operator):
    bl_idname      = "at.toggleprefs"
    bl_label       = ""
    bl_description = "Toggles the AbraTools toolshelf"

    def execute(self, context):
        abraOn = bpy.context.preferences.addons["abTools"].preferences.abraon
        print("EXEC" + str(abraOn))
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
                area.tag_redraw()

    return None
    
def drawToggle(self, context):
    bpy.context.preferences.addons["abTools"].preferences.abraon = False
    ic = icons_coll["icons"]
    logo = ic["logo"]
    self.layout.operator("at.toggleprefs",text="",icon_value=logo.icon_id)

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

    ## QUICK VIEW ##
    if (prefs.vis_viewloc):
        layout.operator(quickView.ABRA_OT_visible_loc.bl_idname, text='', icon="CON_LOCLIMIT")
    if (prefs.vis_viewrot):
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator(quickView.ABRA_OT_visible_rot.bl_idname, text='', icon="CON_ROTLIMIT")
        layout.operator_context = "EXEC_DEFAULT"
    if (prefs.vis_viewscl):
        layout.operator(quickView.ABRA_OT_visible_scl.bl_idname, text='', icon="CON_SIZELIMIT")
    if (prefs.vis_viewshkey):
        layout.operator(quickView.ABRA_OT_visible_keys.bl_idname, text='', icon="SHAPEKEY_DATA")
    if (prefs.vis_viewprops):
        layout.operator(quickView.ABRA_OT_visible_props.bl_idname, text='', icon="PROPERTIES")
    if (prefs.vis_viewinfl):
        layout.operator(quickView.ABRA_OT_visible_const.bl_idname, text='', icon="CONSTRAINT")

    ## KEYING ##
    layout.separator()

    if (prefs.vis_keysel):  
        layout.operator(key.ABRA_OT_key_selected.bl_idname, text='', icon="KEYFRAME")
    if (prefs.vis_keyvis): 
        layout.operator(key.ABRA_OT_key_visible.bl_idname, text='', icon="KEYFRAME_HLT")
    if (prefs.vis_keycopy):
        layout.operator(key.ABRA_OT_key_copy.bl_idname, text='', icon="COPYDOWN")
    if (prefs.vis_keypaste): 
        layout.operator(key.ABRA_OT_key_paste.bl_idname, text='', icon="PASTEDOWN")
    if (prefs.vis_keyshape): 
        layout.operator(key.ABRA_OT_key_shapekeys.bl_idname, text='', icon="MOD_LINEART")
    if (prefs.vis_keyarmature): 
        layout.operator(key.ABRA_OT_key_armature.bl_idname, text='', icon="OUTLINER_DATA_ARMATURE")

    ## TANGENTS ## 
    layout.separator()
    
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

    ## OTHER ##
    layout.separator()

    if (prefs.vis_rangesel): 
        layout.operator(key.ABRA_OT_range_to_selection.bl_idname, text='', icon="FCURVE")
    if (prefs.vis_keypath): 
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator(key.ABRA_OT_tangent_keypath.bl_idname, text='', icon="FORCE_VORTEX")
        layout.operator(key.ABRA_OT_tangent_keypathclear.bl_idname, text='', icon="X")
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
    col = row.column()
    if (prefs.toolshelf_pages == "home"):
        col.label(text="Welcome to the AbraTools Toolshelf!")
        col.label(text="Here you can access header tools and change how the header looks!")
        col.label(text="To utilize AbraTools, shrink this panel so you only see the header!")

        col.separator()

        col.operator("wm.url_open", text="Documentation").url = "https://docs.abx.gg"
        col.operator("wm.url_open", text="GitHub").url = "https://github.com/abrasic/abratools"
    if (prefs.toolshelf_pages == "quickview"):
        col.prop(prefs, "vis_viewloc")
        col.prop(prefs, "vis_viewrot")
        col.prop(prefs, "vis_viewscl")
        col.prop(prefs, "vis_viewshkey")
        col.prop(prefs, "vis_viewprops")
        col.prop(prefs, "vis_viewinfl")
    if (prefs.toolshelf_pages == "fastkey"):
        col.prop(prefs, "vis_keysel")
        col.prop(prefs, "vis_keyvis")
        col.prop(prefs, "vis_keycopy")
        col.prop(prefs, "vis_keypaste")
        col.prop(prefs, "vis_keyshape")
        col.prop(prefs, "vis_keyarmature")
    if (prefs.toolshelf_pages == "tangents"):
        col.prop(prefs, "vis_tanfree")
        col.prop(prefs, "vis_tanaligned")
        col.prop(prefs, "vis_tanvector")
        col.prop(prefs, "vis_tanauto")
        col.prop(prefs, "vis_tanautoclamp")
    if (prefs.toolshelf_pages == "other"):
        col.prop(prefs, "vis_rangesel")
        col.prop(prefs, "vis_keypath")
    if (prefs.toolshelf_pages == "settings"):
        col.prop(prefs, "header_col")

    layout.label(text="aT | alpha2")

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