import bpy, re
from bpy.app.handlers import persistent
from . import api

class ABRA_OT_isolate_func(bpy.types.Operator):
    bl_idname = "screen.at_isolate_function"
    bl_label = "Isolate Curves (Exec)"
    bl_description = "Internal use only"
    bl_options = {"REGISTER"}

    def execute(self, context):
        prefs = api.get_preferences()
        wm = context.window_manager
        if(context.area.type == "GRAPH_EDITOR"):
            if prefs.isolate_curves:
                api.dprint("Isolate Curves Execute", col="white")
                bpy.ops.graph.hide(unselected=True)

            if prefs.auto_frame:
                api.dprint("Auto-Frame Execute")
                gre = None
                for winman in bpy.data.window_managers:
                    for window in winman.windows:
                        for area in window.screen.areas:
                            if area.type == 'GRAPH_EDITOR' and area.ui_type != 'DRIVERS':
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
                    #bpy.ops.graph.select_all(action='DESELECT')
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
                    #bpy.ops.graph.select_all(action='DESELECT')

                    # select_all removes selection of the channel, which will cause it to hide the next time isolate curves is enabled.
                    # The workaround I've found is to make a giant selection box to substract all keyframes but keep the channels themselves selected
                    bpy.ops.graph.select_box(mode="SUB",xmin=-2**30,xmax=2**30,ymin=-2**30,ymax=2**30)
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
        prefs = api.get_preferences()
        prefs.isolate_curves = not prefs.isolate_curves
        return {"FINISHED"}

class ABRA_OT_auto_frame(bpy.types.Operator):
    bl_idname = "screen.at_auto_frame"
    bl_label = "Auto Frame"
    bl_description = "While enabled, AbraTools will automatically frame F-Curves into view within the frame range. Works best alongside Isolate Curves. This is a beta feature"
    bl_options = {"REGISTER"}

    def execute(self, context):
        prefs = api.get_preferences()
        prefs.auto_frame = not prefs.auto_frame
        return {"FINISHED"}

class ABRA_OT_auto_overlay(bpy.types.Operator):
    bl_idname = "screen.at_auto_overlay"
    bl_label = "Automatic Overlay"
    bl_description = "While enabled, AbraTools will automatically turn off overlays while animation is playing"
    bl_options = {"REGISTER"}

    def execute(self, context):
        prefs = api.get_preferences()
        prefs.auto_overlay = not prefs.auto_overlay
        return {"FINISHED"}

@persistent
def overlay_func(self, context):
    prefs = api.get_preferences()
    if prefs.auto_overlay:
        isPlaying = bpy.context.screen.is_animation_playing
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.overlay.show_overlays = not isPlaying

