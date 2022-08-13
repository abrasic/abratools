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
    bl_description = "* 'Copy Timing and Ease' addon required. Select two bones, where the active bone will share the key timing of the other"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if api.is_addon_enabled("Copy_Timing_and_Ease"):
            bones = bpy.context.selected_pose_bones
            if len(bones) == 2:
                area = bpy.context.area
                old_type = area.type
                area.type = 'GRAPH_EDITOR'
                obj = bpy.context.object
                action = obj.animation_data.action

                for bone in bones:
                    if bone != bpy.context.active_pose_bone:
                        boneAction = action.groups.get(bone.name)
                        for i in boneAction.channels:
                            i.select = True
                            for x in i.keyframe_points:
                                if x.co[0] > bpy.context.scene.frame_start and x.co[0] < bpy.context.scene.frame_end:
                                    x.select_control_point=True
                                else:
                                    x.select_control_point=False
                                
                        bpy.ops.graph.copy_timing_and_ease()
                        bpy.ops.graph.select_all(action='DESELECT')
                        bpy.context.active_object.data.bones[bone.name].select = False
                        
                for bone in bones:
                    if bone == bpy.context.active_pose_bone:
                        print("active bone to apply")
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
                    if not event.shift:    # Remove bone from selection if shift is not held
                        bone.bone.select = False
                    children = bone.children
                    if children:
                        for child in children:
                            child.bone.select = True
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
                    if not event.shift:    # Remove bone from selection if shift is not held
                        bone.bone.select = False
                    if bone.parent:
                            bone.parent.bone.select = True
        else:
            self.report({"INFO"}, "Currently only supports Pose Mode")
        return {"FINISHED"}

class ABRA_OT_select_mirror(bpy.types.Operator):
    bl_idname = "screen.at_select_mirror"
    bl_label = "Select Mirror"
    bl_description = "Selects the opposite bone, if applicable. For this to work, adjacent bones must have the same name with a prefix/suffix denoting their position (some examples of detectable bones include: 'LeftShoulder'/'RightShoulder', 'Pinky1_l'/'Pinky1_r', 'Clavicle.Left'/'Clavicle.Right' or 'l_arm_ik'/'r_arm_ik')"
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
    
        curves = api.get_selected_fcurves()
        if curves:
            minimum = None
            maximum = None
            for curve in curves:
                keys = api.get_selected_keys(curve)
                if keys:
                    firstKey = api.get_key_coords(curve, keys[0])[0]
                    lastKey = api.get_key_coords(curve, keys[-1])[0]
                    if not minimum or firstKey < minimum:
                        minimum = firstKey
                    if not maximum or lastKey > maximum:
                        maximum = lastKey
                        
            if minimum > maximum:
                omax = minimum
                minimum = maximum
                maximum = omax

            if minimum != maximum:
                bpy.context.scene.frame_start = int(minimum)
                bpy.context.scene.frame_end = int(maximum)
        else:
            area.type = old_type
            return {"CANCELLED"}
            
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
ABRA_OT_select_children,
ABRA_OT_select_siblings,
ABRA_OT_select_parent,
ABRA_OT_select_mirror,
ABRA_OT_cursor_to_selected,
ABRA_OT_toggle_cursor_pivot,
ABRA_OT_tangent_keypath,
ABRA_OT_tangent_keypathclear,
ABRA_OT_range_to_selection,
ABRA_OT_tangent_free,
ABRA_OT_tangent_aligned,
ABRA_OT_tangent_vector,
ABRA_OT_tangent_auto,
ABRA_OT_tangent_autoclamp)