import bpy
from bpy.app.handlers import persistent
from . import api

# $$\   $$\ $$$$$$$$\ $$\     $$\ $$$$$$\ $$\   $$\  $$$$$$\  
# $$ | $$  |$$  _____|\$$\   $$  |\_$$  _|$$$\  $$ |$$  __$$\ 
# $$ |$$  / $$ |       \$$\ $$  /   $$ |  $$$$\ $$ |$$ /  \__|
# $$$$$  /  $$$$$\      \$$$$  /    $$ |  $$ $$\$$ |$$ |$$$$\ 
# $$  $$<   $$  __|      \$$  /     $$ |  $$ \$$$$ |$$ |\_$$ |
# $$ |\$$\  $$ |          $$ |      $$ |  $$ |\$$$ |$$ |  $$ |
# $$ | \$$\ $$$$$$$$\     $$ |    $$$$$$\ $$ | \$$ |\$$$$$$  |
# \__|  \__|\________|    \__|    \______|\__|  \__| \______/ 

class ABRA_OT_key_selected(bpy.types.Operator):
    bl_idname = "screen.at_quick_insert"
    bl_label = "Key Selected Curves"
    bl_description = "Inserts a key on the playhead for all selected F-Curves"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        if api.get_selected_fcurves():
            bpy.ops.graph.keyframe_insert(type='SEL')

        area.type = old
        return {"FINISHED"}

class ABRA_OT_key_visible(bpy.types.Operator):
    bl_idname = "screen.at_quick_insert_all"
    bl_label = "Key Visible Curves"
    bl_description = "Inserts a key on the playhead on all visible F-Curves"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        if api.get_visible_fcurves():
            bpy.ops.graph.keyframe_insert(type='ALL')

        area.type = old
        return {"FINISHED"}

class ABRA_OT_key_copy(bpy.types.Operator):
    bl_idname = "screen.at_copy_keys"
    bl_label = "Copy Keys"
    bl_description = "Copies any visible keyframes on playhead to a clipboard. Note that this will overwrite your current clipboard and any selected keyframes not on the playhead"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        api.key_clipboard(self, type="copy")
        return {"FINISHED"}

class ABRA_OT_key_paste(bpy.types.Operator):
    bl_idname = "screen.at_paste_keys"
    bl_label = "Paste Keys"
    bl_description = "Simple operator to paste any keyframes from clipboard"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        api.key_clipboard(self, type="paste")
        return {"FINISHED"}
    
class ABRA_OT_key_copy_pose(bpy.types.Operator):
    bl_idname = "screen.at_copy_pose"
    bl_label = "Copy Pose"
    bl_description = "Copies the pose of all visible bones"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if bpy.context.mode == "POSE":
            # Store old selection
            sel = bpy.context.selected_pose_bones

            # Select all and copy pose from visible bones
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.copy()

            # Retrieve old selection
            bpy.ops.pose.select_all(action='DESELECT')
            for bone in sel:
                bone.bone.select = True

            return {"FINISHED"} 
        else:
            self.report({"INFO"}, "This tool only works in Pose Mode.")
            return {"CANCELLED"}
        
class ABRA_OT_key_paste_pose(bpy.types.Operator):
    bl_idname = "screen.at_paste_pose"
    bl_label = "Paste Pose"
    bl_description = "Paste pose data from buffer, if any. This does the same as 'Pose > Paste Pose'. Shift + Click to paste flipped pose"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if bpy.context.mode == "POSE":
            bpy.ops.pose.paste(flipped=event.shift, selected_mask=True)
            return {"FINISHED"}
        else:
            self.report({"INFO"}, "This tool only works in Pose Mode.")
            return {"CANCELLED"}

class ABRA_OT_key_delete(bpy.types.Operator):
    bl_idname = "screen.at_delete_keys"
    bl_label = "Delete Keys"
    bl_description = "Deletes selected keys. If nothing is selected, keys from the playhead will be deleted instead"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        api.key_clipboard(self, type="delete")
        return {"FINISHED"}

class ABRA_OT_share_common_key_timing(bpy.types.Operator):
    bl_idname = "screen.at_common_key_timing"
    bl_label = "Share Common Key Timing"
    bl_description = "Inserts keys onto selected objects that will match the common timing between eachother"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        prefs = api.get_preferences()
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        range = api.get_frame_range()
        area.spaces[0].dopesheet.show_only_selected = True

        bpy.ops.graph.reveal()
        curves = api.get_visible_fcurves()

        # Grab frame numbers that contain keys in current range
        timings = []

        if not api.fcurve_overload(curves):
            for curve in curves:
                for key in curve.keyframe_points:
                    co = key.co.x
                    if co not in timings and co >= range[0] and co <= range[1]:
                        timings.append(co)

            for curve in curves:
                for i, time in enumerate(timings):
                    curve.keyframe_points.insert(frame=time, value = curve.evaluate(int(time)))
        else:
            area.type = old
            self.report({"ERROR"}, f"Preventing overload ({prefs.fcurve_scan_limit} FCurves max, {len(curves)} active)")
        area.type = old

        return{"FINISHED"}

