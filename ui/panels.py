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
        if bpy.app.version < (3, 2, 0):
            layout.prop(prefs, "path_calc")
            if prefs.path_calc == "currentAdd":
                layout.prop(prefs, "path_add")
            layout.separator()
            
        else:
            active = bpy.context.active_object
            if active:
                if active.pose:
                    layout.prop(active.pose.animation_visualization.motion_path, "type")
                    if active.pose.animation_visualization.motion_path.type == "RANGE":
                        layout.prop(active.pose.animation_visualization.motion_path, "frame_start")
                        layout.prop(active.pose.animation_visualization.motion_path, "frame_end")
                    if active.pose.animation_visualization.motion_path.type == "CURRENT_FRAME": 
                        layout.prop(active.pose.animation_visualization.motion_path, "frame_before")
                        layout.prop(active.pose.animation_visualization.motion_path, "frame_after")

                    layout.prop(active.pose.animation_visualization.motion_path, "frame_step")
                    layout.prop(active.pose.animation_visualization.motion_path, "range")
                    layout.prop(prefs, "path_loc")
                else:
                    layout.label(text="Active object does not support motion paths.")
            else:
                layout.label(text="No active object is selected.")

 
cls = (ABRA_OT_mpathpanel,)