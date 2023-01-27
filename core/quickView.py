import bpy, re
from bpy.app.handlers import persistent
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
                api.dprint("Isolate Curves Execute", col="white")
                bpy.ops.graph.hide(unselected=True)

            if prefs.auto_frame:
                api.dprint("EXEC: Attempting to locate Graph Editor")
                gre = None
                for winman in bpy.data.window_managers:
                    for window in winman.windows:
                        for area in window.screen.areas:
                            if area.type == 'GRAPH_EDITOR':
                                api.dprint("GE found!")
                                gre = area
                                break

                if gre and api.get_selected_fcurves():
                    # Copy context of first found GE
                    api.dprint("Copying GE context...")
                    cc = context.copy()
                    cc['area'] = gre
                    cc['region'] = gre.regions[-1]
                    api.dprint("Area is "+ str(cc['area'].type)+" and region is "+str(cc['region'].type))
                    rn = api.get_frame_range()
                    api.dprint("Frame range is "+str(rn[0])+"-"+str(rn[1]))
                    cr = context.scene.frame_current

                    # Deselect markers and keys for good measure
                    api.dprint("Deselecting keys and markers")
                    bpy.ops.graph.select_all(action='DESELECT')
                    for marker in bpy.context.scene.timeline_markers:
                        if marker.select:
                            marker.select = False

                    # Create left marker
                    api.dprint("Placing left marker")
                    mleft = bpy.context.scene.timeline_markers.new("aTmL", frame=rn[0])

                    # Create right marker
                    api.dprint("Placing right marker")
                    mright = bpy.context.scene.timeline_markers.new("aTmR", frame=rn[1])

                    # Call native operators
                    api.dprint("Selecting keys in range")
                    bpy.ops.graph.select_column(mode='MARKERS_BETWEEN')
                    api.dprint("Framing")
                    bpy.ops.graph.view_selected(cc)

                    # Deselect again
                    api.dprint("Deselecting keys")
                    bpy.ops.graph.select_all(action='DESELECT')
                    bpy.ops.marker.select_all(action='DESELECT')

                    # Delete markers
                    api.dprint("Deleting markers")
                    context.scene.timeline_markers.remove(mleft)
                    context.scene.timeline_markers.remove(mright)

                    api.dprint("DONE")
                
            return {"FINISHED"}
        else:
            return {'CANCELLED'}
class ABRA_OT_isolate_curves(bpy.types.Operator):
    bl_idname = "screen.at_isolate_curves"
    bl_label = "Isolate Curves"
    bl_description = "While enabled, AbraTools will automatically hide F-Curve channels that aren't selected. This is a beta feature"
    bl_options = {"REGISTER"}

    def execute(self, context):
        prefs = bpy.context.preferences.addons["abTools"].preferences
        prefs.isolate_curves = not prefs.isolate_curves
        return {"FINISHED"}

class ABRA_OT_auto_frame(bpy.types.Operator):
    bl_idname = "screen.at_auto_frame"
    bl_label = "Auto Frame"
    bl_description = "While enabled, AbraTools will automatically frame keyframes into view within the frame range. This is a beta feature"
    bl_options = {"REGISTER"}

    def execute(self, context):
        prefs = bpy.context.preferences.addons["abTools"].preferences
        prefs.auto_frame = not prefs.auto_frame
        return {"FINISHED"}

class ABRA_OT_auto_overlay(bpy.types.Operator):
    bl_idname = "screen.at_auto_overlay"
    bl_label = "Automatic Overlay"
    bl_description = "While enabled, AbraTools will automatically turn off overlays while animation is playing"
    bl_options = {"REGISTER"}

    def execute(self, context):
        prefs = bpy.context.preferences.addons["abTools"].preferences
        prefs.auto_overlay = not prefs.auto_overlay
        return {"FINISHED"}

@persistent
def overlay_func(self, context):
    prefs = bpy.context.preferences.addons["abTools"].preferences
    if prefs.auto_overlay:
        isPlaying = bpy.context.screen.is_animation_playing
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.overlay.show_overlays = not isPlaying
      
class ABRA_OT_visible_loc(bpy.types.Operator):
    bl_idname = "screen.at_visible_loc"
    bl_label = "Quick View Location"
    bl_description = "Quick operation to only show location F-Curves"
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
    bl_description = "Quick operation to only show euler rotation F-Curves. Hold Shift + Click to show quaternion F-Curves"
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
    bl_description = "Quick operation to only show scale F-Curves"
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
    bl_description = "Quick operation to only show shape key F-Curves"
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
    bl_description = "Quick operation to only show custom property F-Curves"
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
    bl_description = "Quick operation to only show constraint influence F-Curves"
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

cls = (ABRA_OT_isolate_func,
ABRA_OT_isolate_curves,
ABRA_OT_auto_frame,
ABRA_OT_auto_overlay,
ABRA_OT_visible_loc,
ABRA_OT_visible_rot,
ABRA_OT_visible_scl,
ABRA_OT_visible_keys,
ABRA_OT_visible_props,
ABRA_OT_visible_const,)