class ABRA_OT_goto_keyframe_right(bpy.types.Operator):
    bl_idname = "screen.at_goto_keyframe_right"
    bl_label = "Go to Next Keyframe"
    bl_description = "Smart playhead placement to next keyframe based on FCurve visibility and keyframe selection."
    bl_options = {"REGISTER"}

    def execute(self, context):
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        current = bpy.context.scene.frame_current
        curves = api.get_selected_fcurves()
        current_frame_init = bpy.context.scene.frame_current

        if not curves:
            curves = api.get_visible_fcurves()

        if curves:
            # THIS CODE IS DISGUSTING
            nearest = large_number = 2**30
            ranged = False
            move_range = [-2**30, 2**30]

            api.dprint("GOTO RIGHT STARTED", col="green")
            for curve in curves:
                selected_keys = api.get_selected_keys(curve)
                
                # Atleast one key for each FCurve in the function needs to be selected otherwise the len() on the next if will break. It doesnt matter which one, it will get filtered out eventually
                if selected_keys is None:
                    api.dprint("A selected FCurve has no selected keys. Selecting one automatically...", col="yellow")
                    curve.keyframe_points[0].select_control_point = True
                    selected_keys = api.get_selected_keys(curve)
                    bpy.context.scene.frame_current = current # If you comment this out the function is faster but is less accurate
                
                # Determine the key selection. If one (incl. for each curve) is selected, use standard jump-and-select.
                # If two or more keys are selected for one FCurve, limit the jumping to that range and dont do any sort of selection.
                if ranged or len(selected_keys) > 1:
                    ranged = True
                    api.dprint("More than one key is selected for this curve. Ranged movement will be enabled",col="blue")
                    candidate_range = api.get_range_from_selected_keys()
                    
                    if move_range[0] < candidate_range[0]:
                        move_range[0] = candidate_range[0]
                    if move_range[1] > candidate_range[0]:
                        move_range[1] = candidate_range[1]
                    api.dprint(f"Range is {move_range[0]}, {move_range[1]}")
                
                # Put the playhead on a key to determine the next 
                key_index = api.get_key_index_at_frame(curve, current_frame_init)
                api.dprint(f"The current key index is {key_index}")
                while key_index == -1:
                    frame_before_jump = bpy.context.scene.frame_current
                    bpy.ops.screen.keyframe_jump(next=False)
                    frame_after_jump = bpy.context.scene.frame_current
                    key_index = api.get_key_index_at_frame(curve, bpy.context.scene.frame_current)
                    api.dprint(f"No key on this current frame. Jumping to frame {bpy.context.scene.frame_current} and the key index this time is {key_index}", col="yellow")
                    
                    if frame_before_jump == frame_after_jump: # No more keys to jump towards that direction
                        api.dprint("No more keys in that direction anyways...")
                        key_index = 0
                        break
                    
                next_key_value = curve.keyframe_points[key_index].co[0]
                if len(curve.keyframe_points) <= key_index + 1:
                    if not ranged:
                        api.dprint("End of FCurve detected. Selecting the last key instead...", col="yellow")
                        next_key_value = curve.keyframe_points[key_index].co[0]
                else:
                    next_key_value = curve.keyframe_points[key_index + 1].co[0]
                
                # Determine if obtained value is nearest
                if nearest > next_key_value and next_key_value > current_frame_init:
                    api.dprint(f"NEW NEAREST VALUE CHANGED FROM {nearest} TO {next_key_value}")
                    nearest = next_key_value
                
                api.dprint(f"Decided frame jump is at frame {int(nearest)}",col="purple")
                    
                bpy.context.scene.frame_current = current_frame_init

            # Dont move playhead to large number if nearest value never changed (most likely happens if at the start/end of FCurve)
            if large_number != nearest:
                bpy.context.scene.frame_current = int(nearest)

            # Override selection if range selection is out of start/end boundary
            if ranged:
                if nearest > move_range[1]:
                    api.dprint(f"Overriding minimum range ({move_range[1]}) due to ranged selection", col="yellow")
                    bpy.context.scene.frame_current = int(move_range[0])
                elif nearest < move_range[0]:
                    api.dprint(f"Overriding minimum range ({move_range[1]}) due to ranged selection", col="yellow")
                    bpy.context.scene.frame_current = int(move_range[1])
            if not ranged:
                bpy.ops.graph.select_box(mode="SUB",axis_range=True, xmin=-2**30,xmax=2**30,ymin=-2**30,ymax=2**30, include_handles=False, wait_for_input=False)   
                api.select_keys_on_column(selected_only=True)
        else:
            self.report({"INFO"}, "Unable to jump. Are FCurves visible? Is 'Only Show Selected' on?")

        area.type = old
                
        return {"FINISHED"} 
    