class ABRA_OT_share_active_key_timing(bpy.types.Operator):
    bl_idname = "screen.at_active_key_timing"
    bl_label = "Share Active Key Timing"
    bl_description = "Adds keys onto selected objects that will match the timing of the active object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        prefs = api.get_preferences()
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'
        range = api.get_frame_range()
        area.spaces[0].dopesheet.show_only_selected = True

        active = []
        objs = []
        active_curves = []
        non_active_curves = []

        if bpy.context.mode == "OBJECT":
            active = bpy.context.active_object
            objs = bpy.context.selected_objects

            try:
                active_curves = active.animation_data.action.fcurves
            except AttributeError:
                return {"CANCELLED"}

            for ob in objs:
                if ob != active:
                    for fcurve in ob.animation_data.action.fcurves:
                        non_active_curves.append(fcurve)

        elif bpy.context.mode == "POSE":
            active = bpy.context.active_pose_bone
            objs = bpy.context.selected_pose_bones

            arm_list = []
            for ob in bpy.context.selected_objects:
                if ob.type == "ARMATURE":
                    for fcurve in ob.animation_data.action.fcurves:
                        arm_list.append(fcurve)          

            active_curves = [f for f in arm_list if active.name in f.data_path.split('"')[1]]

            bone_names_list = [b.name for b in objs if b != active]
            non_active_curves = [f for f in arm_list if f.data_path.split('"')[1] in bone_names_list]

        timings = [] 
        if not api.fcurve_overload(active_curves + non_active_curves):
            for curve in active_curves: # Keyframe numbers from active object
                for key in curve.keyframe_points:
                    co = key.co.x
                    if co not in timings and co >= range[0] and co <= range[1]:
                        timings.append(co)

            for curve in non_active_curves: # Non-active object curves
                for time in timings:
                    curve.keyframe_points.insert(frame=time, value = curve.evaluate(int(time)))
        else:
            area.type = old
            self.report({"ERROR"}, f"Preventing overload ({prefs.fcurve_scan_limit} FCurves max, {len(active_curves + non_active_curves)} active)")   

        if bpy.context.mode == "OBJECT":
            bpy.ops.object.select_all(action='DESELECT')
            objs[-1].select_set(True)   
            bpy.context.view_layer.objects.active = objs[-1].bone
        elif bpy.context.mode == "POSE":
            bpy.ops.pose.select_all(action='DESELECT')
            for ob in objs:
                if ob != active:
                    ob.bone.select = True

        area.type = old
        return {"FINISHED"}


class ABRA_OT_key_shapekeys(bpy.types.Operator):
    bl_idname = "screen.at_key_shapes_all"
    bl_label = "Key All Shape Keys"
    bl_description = "Inserts a keyframe on selected object's shape keys. Useful for blocking out facial expessions"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if bpy.context.mode == "OBJECT":
            for obj in bpy.context.selected_objects:
                if obj.type == "MESH":
                    for key in obj.data.shape_keys.key_blocks:
                        if (key != "Basis"):
                            key.keyframe_insert(data_path="value")

                for window in bpy.context.window_manager.windows:
                    for area in window.screen.areas:
                        area.tag_redraw()
        return {"FINISHED"}

class ABRA_OT_key_armature(bpy.types.Operator):
    bl_idname = "screen.at_key_armature"
    bl_label = "Key Whole Armature"
    bl_description = "Keys every single bone on the armature. This saves you a couple [A] and [I] keypresses"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        oldSet = None
        if bpy.context.mode == "POSE":
            oldSet = bpy.context.scene.keying_sets.active
            bpy.context.scene.keying_sets.active
            for obj in bpy.context.selected_objects:
                if obj.type == "ARMATURE":
                    bpy.context.scene.keying_sets_all.active = bpy.context.scene.keying_sets_all["Whole Character"]
                    bpy.ops.anim.keyframe_insert_menu(type='__ACTIVE__') 

            bpy.context.scene.keying_sets_all.active = oldSet

            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
                
        return {"FINISHED"}

class ABRA_OT_key_retime(bpy.types.Operator):
    bl_idname = "screen.at_key_retime"
    bl_label = "Retime Scene"
    bl_description = "Adds a specified amount of space between keys by translating keys and markers automatically"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        prefs = api.get_preferences()
        prefs.retime_framestart = context.scene.frame_current
        bpy.ops.message.retimepanel("INVOKE_DEFAULT")
        return {"FINISHED"}

