import bpy

from . import prefs

class ABRA_OT_mpathpanel(bpy.types.Operator):
    bl_label = "Motion Path Settings"
    bl_idname = "message.mpathpanel"
 
    def execute(self, context):
        self.report({'INFO'}, "Changes saved")
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250)
 
    def draw(self, context):
        prefs = bpy.context.preferences.addons["abTools"].preferences
        layout = self.layout
        layout.prop(prefs, "path_calc")
        if prefs.path_calc == "currentAdd":
            layout.prop(prefs, "path_add")
        layout.separator()
        layout.prop(prefs, "path_loc")
 
cls = (ABRA_OT_mpathpanel,)