class ABRA_OT_goto_keyframe_left(bpy.types.Operator):
    bl_idname = "screen.at_goto_keyframe_left"
    bl_label = "Go to Previous Keyframe"
    bl_description = "Smart playhead placement to previous keyframe based on FCurve visibility and keyframe selection."
    bl_options = {"REGISTER"}

    def execute(self, context):
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        current = bpy.context.scene.frame_current
        curves = api.get_selected_fcurves()
        current_frame_init = bpy.context.scene.frame_current

        if not curves:
            curves = api.get_visible_fcurves()

        if curves:
            # THIS CODE IS STILL DISGUSTING
            nearest = large_number = -2**30
            ranged = False
            move_range = [-2**30, 2**30]

            api.dprint("GOTO LEFT STARTED", col="green")
            for curve in curves:
                selected_keys = api.get_selected_keys(curve)
                
                # Atleast one key for each FCurve in the function needs to be selected otherwise the len() on the next if will break. It doesnt matter which one, it will get filtered out eventually
                if selected_keys is None:
                    api.dprint("A selected FCurve has no selected keys. Selecting one automatically...", col="yellow")
                    curve.keyframe_points[len(curve.keyframe_points)-1].select_control_point = True
                    selected_keys = api.get_selected_keys(curve)
                    bpy.context.scene.frame_current = current # If you comment this out the function is faster but is less accurate
                
                # Determine the key selection. If one (incl. for each curve) is selected, use standard jump-and-select.
                # If two or more keys are selected for one FCurve, limit the jumping to that range and dont do any sort of selection.
                if ranged or len(selected_keys) > 1:
                    ranged = True
                    api.dprint("More than one key is selected for this curve. Ranged movement will be enabled",col="blue")
                    candidate_range = api.get_range_from_selected_keys()
                    
                    if move_range[0] < candidate_range[0]:
                        move_range[0] = candidate_range[0]
                    if move_range[1] > candidate_range[0]:
                        move_range[1] = candidate_range[1]
                    api.dprint(f"Range is {move_range[0]}, {move_range[1]}")
                
                # Put the playhead on a key to determine the next 
                key_index = api.get_key_index_at_frame(curve, current_frame_init)
                api.dprint(f"The current key index is {key_index}")
                while key_index == -1:
                    frame_before_jump = bpy.context.scene.frame_current
                    bpy.ops.screen.keyframe_jump(next=True)
                    frame_after_jump = bpy.context.scene.frame_current
                    key_index = api.get_key_index_at_frame(curve, bpy.context.scene.frame_current)
                    api.dprint(f"No key on this current frame. Jumping to frame {bpy.context.scene.frame_current} and the key index this time is {key_index}", col="yellow")
                    
                    if frame_before_jump == frame_after_jump: # No more keys to jump towards that direction
                        api.dprint("No more keys in that direction anyways...")
                        key_index = 0
                        break
                    
                next_key_value = curve.keyframe_points[key_index].co[0]
                if key_index == 0:
                    if not ranged:
                        api.dprint("End of FCurve detected. Selecting the last key instead...", col="yellow")
                        next_key_value = curve.keyframe_points[key_index].co[0]
                else:
                    next_key_value = curve.keyframe_points[key_index - 1].co[0]
                
                # Determine if obtained value is nearest
                if nearest < next_key_value and next_key_value < current_frame_init:
                    api.dprint(f"NEW NEAREST VALUE CHANGED FROM {nearest} TO {next_key_value}")
                    nearest = next_key_value
                
                api.dprint(f"Decided frame jump is at frame {int(nearest)}",col="purple")
                    
                bpy.context.scene.frame_current = current_frame_init

            # Dont move playhead to large number if nearest value never changed (most likely happens if at the start/end of FCurve)
            if large_number != nearest:
                bpy.context.scene.frame_current = int(nearest)

            # Override selection if range selection is out of start/end boundary
            if ranged:
                if nearest > move_range[1]:
                    api.dprint(f"Overriding minimum range ({move_range[1]}) due to ranged selection", col="yellow")
                    bpy.context.scene.frame_current = int(move_range[0])
                elif nearest < move_range[0]:
                    api.dprint(f"Overriding minimum range ({move_range[1]}) due to ranged selection", col="yellow")
                    bpy.context.scene.frame_current = int(move_range[1])
            if not ranged:
                bpy.ops.graph.select_box(mode="SUB",axis_range=True, xmin=-2**30,xmax=2**30,ymin=-2**30,ymax=2**30, include_handles=False, wait_for_input=False)   
                api.select_keys_on_column(selected_only=True)
        else:
            self.report({"INFO"}, "Unable to jump. Are FCurves visible? Is 'Only Show Selected' on?")

        area.type = old
                
        return {"FINISHED"} 
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
            if match:
                curve.hide = False
                curve.select = True
            else:
                curve.hide = True
                curve.select = False

        bpy.ops.screen.at_isolate_function()

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
            if match:
                curve.hide = False
                curve.select = True
            else:
                curve.hide = True
                curve.select = False

        bpy.ops.screen.at_isolate_function()
        
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
            if match:
                curve.hide = False
                curve.select = True
            else:
                curve.hide = True
                curve.select = False

        bpy.ops.screen.at_isolate_function()
                
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
            if match:
                curve.hide = False
                curve.select = True
            else:
                curve.hide = True
                curve.select = False

        bpy.ops.screen.at_isolate_function()
                
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
            if match:
                curve.hide = False
                curve.select = True
            else:
                curve.hide = True
                curve.select = False

        bpy.ops.screen.at_isolate_function()
                
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
            if match:
                curve.hide = False
                curve.select = True
            else:
                curve.hide = True
                curve.select = False

        bpy.ops.screen.at_isolate_function()
                
        area.type = old
        return {"FINISHED"}

cls = (ABRA_OT_isolate_func,
ABRA_OT_isolate_curves,
ABRA_OT_auto_frame,
ABRA_OT_auto_overlay,
ABRA_OT_goto_keyframe_left,
ABRA_OT_goto_keyframe_right,
ABRA_OT_visible_loc,
ABRA_OT_visible_rot,
ABRA_OT_visible_scl,
ABRA_OT_visible_keys,
ABRA_OT_visible_props,
ABRA_OT_visible_const,)