class ABRA_OT_bake_keys(bpy.types.Operator):
    bl_idname = "screen.at_bake_keys"
    bl_label = "Bake Keys"
    bl_description = "Adds and replaces keys for all selected objects' F-Curves for every nth frame, inside of the specified frame range. Shift + Click this tool to modify frame step."
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if event.shift:
            bpy.ops.message.bakepanel("INVOKE_DEFAULT")
            return {"FINISHED"}
        else:
            # Set to GE
            area = bpy.context.area
            old_type = area.type
            area.type = 'GRAPH_EDITOR'

            # Get data ready for bake
            prefs = api.get_preferences()
            range = api.get_frame_range()
            frame_const = bpy.context.scene.frame_current
            step = prefs.bake_framestep

            # Basic checks
            if api.get_visible_fcurves() is None:
                self.report({"INFO"}, "At least one F-Curve needs to be visible")
                area.type = old_type
                return {"CANCELLED"}

            if bpy.context.mode == "POSE" or bpy.context.mode == "OBJECT":
                pass
            else:
                self.report({"INFO"}, "Unsupported mode. You must be in either Object or Pose mode.")
                area.type = old_type
                return {"CANCELLED"}

            # Begin inserting keyframes by moving playhead on every nth frame until playhead reaches end of range.
            api.dprint("BAKING RANGE ("+str(range[0])+"-"+str(range[1])+")", col="red")
            # Deselect for interpolation change later
            bpy.ops.graph.select_all(action='DESELECT')

            # NLA Bake
            bpy.ops.graph.reveal()
            bpy.ops.nla.bake(frame_start=range[0], frame_end=range[1], bake_types={bpy.context.mode}, use_current_action = True, clean_curves=False)

            # Change interpolation type of new keys
            bpy.ops.graph.interpolation_type(type=prefs.bake_type)
            bpy.ops.graph.handle_type(type=prefs.bake_handle)

            # Deselect everything one final time
            bpy.ops.graph.select_all(action='DESELECT')

            api.dprint("Initial bake complete. Moving to range start")
            bpy.context.scene.frame_current = range[0]
            ref = bpy.context.scene.frame_current

            wm = bpy.context.window_manager
            wm.progress_begin(range[0], range[1])
            while bpy.context.scene.frame_current < range[1]:
                s = 0
                bpy.context.scene.frame_current+=1
                wm.progress_update(bpy.context.scene.frame_current)
                s += bpy.context.scene.frame_current - ref
                if s == 0:
                    api.dprint("There are no more keyframes left to bake", col="yellow")
                    break
                api.dprint("Playhead jumped to frame " + str(bpy.context.scene.frame_current) + " with a total offset of "+ str(s))
                if s % step == 0:
                    api.dprint("Current frame is divisible. Skipping...")
                else:
                    api.dprint("Current frame is NOT divisible. Deleting keys on "+str(bpy.context.scene.frame_current)+")", col="yellow")
                    bpy.ops.graph.select_column(mode='CFRA')
                    bpy.ops.graph.delete(confirm=False)
            wm.progress_end()

            bpy.context.scene.frame_current = frame_const

            # Remove overalpping keys incase of a double bake (dumb workaround)
            bpy.ops.graph.select_all(action='SELECT')
            bpy.ops.graph.clean(threshold=0) 
            bpy.ops.graph.select_all(action='DESELECT')

            area.type = old_type
            api.dprint("Bake should be complete", col="green")
            return {"FINISHED"}

#  $$$$$$\  $$$$$$$$\ $$\       $$$$$$$$\  $$$$$$\ $$$$$$$$\ $$$$$$\  $$$$$$\  $$\   $$\ 
# $$  __$$\ $$  _____|$$ |      $$  _____|$$  __$$\\__$$  __|\_$$  _|$$  __$$\ $$$\  $$ |
# $$ /  \__|$$ |      $$ |      $$ |      $$ /  \__|  $$ |     $$ |  $$ /  $$ |$$$$\ $$ |
# \$$$$$$\  $$$$$\    $$ |      $$$$$\    $$ |        $$ |     $$ |  $$ |  $$ |$$ $$\$$ |
#  \____$$\ $$  __|   $$ |      $$  __|   $$ |        $$ |     $$ |  $$ |  $$ |$$ \$$$$ |
# $$\   $$ |$$ |      $$ |      $$ |      $$ |  $$\   $$ |     $$ |  $$ |  $$ |$$ |\$$$ |
# \$$$$$$  |$$$$$$$$\ $$$$$$$$\ $$$$$$$$\ \$$$$$$  |  $$ |   $$$$$$\  $$$$$$  |$$ | \$$ |
#  \______/ \________|\________|\________| \______/   \__|   \______| \______/ \__|  \__|                                                                    

