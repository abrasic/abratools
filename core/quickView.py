import bpy, re
from . import api

class ABRA_OT_isolate_func(bpy.types.Operator):
    bl_idname = "screen.at_isolate_function"
    bl_label = "Isolate Curves (Exec)"
    bl_description = "Internal use only"
    bl_options = {"REGISTER"}

    def execute(self, context):
        prefs = bpy.context.preferences.addons["abTools"].preferences
        wm = context.window_manager
        if(context.area.type == "GRAPH_EDITOR"):
            if prefs.isolate_curves:
                bpy.ops.graph.hide(unselected=True)
                return {"FINISHED"}
            else:
                return {'CANCELLED'}
        else:
            return {'CANCELLED'}
    
class ABRA_OT_isolate_curves(bpy.types.Operator):
    bl_idname = "screen.at_isolate_curves"
    bl_label = "Isolate Curves [BETA]"
    bl_description = "While enabled, AbraTools will automatically hide F-Curve channels that aren't selected. This is a beta feature"
    bl_options = {"REGISTER"}

    def execute(self, context):
        prefs = bpy.context.preferences.addons["abTools"].preferences
        prefs.isolate_curves = not prefs.isolate_curves
        return {"FINISHED"}
      
class ABRA_OT_visible_loc(bpy.types.Operator):
    bl_idname = "screen.at_visible_loc"
    bl_label = "Quick View Location"
    bl_description = "Quick operation to only show Location F-Curves"
    bl_options = {"REGISTER"}

    def execute(self, context):
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        bpy.ops.graph.reveal()
        for curve in bpy.context.editable_fcurves:
            match = re.search("location$", curve.data_path)
            curve.hide = False if match else True
            curve.select = False

        area.type = old
                
        return {"FINISHED"}

class ABRA_OT_visible_rot(bpy.types.Operator):
    bl_idname = "screen.at_visible_rot"
    bl_label = "Quick View Rotation"
    bl_description = "Quick operation to only show Euler Rotation F-Curves. Hold Shift + Click to show Quaternion F-Curves"
    bl_options = {"REGISTER"}

    def invoke(self, context, event):
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        bpy.ops.graph.reveal()
        for curve in bpy.context.editable_fcurves:
            if event.shift:
                match = re.search("rotation_quaternion$", curve.data_path)
            else:
                match = re.search("rotation_euler$", curve.data_path)
            curve.hide = False if match else True
            curve.select = False
        
        area.type = old
        return {"FINISHED"}

class ABRA_OT_visible_scl(bpy.types.Operator):
    bl_idname = "screen.at_visible_scl"
    bl_label = "Quick View Scale"
    bl_description = "Quick operation to only show Scale F-Curves"
    bl_options = {"REGISTER"}

    def execute(self, context):
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        bpy.ops.graph.reveal()
        for curve in bpy.context.editable_fcurves:
            match = re.search("scale$", curve.data_path)
            curve.hide = False if match else True
            curve.select = False
                
        area.type = old
        return {"FINISHED"}

class ABRA_OT_visible_keys(bpy.types.Operator):
    bl_idname = "screen.at_visible_keys"
    bl_label = "Quick View Shape Keys"
    bl_description = "Quick operation to only show Shape Key F-Curves"
    bl_options = {"REGISTER"}

    def execute(self, context):
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        bpy.ops.graph.reveal()
        for curve in bpy.context.editable_fcurves:
            match = re.search("^key_blocks\[", curve.data_path)
            curve.hide = False if match else True
            curve.select = False
                
        area.type = old
        return {"FINISHED"}

class ABRA_OT_visible_props(bpy.types.Operator):
    bl_idname = "screen.at_visible_props"
    bl_label = "Quick View Custom Properties"
    bl_description = "Quick operation to only show Custom Property F-Curves"
    bl_options = {"REGISTER"}

    def execute(self, context):
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        bpy.ops.graph.reveal()
        for curve in bpy.context.editable_fcurves:
            match = re.search('\[\"(.*?)\"\]$', curve.data_path)
            curve.hide = False if match else True
            curve.select = False
                
        area.type = old
        return {"FINISHED"}

class ABRA_OT_visible_const(bpy.types.Operator):
    bl_idname = "screen.at_visible_constraint"
    bl_label = "Quick View Constraint Influence"
    bl_description = "Quick operation to only show Custom Property F-Curves"
    bl_options = {"REGISTER"}

    def execute(self, context):
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        bpy.ops.graph.reveal()
        for curve in bpy.context.editable_fcurves:
            match = re.search('influence$', curve.data_path)
            curve.hide = False if match else True
            curve.select = False
                
        area.type = old
        return {"FINISHED"}

cls = (ABRA_OT_isolate_func,ABRA_OT_isolate_curves,ABRA_OT_visible_loc,ABRA_OT_visible_rot,ABRA_OT_visible_scl,ABRA_OT_visible_keys,ABRA_OT_visible_props,ABRA_OT_visible_const,)
