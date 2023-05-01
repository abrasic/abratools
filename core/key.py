import bpy
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

class ABRA_OT_key_delete(bpy.types.Operator):
    bl_idname = "screen.at_delete_keys"
    bl_label = "Delete Keys"
    bl_description = "Deletes selected keys. If nothing is selected, keys from the playhead will be deleted instead"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        api.key_clipboard(self, type="delete")
        return {"FINISHED"}

class ABRA_OT_key_timing(bpy.types.Operator):
    bl_idname = "screen.at_copy_key_timing"
    bl_label = "Copy Key Timing *"
    bl_description = "* 'Animcopy' addon required. Select two bones, where the active bone will share the key timing of the other"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if api.is_addon_enabled("AnimCopy") and bpy.context.mode == "POSE":
            api.dprint("Addon detected", col="green")
            bones = bpy.context.selected_pose_bones
            api.dprint("Selected bones: "+str(len(bones)))
            if len(bones) == 2:
                api.dprint("Two bones selected. Starting copier...", col="green")
                area = context.area
                old_type = area.type
                area.type = 'GRAPH_EDITOR'
                obj = context.object
                action = obj.animation_data.action
                bpy.ops.graph.select_all(action='DESELECT')

                # Copy Timing from non-active object
                api.dprint("Copying timing from non-active")
                frameKeys = []
                for bone in bones:
                    if bone != context.active_pose_bone:
                        api.dprint("Copying frames from bone: "+str(bone.name))
                        boneAction = action.groups.get(bone.name)
                        for i in boneAction.channels:
                            api.dprint("=== ITERATING CHANNEL: "+i.data_path)
                            i.select = True
                            for x in i.keyframe_points:
                                if x.co[0] > context.scene.frame_start and x.co[0] < context.scene.frame_end:
                                    x.select_control_point=True
                                    if x.co[0] not in frameKeys:
                                        frameKeys.append(x.co[0])
                                else:
                                    x.select_control_point=False
                        api.dprint("FINAL FRAMES TO COPY:", col="blue")
                        api.dprint(str(frameKeys), col="blue")

                        bpy.ops.graph.copy_timing_and_ease()
                        bpy.ops.graph.select_all(action='DESELECT')
                        context.active_object.data.bones[bone.name].select = False

                # Paste timing from active object
                for bone in bones:
                    if bone == context.active_pose_bone:
                        boneAction = action.groups.get(bone.name)
                        for i in boneAction.channels:
                            i.select = True
                            bpy.ops.graph.paste_timing()
                
                area.type = old_type
            else:
                self.report({"INFO"}, "Select exactly two bones")
        else:
            self.report({"INFO"}, "Required addon is not installed")
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
        prefs = bpy.context.preferences.addons["abTools"].preferences
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
            prefs = bpy.context.preferences.addons["abTools"].preferences
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
            bpy.ops.nla.bake(frame_start=range[0], frame_end=range[1], bake_types={bpy.context.mode}, use_current_action = True)
            bpy.ops.graph.select_all(action='DESELECT')

            api.dprint("Initial bake complete. Moving to range start")
            bpy.context.scene.frame_current = range[0]
            ref = bpy.context.scene.frame_current
            while bpy.context.scene.frame_current < range[1]:
                s = 0
                bpy.ops.screen.keyframe_jump()
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

            bpy.context.scene.frame_current = frame_const
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
                    armature = bone.id_data.data
                    layers = armature.layers # Get currently visible bone layers
                    active_layers = []
                    i = 0
                    for layer in layers:
                        if layer == True:
                            active_layers.append(i) # Make a list of bone layers in use by armature
                        i+=i
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
                                            print(child)
                                            if api.is_bone_visible(child.bone, active_layers):
                                                print("child bone is finally visible. show this one")
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
                    armature = bone.id_data.data
                    layers = armature.layers # Get currently visible bone layers
                    active_layers = []
                    i = 0
                    for layer in layers:
                        if layer == True:
                            active_layers.append(i) # Make a list of bone layers in use by armature
                        i+=i
                    if not event.shift:
                        bone.bone.select = False
                    parent = bone.parent
                    if parent:
                        if api.is_bone_visible(parent.bone, active_layers):
                            parent.bone.select = True
                        else:  
                            p_iter = False
                            while p_iter == False:
                                parent = parent.parent
                                print(parent)
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

                        o.select_set(True)
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
                prefs = bpy.context.preferences.addons["abTools"].preferences
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
ABRA_OT_key_delete,
ABRA_OT_key_timing,
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
ABRA_OT_cursor_to_selected,
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