class ABRA_OT_select_children(bpy.types.Operator):
    bl_idname = "screen.at_select_children"
    bl_label = "Select Children"
    bl_description = "Selects the children from all selected bones. Hold SHIFT to add bones to selection instead of replace"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if bpy.context.mode == "POSE":
            selectedBones = bpy.context.selected_pose_bones
            if selectedBones:
                for bone in selectedBones:
                    api.dprint(f"Looping thru bone {str(bone.name)}")
                    armature = bone.id_data.data
                    if bpy.app.version[0] >= 4:
                        layers = bone.bone.collections # Get currently visible bone layers
                        api.dprint(str(layers))
                    else:
                        layers = armature.layers # Get currently visible bone layers
                    active_layers = []
                    i = 0
                    for layer in layers:
                        if bpy.app.version[0] >= 4:
                            if layer.is_visible == True:
                                active_layers.append(layer.name) # Make a list of bone layers in use by armature
                        else:
                            if layer == True:
                                active_layers.append(i) # Make a list of bone layers in use by armature
                            i+=i
                    api.dprint(f"Layers in use: {str(active_layers)}")
                    if not event.shift:    # Remove bone from selection if shift is not held
                        bone.bone.select = False
                    children = bone.children # Get children from iterating bone
                    if children:
                        for child in children: # Loop thru child bones and check if they are visible. If not, skip them and use next visible child
                            if api.is_bone_visible(child.bone, active_layers):
                                child.bone.select = True
                                continue
                            else:
                                c_iter = False
                                while c_iter == False:
                                    children = child.children
                                    if children:
                                        for child in children: # Loop thru child bones and check if they are visible. If not, skip them and use next visible child
                                            if api.is_bone_visible(child.bone, active_layers):
                                                child.bone.select = True
                                                c_iter = True
                                    else:
                                        break
        else:
            self.report({"INFO"}, "Currently only supports Pose Mode")
        return {"FINISHED"}

class ABRA_OT_select_siblings(bpy.types.Operator):
    bl_idname = "screen.at_select_siblings"
    bl_label = "Select Siblings"
    bl_description = "Selects all other children related to selected bones"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if bpy.context.mode == "POSE":
            selectedBones = bpy.context.selected_pose_bones
            if selectedBones:
                for bone in selectedBones:
                    parent = bone.parent
                    for child in parent.children:
                        child.bone.select = True
        else:
            self.report({"INFO"}, "Currently only supports Pose Mode")
        return {"FINISHED"}

class ABRA_OT_select_parent(bpy.types.Operator):
    bl_idname = "screen.at_select_parent"
    bl_label = "Select Parent"
    bl_description = "Selects the parent from all selected bones. Hold SHIFT to add bones to selection instead of replace"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if bpy.context.mode == "POSE":
            selectedBones = bpy.context.selected_pose_bones
            if selectedBones:
                for bone in selectedBones:
                    api.dprint(f"Looping thru bone {str(bone.name)}")
                    armature = bone.id_data.data
                    if bpy.app.version[0] >= 4:
                        layers = bone.bone.collections # Get currently visible bone layers
                        api.dprint(str(layers))
                    else:
                        layers = armature.layers # Get currently visible bone layers
                    active_layers = []
                    i = 0
                    for layer in layers:
                        if bpy.app.version[0] >= 4:
                            if layer.is_visible == True:
                                active_layers.append(layer.name) # Make a list of bone layers in use by armature
                        else:
                            if layer == True:
                                active_layers.append(i) # Make a list of bone layers in use by armature
                            i+=i
                    api.dprint(f"Layers in use: {str(active_layers)}")
                    if not event.shift:
                        bone.bone.select = False
                    parent = bone.parent
                    if parent:
                        api.dprint(f"Current parent is {parent.name}")
                        if api.is_bone_visible(parent.bone, active_layers):
                            parent.bone.select = True
                        else:  
                            p_iter = False
                            while p_iter == False:
                                parent = parent.parent
                                if parent:
                                    if api.is_bone_visible(parent.bone, active_layers):
                                        parent.bone.select = True
                                        p_iter = True
                                else:
                                    break
        else:
            self.report({"INFO"}, "Currently only supports Pose Mode")
        return {"FINISHED"}

class ABRA_OT_select_mirror(bpy.types.Operator):
    bl_idname = "screen.at_select_mirror"
    bl_label = "Select Mirror"
    bl_description = "Selects the opposite bone. For this to work, adjacent bones must have the same name with a prefix/suffix denoting their position (ex: 'LeftShoulder'/'RightShoulder', 'Pinky1_l'/'Pinky1_r', 'Clavicle.Left'/'Clavicle.Right' or 'l_arm_ik'/'r_arm_ik')"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if bpy.context.mode == "POSE":
            if event.shift:
                bpy.ops.pose.select_mirror(extend=True)
            else:
                bpy.ops.pose.select_mirror()
        else:
            self.report({"INFO"}, "Currently only supports Pose Mode")
        return {"FINISHED"}
class ABRA_OT_orient_switcher(bpy.types.Operator):
    bl_idname = "screen.at_orient_switcher"
    bl_label = "Orient Switcher"
    bl_description = "Quickly switch to your preferred orientation axes. Shift + Click this tool to change which orientations you'd like to switch from"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):

        if event.shift:
            bpy.ops.message.axispanel("INVOKE_DEFAULT")
        else:
            prefs = api.get_preferences()
            try:
                bpy.context.scene.transform_orientation_slots[0].type = "" # Hacky way to get all orientations. This should fail every time
            except Exception as e:
                ax = []
                ay = []
                s = str(e).split("in ")[1].strip("()").split(', ') # Grab available axes from error
                for t in s:
                    ax.append(t.strip("'"))

                current = context.scene.transform_orientation_slots[0].type

                # For some reason the EnumProperty value returns the the selected types out-of-order. 
                # The array needs to be sorted how they are shown in the panel, so for now we have to do it this way lol
                for a in ax:
                    if a in prefs.vis_available_axes:
                        ay.append(a)
                api.dprint(f"Ordered: {str(ay)}")

                for i, item in enumerate(ay):
                    if current == item:
                        try:
                            context.scene.transform_orientation_slots[0].type = ay[i+1]
                            break
                        except:
                            bpy.context.scene.transform_orientation_slots[0].type = ay[0]
                            break
                    else:
                        bpy.context.scene.transform_orientation_slots[0].type = ay[0]

                self.report({"INFO"}, bpy.context.scene.transform_orientation_slots[0].type)

        return {"FINISHED"}
    
class ABRA_OT_cursor_to_selected(bpy.types.Operator):
    bl_idname = "screen.at_cursor_to_selected"
    bl_label = "Cursor to Selected"
    bl_description = "Native Blender function that moves the 3D cursor to selected objects"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        area = bpy.context.area
        old_type = area.type
        area.type = 'VIEW_3D'

        bpy.ops.view3d.snap_cursor_to_selected()
        area.type = old_type
        return {"FINISHED"}

class ABRA_OT_toggle_cursor_pivot(bpy.types.Operator):
    bl_idname = "screen.at_toggle_cursor_pivot"
    bl_label = "Toggle Cursor Pivot"
    bl_description = "Quickly changes between 3D Cursor and Individual Origins pivot types"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if bpy.context.scene.tool_settings.transform_pivot_point == "CURSOR":
            bpy.context.scene.tool_settings.transform_pivot_point = "INDIVIDUAL_ORIGINS"
        else:
            bpy.context.scene.tool_settings.transform_pivot_point = "CURSOR"

        return {"FINISHED"}
    
class ABRA_OT_cursor_gizmo(bpy.types.Operator):
    bl_idname = "screen.at_cursor_gizmo"
    bl_label = "Toggle Cursor Gizmo"
    bl_description = "Toggles a gizmo that allows you to transform the 3D Cursor"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        prefs = api.get_preferences()
        pose_bypass = False
        arm_object = ""
        if bpy.context.mode == "POSE" and bpy.context.active_object.type == "ARMATURE":
            pose_bypass = True
            arm_object = context.active_object
            if "aTCursorGizmoBridge" not in bpy.context.active_object.data.bones:
                bpy.ops.object.editmode_toggle() # EDIT
                bpy.ops.armature.select_all(action='DESELECT')
                bpy.ops.armature.bone_primitive_add(name="aTCursorGizmoBridge") 
                bpy.context.active_object.data.edit_bones.active = arm_object.data.edit_bones["aTCursorGizmoBridge"]
                bpy.context.active_bone.length = 0.01
                bpy.ops.object.editmode_toggle() # OBJECT
        
        if not "aTCursorGizmo" in bpy.data.objects:
                if bpy.context.mode == "POSE":
                    bpy.ops.object.posemode_toggle() # OBJECT
                prefs.cursor_gizmo = True
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=context.scene.cursor.location, rotation=context.scene.cursor.rotation_euler, scale=(1, 1, 1))
                bpy.context.object.name = "aTCursorGizmo"
                bpy.context.object.empty_display_size = 0.01
                bpy.context.object.empty_display_type = "ARROWS"
                bpy.context.object.select_set(True)

                if pose_bypass:
                    constr = bpy.data.objects["aTCursorGizmo"].constraints.new(type='COPY_TRANSFORMS')
                    constr.target = arm_object
                    constr.subtarget = "aTCursorGizmoBridge"
                    bpy.context.view_layer.objects.active = arm_object
                    bpy.ops.object.posemode_toggle() # POSE
                    bpy.ops.pose.select_all(action='DESELECT')
                    arm_object.data.bones["aTCursorGizmoBridge"].select = True


        else:
            prefs.cursor_gizmo = False
            bpy.data.objects.remove(bpy.data.objects ['aTCursorGizmo'], do_unlink=True)
            if pose_bypass and arm_object.type == "ARMATURE":
                bpy.ops.object.editmode_toggle() # EDIT
                bpy.ops.armature.select_all(action='DESELECT')
                arm_object.data.edit_bones["aTCursorGizmoBridge"].select = True
                bpy.ops.armature.delete()
                bpy.ops.object.posemode_toggle() # POSE


                
        return {"FINISHED"}
    
@persistent
def gizmo_func(self, context):
    api.dprint("Gizmo Call")
    prefs = api.get_preferences()
    if prefs.cursor_gizmo and "aTCursorGizmo" in bpy.data.objects and "EMPTY":
        if bpy.data.objects["aTCursorGizmo"].type == "EMPTY":
            cmode = context.scene.cursor.rotation_mode
            gizmo = bpy.data.objects["aTCursorGizmo"]

            context.scene.cursor.location = gizmo.matrix_world.translation
            if cmode != "QUATERNION":
                gizmo.rotation_mode = cmode
                context.scene.cursor.rotation_euler = gizmo.matrix_world.to_euler()
            else:
                gizmo.rotation_mode = "QUATERNION"
                context.scene.cursor.rotation_quaternion = gizmo.matrix_world.to_quaternion()



class ABRA_OT_gizmo_func(bpy.types.Operator):
    bl_idname = "screen.at_gizmo_func"
    bl_label = "Cursor Gizmo (Exec)"
    bl_description = "Internal use only"
    bl_options = {"REGISTER"}

    def execute(self, context):
        gizmo_func(self, context)
        api.dprint("Cursor Gizmo Update")
        return {"FINISHED"} 

class ABRA_OT_selection_sets(bpy.types.Operator):
    bl_idname = "screen.at_selection_sets"
    bl_label = "View Selection Sets *"
    bl_description = "* 'Selection Sets' addon required. Manage and assign bones to selection sets for easier access"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        bpy.ops.message.selsetspanel("INVOKE_DEFAULT")
        return {"FINISHED"}

class ABRA_OT_swap_rig_mode(bpy.types.Operator):
    bl_idname = "screen.at_swap_rig_mode"
    bl_label = "Swap Rig Mode"
    bl_description = "Swaps between Pose/Object Mode and selects the associated armature or armature meshes. Useful when working with rig shape keys outside of Pose Mode and want to access the mesh faster, and vice versa"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if bpy.context.mode == "POSE":
            if bpy.context.active_object.type == "ARMATURE":
                armature = bpy.context.active_object

            objects = []
            if armature:
                for obj in bpy.data.objects:
                    if obj.type == 'MESH': 
                        for modifier in obj.modifiers:
                            if (modifier.type == 'ARMATURE'): 
                                if modifier.object == armature:
                                    objects.append(obj)
                                    
                if objects:
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.view_layer.objects.active = None
                    for i, o in enumerate(objects):
                        if i == 0:
                            bpy.context.view_layer.objects.active = o

                        try:
                            o.select_set(True)
                        except RuntimeError:
                            pass

                else:
                    self.report({"INFO"}, "No meshes associated with armature")
                    return {"CANCELLED"}
                    
        elif bpy.context.mode == "OBJECT":
            armature = None
            if bpy.context.active_object.type == "MESH":
                obj = bpy.context.active_object
                if obj.modifiers:
                    for modifier in obj.modifiers:
                        if modifier.type == 'ARMATURE':
                            if modifier.object:
                                armature = modifier.object
                            else:
                                self.report({"INFO"}, "Mesh has no Armature modifier")
                                return {"CANCELLED"}
                else:
                    self.report({"INFO"}, "Mesh has no Armature modifier")
                    return {"CANCELLED"}
            else:
                self.report({"INFO"}, "Select mesh with Armature modifier")
                return {"CANCELLED"}
                            
            if armature:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = armature
                bpy.ops.object.mode_set(mode='POSE')
        
        return {"FINISHED"}


#  $$$$$$\ $$$$$$$$\ $$\   $$\ $$$$$$$$\ $$$$$$$\  
# $$  __$$\\__$$  __|$$ |  $$ |$$  _____|$$  __$$\ 
# $$ /  $$ |  $$ |   $$ |  $$ |$$ |      $$ |  $$ |
# $$ |  $$ |  $$ |   $$$$$$$$ |$$$$$\    $$$$$$$  |
# $$ |  $$ |  $$ |   $$  __$$ |$$  __|   $$  __$$< 
# $$ |  $$ |  $$ |   $$ |  $$ |$$ |      $$ |  $$ |
#  $$$$$$  |  $$ |   $$ |  $$ |$$$$$$$$\ $$ |  $$ |
#  \______/   \__|   \__|  \__|\________|\__|  \__|

class ABRA_OT_tangent_keypath(bpy.types.Operator):
    bl_idname = "screen.at_key_path"
    bl_label = "Calculate Motion Path"
    bl_description = "Generates motion paths for all selected objects. Shift + Click for additional settings"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if event.shift:
            bpy.ops.message.mpathpanel("INVOKE_DEFAULT")
            return {"FINISHED"}
        else:
            if api.get_selected_bones() > 5:
                self.report({"WARNING"}, "Preventing overload: Max 5 bones")
                return {"CANCELLED"}
            opcode = None
            if bpy.context.mode == "OBJECT":
                opcode = bpy.ops.object
                opcode.paths_clear(only_selected=True)
            if bpy.context.mode == "POSE":
                opcode = bpy.ops.pose
                opcode.paths_clear(only_selected=True)

            if opcode:
                prefs = api.get_preferences()
                range = api.get_frame_range()
                currentFrame = api.get_current_frame()
                if bpy.app.version < (3, 2, 0):
                    if prefs.path_calc == "range":
                        if bpy.context.mode == "POSE":
                            opcode.paths_calculate(start_frame=range[0], end_frame=range[1], bake_location=prefs.path_loc)
                        else:
                            opcode.paths_calculate(start_frame=range[0], end_frame=range[1])
                    if prefs.path_calc == "currentEnd" and currentFrame < range[1]:
                        if bpy.context.mode == "POSE":
                            opcode.paths_calculate(start_frame=currentFrame, end_frame=range[1], bake_location=prefs.path_loc)
                        else:
                            opcode.paths_calculate(start_frame=currentFrame, end_frame=range[1])
                    if prefs.path_calc == "currentAdd":  
                        if bpy.context.mode == "POSE":
                            opcode.paths_calculate(start_frame=currentFrame, end_frame=currentFrame + prefs.path_add + 1, bake_location=prefs.path_loc)
                        else:
                            opcode.paths_calculate(start_frame=currentFrame, end_frame=currentFrame + prefs.path_add + 1)
                else:
                    active = bpy.context.active_object
                    if active:
                        if bpy.context.mode == "POSE" and active.pose:
                            bpy.ops.pose.paths_calculate(display_type=bpy.context.active_object.animation_visualization.motion_path.type, range=bpy.context.active_object.animation_visualization.motion_path.range, bake_location=prefs.path_loc)
                        elif bpy.context.mode == "OBJECT" and active:
                            bpy.ops.object.paths_calculate()

                return {"FINISHED"}
            else:
                return {"CANCELLED"}

class ABRA_OT_tangent_keypathclear(bpy.types.Operator):
    bl_idname = "screen.at_key_pathclear"
    bl_label = "Clear Paths"
    bl_description = "Removes all motion paths from scene. Shift + Click to remove paths from selected objects only"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        opcode = None
        if bpy.context.mode == "OBJECT":
            opcode = bpy.ops.object
        if bpy.context.mode == "POSE":
            opcode = bpy.ops.pose

        if opcode:
            if event.shift:
                opcode.paths_clear(only_selected=True)
            else:
                opcode.paths_clear()
        return {"FINISHED"}

class ABRA_OT_range_to_selection(bpy.types.Operator):
    bl_idname = "screen.at_range_to_selection"
    bl_label = "Frame Range to Selection"
    bl_description = "Sets the frame range to the current keyframe selection"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        area = bpy.context.area
        old_type = area.type
        area.type = 'GRAPH_EDITOR'
    
        range = api.get_range_from_selected_keys()

        if range[0] != range[1]:
            prefs = api.get_preferences()
            if prefs.use_preview_range and context.scene.use_preview_range:
                bpy.context.scene.frame_preview_start = int(range[0])
                bpy.context.scene.frame_preview_end = int(range[1])
            else:
                bpy.context.scene.frame_start = int(range[0])
                bpy.context.scene.frame_end = int(range[1])
            
        area.type = old_type
        return {"FINISHED"}
    
class ABRA_OT_range_to_markers(bpy.types.Operator):
    bl_idname = "screen.at_range_to_markers"
    bl_label = "Frame Range to Markers"
    bl_description = "Sets the frame range to the markers that are nearest to the current frame. Useful if you're working on individual camera shots in a single scene file"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        area = bpy.context.area
        old_type = area.type
        area.type = 'DOPESHEET_EDITOR'

        current_frame = context.scene.frame_current
        markers = context.scene.timeline_markers
        frame_range = [0,1048574] # Frame range can never be less than zero
        marker_check = [False, False]

        if markers:
            for marker in markers:
                if marker.frame >= current_frame: # Marker is to the right of playhead
                    if marker.frame < frame_range[1]: 
                        frame_range[1] = marker.frame
                        marker_check[1] = True
                elif marker.frame <= current_frame: # Marker is to the left of playhead
                    if marker.frame > frame_range[0]: 
                        frame_range[0] = marker.frame
                        marker_check[0] = True

            # Check if markers were ever to the left or right of playhead. In either case, set frame range to itself instead.
            if not marker_check[1]:
                frame_range[1] = current_frame
            if not marker_check[0]:
                frame_range[0] = current_frame
                
            prefs = api.get_preferences()
            if prefs.use_preview_range and context.scene.use_preview_range:
                context.scene.frame_preview_start = frame_range[0]
                context.scene.frame_preview_end = frame_range[1] - 1
            else:
                context.scene.frame_start = frame_range[0]
                context.scene.frame_end = frame_range[1] - 1
            
        area.type = old_type
        return {"FINISHED"}


#  /$$$$$$$$ /$$$$$$  /$$   /$$  /$$$$$$  /$$$$$$$$ /$$   /$$ /$$$$$$$$ /$$$$$$ 
# |__  $$__//$$__  $$| $$$ | $$ /$$__  $$| $$_____/| $$$ | $$|__  $$__//$$__  $$
#    | $$  | $$  \ $$| $$$$| $$| $$  \__/| $$      | $$$$| $$   | $$  | $$  \__/
#    | $$  | $$$$$$$$| $$ $$ $$| $$ /$$$$| $$$$$   | $$ $$ $$   | $$  |  $$$$$$ 
#    | $$  | $$__  $$| $$  $$$$| $$|_  $$| $$__/   | $$  $$$$   | $$   \____  $$
#    | $$  | $$  | $$| $$\  $$$| $$  \ $$| $$      | $$\  $$$   | $$   /$$  \ $$
#    | $$  | $$  | $$| $$ \  $$|  $$$$$$/| $$$$$$$$| $$ \  $$   | $$  |  $$$$$$/
#    |__/  |__/  |__/|__/  \__/ \______/ |________/|__/  \__/   |__/   \______/                                                                    

class ABRA_OT_tangent_free(bpy.types.Operator):
    bl_idname = "screen.at_tangent_free"
    bl_label = "Set Free Tangent"
    bl_description = "Simple operator to set all selected keys to Free"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        api.set_tangent("FREE")
        return {"FINISHED"}

class ABRA_OT_tangent_aligned(bpy.types.Operator):
    bl_idname = "screen.at_tangent_aligned"
    bl_label = "Set Aligned Tangent"
    bl_description = "Simple operator to set all selected keys to Aligned"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        api.set_tangent("ALIGNED")
        return {"FINISHED"}

class ABRA_OT_tangent_vector(bpy.types.Operator):
    bl_idname = "screen.at_tangent_vector"
    bl_label = "Set Vector Tangent"
    bl_description = "Simple operator to set all selected keys to Vector"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        api.set_tangent("VECTOR")
        return {"FINISHED"}

class ABRA_OT_tangent_auto(bpy.types.Operator):
    bl_idname = "screen.at_tangent_auto"
    bl_label = "Set Automatic Tangent"
    bl_description = "Simple operator to set all selected keys to Automatic"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        api.set_tangent("AUTO")
        return {"FINISHED"}

class ABRA_OT_tangent_autoclamp(bpy.types.Operator):
    bl_idname = "screen.at_tangent_autoclamp"
    bl_label = "Set Auto Clamped Tangent"
    bl_description = "Simple operator to set all selected keys to Auto-Clamped"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        api.set_tangent("AUTO_CLAMPED")
        return {"FINISHED"}
        
############################################

cls = (ABRA_OT_key_selected,
ABRA_OT_key_visible,
ABRA_OT_key_copy,
ABRA_OT_key_paste,
ABRA_OT_key_copy_pose,
ABRA_OT_key_paste_pose,
ABRA_OT_key_delete,
ABRA_OT_share_active_key_timing,
ABRA_OT_share_common_key_timing,
ABRA_OT_key_shapekeys,
ABRA_OT_key_armature,
ABRA_OT_key_retime,
ABRA_OT_bake_keys,
ABRA_OT_select_children,
ABRA_OT_select_siblings,
ABRA_OT_select_parent,
ABRA_OT_select_mirror,
ABRA_OT_selection_sets,
ABRA_OT_swap_rig_mode,
ABRA_OT_orient_switcher,
ABRA_OT_cursor_to_selected,
ABRA_OT_cursor_gizmo,
ABRA_OT_toggle_cursor_pivot,
ABRA_OT_tangent_keypath,
ABRA_OT_tangent_keypathclear,
ABRA_OT_range_to_selection,
ABRA_OT_range_to_markers,
ABRA_OT_tangent_free,
ABRA_OT_tangent_aligned,
ABRA_OT_tangent_vector,
ABRA_OT_tangent_auto,
ABRA_OT_tangent_autoclamp)