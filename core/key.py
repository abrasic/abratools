import blf, bpy, re, time
import numpy as np
from bpy.app.handlers import persistent
from . import api
gop = None
go_text = None
ak_choice = False

# $$\   $$\ $$$$$$$$\ $$\     $$\ $$$$$$\ $$\   $$\  $$$$$$\  
# $$ | $$  |$$  _____|\$$\   $$  |\_$$  _|$$$\  $$ |$$  __$$\ 
# $$ |$$  / $$ |       \$$\ $$  /   $$ |  $$$$\ $$ |$$ /  \__|
# $$$$$  /  $$$$$\      \$$$$  /    $$ |  $$ $$\$$ |$$ |$$$$\ 
# $$  $$<   $$  __|      \$$  /     $$ |  $$ \$$$$ |$$ |\_$$ |
# $$ |\$$\  $$ |          $$ |      $$ |  $$ |\$$$ |$$ |  $$ |
# $$ | \$$\ $$$$$$$$\     $$ |    $$$$$$\ $$ | \$$ |\$$$$$$  |
# \__|  \__|\________|    \__|    \______|\__|  \__| \______/ 

class ABRA_OT_nudge_left(bpy.types.Operator):
    bl_idname = "screen.at_nudge_left"
    bl_label = "Nudge Left"
    bl_description = "Moves/nudges selected keyframes to the left based on Nudge Interval value"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'
        area.spaces[0].dopesheet.show_only_selected = api.use_oss()[0]

        prefs = api.get_preferences()
        fcurves = api.get_standard_curves()

        #F-Curves are not selected when keys are selected in Dope Sheet
        for curve in fcurves:
            curve.select = True

        key_editable = bpy.context.selected_editable_keyframes

        if len(key_editable):
            api.dprint("Keys are selected. Only move what is selected.")
            cfra = context.scene.frame_current
            near = -2**30
            far = 2**30
            for k in key_editable:
                if k.co[0] > near:
                    near = k.co[0]
                if k.co[0] < far:
                    far = k.co[0]

            bpy.ops.transform.translate(value=(-(prefs.nudge_interval), 0, 0))
            if (far - prefs.nudge_interval) <= cfra and (near + prefs.nudge_interval) >= cfra:
                context.scene.frame_current -= prefs.nudge_interval
        else:
            api.dprint("No keys are selected. Check for keys on playhead.")
            try:
                bpy.ops.graph.select_column(mode='CFRA')
            except RuntimeError:
                area.type = old
                return {"CANCELLED"}
            key_editable = bpy.context.selected_editable_keyframes

            if len(key_editable):
            # If keys are on playhead, move only the keys on the playhead and move current frame.
                bpy.ops.transform.translate(value=(-(prefs.nudge_interval), 0, 0))
                context.scene.frame_current -= prefs.nudge_interval
                bpy.ops.graph.select_all(action='DESELECT')
            else:
                api.dprint("No keys selected or on playhead.")
                cfra = context.scene.frame_current
                key_selection = []
                closest = 2**30
                for curve in fcurves:
                    api.dprint(f"---- {curve.data_path} ----")
                    kfp = list(curve.keyframe_points)
                    kfp.reverse()
                    for k in kfp:
                        distance = k.co[0] - cfra
                        if k.co[0] <= context.scene.frame_current:
                            api.dprint(f"Key exceeds playhead {k.co[0]}. Breaking")
                            break
                        if (distance < closest):
                            closest = distance
                            api.dprint(f"NEW CLOSEST FRAME: {closest}", col="red")

                api.dprint(f"Closest distance appears to be {closest}", col="orange")

                bpy.ops.graph.select_all(action='DESELECT')
                if closest != 2**30:
                    for curve in fcurves:
                        try:
                            frame_target = int(closest+cfra)
                            key_index = api.get_key_index_at_frame(curve,frame_target)
                            if curve.keyframe_points[key_index].co[0] == frame_target:
                                curve.keyframe_points[key_index].select_control_point = True
                        except IndexError:
                            continue

                    bpy.ops.transform.translate(value=(-int(closest), 0, 0))
                    bpy.ops.graph.select_all(action='DESELECT')

        area.type = old
        return {"FINISHED"}
    
class ABRA_OT_nudge_right(bpy.types.Operator):
    bl_idname = "screen.at_nudge_right"
    bl_label = "Nudge Right"
    bl_description = "Moves/nudges selected keyframes to the right based on Nudge Interval value"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'
        area.spaces[0].dopesheet.show_only_selected = api.use_oss()[0]

        prefs = api.get_preferences()
        fcurves = api.get_standard_curves()

        #F-Curves are not selected when keys are selected in Dope Sheet
        for curve in fcurves:
            curve.select = True

        key_editable = bpy.context.selected_editable_keyframes

        if len(key_editable):
            api.dprint("Keys are selected. Only move what is selected.")
            cfra = context.scene.frame_current
            near = -2**30
            far = 2**30
            for k in key_editable:
                if k.co[0] > near:
                    near = k.co[0]
                if k.co[0] < far:
                    far = k.co[0]

            bpy.ops.transform.translate(value=((prefs.nudge_interval), 0, 0))
            if (far - prefs.nudge_interval) <= cfra and (near + prefs.nudge_interval) >= cfra:
                context.scene.frame_current += prefs.nudge_interval
        else:
            api.dprint("No keys are selected. Check for keys on playhead.")
            try:
                bpy.ops.graph.select_column(mode='CFRA')
            except RuntimeError:
                area.type = old
                return {"CANCELLED"}
            key_editable = bpy.context.selected_editable_keyframes

            if len(key_editable):
            # If keys are on playhead, move only the keys on the playhead and move current frame.
                bpy.ops.transform.translate(value=((prefs.nudge_interval), 0, 0))
                context.scene.frame_current += prefs.nudge_interval
                bpy.ops.graph.select_all(action='DESELECT')
            else:
                api.dprint("No keys selected or on playhead.")
                cfra = context.scene.frame_current
                key_selection = []
                closest = 2**30
                for curve in fcurves:
                    api.dprint(f"---- {curve.data_path} ----")
                    for k in curve.keyframe_points:
                        distance = cfra - k.co[0]
                        if k.co[0] >= context.scene.frame_current:
                            api.dprint(f"Key exceeds playhead {k.co[0]}. Breaking")
                            break
                        if (distance < closest):
                            closest = distance
                            api.dprint(f"NEW CLOSEST FRAME: {closest}", col="red")

                api.dprint(f"Closest distance appears to be {closest}", col="orange")

                bpy.ops.graph.select_all(action='DESELECT')
                if closest != 2**30:
                    for curve in fcurves:
                        try:
                            frame_target = int(cfra-closest)
                            key_index = api.get_key_index_at_frame(curve,frame_target)
                            if curve.keyframe_points[key_index].co[0] == frame_target:
                                curve.keyframe_points[key_index].select_control_point = True
                        except IndexError:
                            continue

                    bpy.ops.transform.translate(value=(int(closest), 0, 0))
                    bpy.ops.graph.select_all(action='DESELECT')

        area.type = old
        return {"FINISHED"}

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
            self.report({"INFO"}, "This tool only works in Pose Mode")
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
            self.report({"INFO"}, "This tool only works in Pose Mode")
            return {"CANCELLED"}

class ABRA_OT_key_delete(bpy.types.Operator):
    bl_idname = "screen.at_delete_keys"
    bl_label = "Delete Keys"
    bl_description = "Deletes selected keys. If nothing is selected, keys from the playhead will be deleted instead"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        api.key_clipboard(self, type="delete")
        return {"FINISHED"}
class clipboard(bpy.types.PropertyGroup):
    timing: bpy.props.FloatProperty(name="Timing")
class ABRA_OT_copy_timing(bpy.types.Operator):
    bl_idname = "screen.at_copy_timing"
    bl_label = "Copy Timing"
    bl_description = "Copies the timing/frames in which selected keys are placed on. If no selection is used, all keys within the frame range is used instead"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        prefs = api.get_preferences()
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        range = api.get_frame_range()
        area.spaces[0].dopesheet.show_only_selected = api.use_oss()[0]

        curves = api.get_selected_fcurves()
        if not len(curves):
            api.dprint("No curves are selected. Getting visible ones instead...")
            curves = api.get_visible_fcurves()

        timings = []

        if not curves:
            area.type = old
            return {"CANCELLED"}
        
        keys_selected = api.are_keys_selected(curves)

        bpy.context.scene.at_time_clipboard.clear()
        if not api.fcurve_overload(curves):
            for curve in curves:
                for key in curve.keyframe_points:
                    co = key.co.x
                    if keys_selected:
                        api.dprint("Keys are selected. Limiting selection to those...")
                        if co not in timings and co >= range[0] and co <= range[1] and key.select_control_point:
                            timings.append(co)
                    else:
                        api.dprint("Keys are not selected")
                        if co not in timings and co >= range[0] and co <= range[1]:
                            timings.append(co)

            for t in timings:
                key = bpy.context.scene.at_time_clipboard.add()
                key.timing = t

            for a in bpy.context.scene.at_time_clipboard:
                api.dprint(str(a.timing))
        else:
            area.type = old
            self.report({"ERROR"}, f"Preventing overload ({prefs.fcurve_scan_limit} FCurves max, {len(curves)} active)")
            return {"CANCELLED"}
        
        area.type = old

        return{"FINISHED"}
    
class ABRA_OT_paste_timing(bpy.types.Operator):
    bl_idname = "screen.at_paste_timing"
    bl_label = "Paste Timing"
    bl_description = "On selected F-Curves, inserts keyframes on frames from Copy Timing clipboard. If no F-Curves are selected, it will scan thru all visible F-Curves instead"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        prefs = api.get_preferences()
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        range = api.get_frame_range()

        if len(context.scene.at_time_clipboard):
            area.spaces[0].dopesheet.show_only_selected = api.use_oss()[0]

            curves = api.get_selected_fcurves()
            if not len(curves):
                api.dprint("No curves are selected. Getting visible ones instead...")
                curves = api.get_visible_fcurves()

            if not curves:
                area.type = old
                return {"CANCELLED"}

            if not api.fcurve_overload(curves):
                for curve in curves:
                    for i in context.scene.at_time_clipboard:
                        if i.timing >= range[0] and i.timing <= range[1]:
                            curve.keyframe_points.insert(frame=i.timing, value = curve.evaluate(i.timing))
            else:
                area.type = old
                self.report({"ERROR"}, f"Preventing overload ({prefs.fcurve_scan_limit} FCurves max, {len(curves)} active)")
                return {"CANCELLED"}
            
            area.type = old

            return{"FINISHED"}
        else:
            area.type = old
            self.report({"WARNING"}, "No data in clipboard")
            return{"CANCELLED"}
        
class rot_scores(bpy.types.PropertyGroup):
    scores: bpy.props.StringProperty(default="{}")
    scores_max: bpy.props.StringProperty(default="{}")
    range_min: bpy.props.IntProperty(default=0)
    range_max: bpy.props.IntProperty(default=0)
    current: bpy.props.StringProperty(default="XYZ")

class ABRA_OT_switch_rotation(bpy.types.Operator):
    bl_idname = "screen.at_switch_rotation"
    bl_label = "Switch Rotation"
    bl_description = "Switches rotation order and bakes new order from matrix, preserving relative animation and avoiding gimbal lock"
    bl_options = {"REGISTER", "UNDO"}

    order: bpy.props.StringProperty(
        name="order",
        default = "XYZ"
    )

    def execute(self, context):
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        prefs = api.get_preferences()
        obj = bpy.context.active_object
        fcurves = []
        bone = ""

        if bpy.context.mode == "POSE": #If in pose mode, grab active pose bone
            api.dprint("Collecting Pose Bone Euler curves...")
            bone = bpy.context.active_pose_bone
            if obj and bone:
                bone.keyframe_insert(data_path="rotation_euler", frame=1234567) # Temporary
                all_fcurves = obj.animation_data.action.fcurves
                if not api.fcurve_overload(all_fcurves):
                    for f in all_fcurves:
                        try:
                            if f.data_path.split('"')[1] in bone.name:
                                if f.data_path.split('.')[-1] == 'rotation_euler':
                                    fcurves.append(f)        
                        except IndexError:
                            continue
                else:
                    area.type = old
                    self.report({"ERROR"}, f"Preventing overload ({prefs.fcurve_scan_limit} FCurves max, {len(all_fcurves)} active)")
                    return {"CANCELLED"}
            else:
                self.report("WARNING", "There is no active bone in the scene")
                return {"CANCELLED"}
        elif bpy.context.mode == "OBJECT": #Other
            api.dprint("Collecting Object Euler curves...")
            obj.keyframe_insert(data_path="rotation_euler", frame=1234567) # Temporary
            all_fcurves = obj.animation_data.action.fcurves
            if not api.fcurve_overload(all_fcurves):
                for f in all_fcurves:
                    if f.data_path == 'rotation_euler':
                        fcurves.append(f)
            else:
                area.type = old
                self.report({"ERROR"}, f"Preventing overload ({prefs.fcurve_scan_limit} FCurves max, {len(all_fcurves)} active)")
                return {"CANCELLED"}
                
        else:
            self.report("WARNING", "Only Object and Pose mode are supported")
            return {"CANCELLED"}


        current_mode = obj.rotation_mode
        frame_targets = []

        # Get all frames that contain keys on euler curves
        for curve in fcurves:
            if rot_scores.range_min == rot_scores.range_max:
                frame_targets.append(rot_scores.range_min)   
            else:
                for keyf in curve.keyframe_points:
                    if keyf.co_ui.x not in frame_targets and keyf.co_ui.x >= rot_scores.range_min and keyf.co_ui.x <= rot_scores.range_max:
                        frame_targets.append(keyf.co_ui.x)    
        
        frame_targets.sort()

        for frame in frame_targets:
            for curve in fcurves:
                curve.keyframe_points.insert(frame, curve.evaluate(frame), options={"NEEDED", "FAST"})
        
        bpy.context.view_layer.update()
        old_frame = bpy.context.scene.frame_current
        for frame in frame_targets:
            bpy.context.scene.frame_current = int(frame)
            bpy.context.view_layer.update()

            if bpy.context.mode == "POSE":
                global_matrix = obj.pose.bones[bone.name].matrix_basis.to_euler(self.order)
            else:
                global_matrix = obj.matrix_basis.to_euler(self.order)
            
            for curve in fcurves:
                curve.keyframe_points.insert(frame, global_matrix[curve.array_index], options={"REPLACE"})

        if bpy.context.mode == "POSE":
            obj.pose.bones[bone.name].rotation_mode = self.order
            for curve in all_fcurves:
                if curve.data_path.split('.')[-1] == 'rotation_mode':
                    for f in frame_targets:
                        obj.pose.bones[bone.name].keyframe_delete(data_path="rotation_mode", frame=f)
                    obj.pose.bones[bone.name].keyframe_insert(data_path="rotation_mode", frame=frame_targets[0])
        else:
            obj.rotation_mode = self.order
            for curve in all_fcurves:
                if curve.data_path == 'rotation_mode':
                    for f in frame_targets:
                        obj.keyframe_delete(data_path="rotation_mode", frame=f)
                    obj.keyframe_insert(data_path="rotation_mode", frame=frame_targets[0])
                

        if bpy.context.mode == "POSE":
            bone.keyframe_delete(data_path="rotation_euler", frame=1234567)
        else:
            obj.keyframe_delete(data_path="rotation_euler", frame=1234567)

        bpy.context.scene.frame_current = old_frame
                
        area.type = old
        return {'FINISHED'}
class ABRA_OT_rotation_switcher(bpy.types.Operator):
    bl_idname = "screen.at_rotation_switcher"
    bl_label = "Rotation Switcher"
    bl_description = "Bake out/switch selected keys into a new rotation order. Also determines best rotation-order for selected range"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        area = bpy.context.area
        old = area.type
        area.type = 'GRAPH_EDITOR'

        import math
        prefs = api.get_preferences()
        score_dict = {}
        score_dict_max = {}
        frame_targets = []
        fcurves = []
        bone = ""
        global_matrix = {}
        modes = ["XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX"]
        gimbals = [1,2,0,2,0,1]
        mode_index = 0
        order = list(modes[0])
        obj = bpy.context.active_object

        if obj:
            if bpy.context.mode == "POSE": #If in pose mode, grab active pose bone
                api.dprint("Collecting Pose Bone Euler curves...")
                bone = bpy.context.active_pose_bone
                if obj and bone:
                    bone.keyframe_insert(data_path="rotation_euler", frame=1234567) # Temporary
                    all_fcurves = obj.animation_data.action.fcurves
                    if not api.fcurve_overload(all_fcurves):
                        for f in all_fcurves:
                            try:
                                if f.data_path.split('"')[1] in bone.name:
                                    if f.data_path.split('.')[-1] == 'rotation_euler':
                                        f.keyframe_points[-1].select_control_point = False
                                        fcurves.append(f)        
                            except IndexError:
                                continue
                    else:
                        area.type = old
                        self.report({"ERROR"}, f"Preventing overload ({prefs.fcurve_scan_limit} FCurves max, {len(all_fcurves)} active)")
                        return {"CANCELLED"}
                else:
                    self.report({"WARNING"}, "There is no active bone in the scene")
                    area.type = old
                    return {"CANCELLED"}
            elif bpy.context.mode == "OBJECT": #Other
                api.dprint("Collecting Object Euler curves...")
                obj.keyframe_insert(data_path="rotation_euler", frame=1234567) # Temporary
                all_fcurves = obj.animation_data.action.fcurves
                if not api.fcurve_overload(all_fcurves):
                    for f in all_fcurves:
                        if f.data_path == 'rotation_euler':
                            f.keyframe_points[-1].select_control_point = False
                            fcurves.append(f)
                else:
                    area.type = old
                    self.report({"ERROR"}, f"Preventing overload ({prefs.fcurve_scan_limit} FCurves max, {len(all_fcurves)} active)")
                    return {"CANCELLED"}
            else:
                self.report({"WARNING"}, "Only Object and Pose mode are supported")
                area.type = old
                return {"CANCELLED"}
        else:
            self.report({"WARNING"}, "There is no active object in the scene")
            area.type = old
            return {"CANCELLED"}

        api.dprint(fcurves, col="blue")

        #F-Curves are not selected when keys are selected in Dope Sheet (Also only select euler curves)
        for curve in all_fcurves:
            curve.select = False
        for curve in fcurves:
            curve.select = True

        # Get range from current selection
        api.dprint("Determining selection method...")
        range = api.get_range_from_selected_keys()
        api.dprint(range)
        if not range:
            api.dprint("No visible selection, using current frame only")
            range = [bpy.context.scene.frame_current, bpy.context.scene.frame_current]

        api.dprint(fcurves)

        rot_scores.range_min = range[0]
        rot_scores.range_max = range[1]

        if bpy.context.mode == "POSE":
            rot_scores.current = bone.rotation_mode
        else:
            rot_scores.current = obj.rotation_mode

        api.dprint("The working range for this execution is "+str(range))

        for i, m in enumerate(modes):
            if m == obj.rotation_mode:
                mode_index = gimbals[i]
                api.dprint("The gimbal index for rotation mode is "+ str(mode_index))
                break

        old_frame = bpy.context.scene.frame_current
        for curve in fcurves:
            if curve.array_index == mode_index:

                if rot_scores.range_min == rot_scores.range_max:
                    api.dprint("No keys are selected for range, using current frame only")
                    if rot_scores.range_min == None:
                        self.report({"WARNING"}, "Select one object or bone")
                        area.type = old
                        return {"CANCELLED"}
                    api.dprint(int(rot_scores.range_min))
                    bpy.context.scene.frame_current = int(rot_scores.range_min)
                    bpy.context.view_layer.update()

                    for i, mode in enumerate(modes):
                        gimbal_culprit = [*mode][1]
                        
                        order_i=0
                        for o in order:
                            if any(item in order[order_i] for item in gimbal_culprit):
                                break
                            order_i+=1

                        if bpy.context.mode == "POSE":
                            global_matrix = bone.matrix_basis.to_euler(mode)
                        else:
                            global_matrix = obj.matrix_basis.to_euler(mode)

                        key_rot = math.degrees(global_matrix[order_i])
                        api.dprint("Scoring: "+str(mode)+" (" + str(global_matrix[order_i])+")")
                        score = abs((key_rot + 90) % 180 - 90) / 90
                        api.dprint(str(mode) + " SCORE IS "+str(score), col="yellow")
                        score_dict[mode] = score
                else:
                    score_data = {}
                    for key in curve.keyframe_points:
                        if key.co_ui.x >= range[0] and key.co_ui.x <= range[1]:
                            bpy.context.scene.frame_current = int(key.co_ui.x)-1
                            bpy.context.view_layer.update()
                            api.dprint("FRAME "+ str(bpy.context.scene.frame_current))

                            for i, mode in enumerate(modes):
                                gimbal_culprit = [*mode][1]
                                
                                order_i=0
                                for o in order:
                                    if any(item in order[order_i] for item in gimbal_culprit):
                                        break
                                    order_i+=1


                                if bpy.context.mode == "POSE":
                                    global_matrix = bone.matrix_basis.to_euler(mode)
                                else:
                                    global_matrix = obj.matrix_basis.to_euler(mode)

                                key_rot = math.degrees(global_matrix[order_i])
                                api.dprint("Scoring: "+str(mode)+" (" + str(global_matrix[order_i])+")")
                                score = abs((key_rot + 90) % 180 - 90) / 90
                                api.dprint(str(mode) + " SCORE IS "+str(score), col="yellow")

                                if mode not in score_data.keys():
                                    score_data[mode] = [score]
                                else:
                                    score_data[mode].append(score)
                        
                    api.dprint("-------------- FINAL SCORES --------------")
                    for scores in score_data:
                        avg_score = sum(score_data[scores]) / len(score_data[scores])
                        score_max = max(score_data[scores])
                        api.dprint(str(scores) + " AVERAGE: "+str(avg_score), col="yellow")
                        api.dprint(str(scores) + " MAX: "+str(score_max), col="yellow")
                        score_dict[scores] = avg_score
                        score_dict_max[scores] = score_max

            if bpy.context.mode == "POSE":
                try:
                    bone.keyframe_delete(data_path="rotation_euler", frame=1234567)
                except RuntimeError:
                    pass
            else:
                try:
                    obj.keyframe_delete(data_path="rotation_euler", frame=1234567)
                except RuntimeError:
                    pass

                                                
        bpy.context.scene.frame_current = old_frame
        api.dprint("DONE", col="green")

        area.type = old

        if not score_dict:
            self.report({"WARNING"}, "Invalid selection. Does the object have Euler F-Curves?")
            area.type = old
            return {"CANCELLED"}

        rot_scores.scores = str(score_dict).replace("'",'"')
        rot_scores.scores_max = str(score_dict_max).replace("'",'"')
        bpy.ops.message.rotationpanel("INVOKE_DEFAULT")

        return {"FINISHED"}

class ABRA_OT_global_offset(bpy.types.Operator):
    bl_idname = "screen.at_global_offset"
    bl_label = "Global Offset"
    bl_description = "While enabled, changes you make to the transforms of the current frame will be applied to all others keys. Shift + Click this tool for additional settings"
    bl_options = {"REGISTER"}

    def invoke(self, context, event):
        if event.shift:
            bpy.ops.message.offsetpanel("INVOKE_DEFAULT")
            return {"FINISHED"}
        else:
            global ak_choice
            prefs = api.get_preferences()
            prefs.global_offset = not prefs.global_offset

            if prefs.global_offset:
                bpy.app.handlers.depsgraph_update_post.append(global_offset_func)
                ak_choice = bpy.context.scene.tool_settings.use_keyframe_insert_auto
                if ak_choice:
                    bpy.context.scene.tool_settings.use_keyframe_insert_auto = False
                    self.report({"INFO"}, "Auto-Key disabled while Global Offset is in use")
            
            if not prefs.global_offset:
                bpy.app.handlers.depsgraph_update_post.remove(global_offset_func)
                bpy.context.scene.tool_settings.use_keyframe_insert_auto = ak_choice

            api.write_text("Global Offset ON") if prefs.global_offset else api.remove_text()
            context.area.tag_redraw()
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            
        return {"FINISHED"}

@persistent
def global_offset_func(self, context):
    global gop
    eop = bpy.context.active_operator

    prefs = api.get_preferences()
    if prefs.global_offset:
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = False

        if eop is gop and prefs.offset_live_feedback == False:
            return
        gop = bpy.context.active_operator
        
        range = api.get_frame_range()
        if bpy.context.scene.frame_current < range[0] or bpy.context.scene.frame_current > range[1]:
            return
        else:
            for obj in bpy.context.selected_objects:
                action = obj.animation_data.action
                curves = action.fcurves

                for curve in curves:
                    if curve.data_path.endswith("rotation_mode"):
                        continue
                    delta_y = api.get_curve_delta(context, obj, curve)
                    for k in curve.keyframe_points:
                        if prefs.offset_range_only:
                            range = api.get_frame_range()
                            if k.co_ui.x < range[0] or k.co_ui.x > range[1]:
                                continue
                            k.co_ui.y = k.co_ui.y + delta_y
                        else:
                            k.co_ui.y = k.co_ui.y + delta_y

                    curve.update()

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

        if not curves:
            area.type = old
            return {"CANCELLED"}

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
            return {"CANCELLED"}
        
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
                area.type = old
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
                    try:
                        for fcurve in ob.animation_data.action.fcurves:
                            arm_list.append(fcurve)          
                    except AttributeError:
                        area.type = old
                        self.report({"WARNING"}, f"There are no F-Curves available")  
                        return {"CANCELLED"}

            active_curves = [f for f in arm_list if active.name in f.data_path.split('"')[1]]

            bone_names_list = [b.name for b in objs if b != active]
            non_active_curves = [f for f in arm_list if f.data_path.split('"')[1] in bone_names_list]

        timings = []
        conv = []

        if isinstance(active_curves, bpy.types.bpy_prop_collection): # Object Mode
            for c in active_curves:
                conv.append(c)

            active_curves = conv

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
            if len(objs):
                bpy.context.view_layer.objects.active = objs[0]
            for ob in objs:
                if ob != active:
                    ob.select_set(True)   
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
                    try:
                        shape_keys = obj.data.shape_keys
                    except AttributeError:
                        break

                    if shape_keys:
                        for key in shape_keys.key_blocks:
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

class ABRA_OT_delete_static_channels(bpy.types.Operator):
    bl_idname = "screen.at_delete_static_channels"
    bl_label = "Delete Static Channels"
    bl_description = "Deletes any visible F-Curves that do not change value"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        use_oss = api.use_oss()[0]
        area = bpy.context.area
        old_type = area.type
        area.type = 'GRAPH_EDITOR'
        area.spaces[0].dopesheet.show_only_selected = use_oss
        visible = api.get_standard_curves()
        fd = 0
        
        if visible:
            wm = bpy.context.window_manager
            wm.progress_begin(0, len(visible))
            for ci, curve in enumerate(visible):
                api.dprint(f"[[ {curve.data_path} ]]", col="blue")
                kfp = curve.keyframe_points
                conf = len(kfp)
                numbers = np.zeros(conf)

                if conf:
                    for r, i in enumerate(kfp):
                        numbers[r] = i.co[1]

                    if np.min(numbers) == np.max(numbers):
                        api.dprint("--- Curve is static. Deleting...", col="red")
                        ac = curve.id_data
                        ac.fcurves.remove(curve)
                        fd += 1
                    else:
                        api.dprint("--- Curve is moving...", col="blue")
                wm.progress_update(ci)
            
            wm.progress_end()
            self.report({"INFO"}, f"Removed {fd} F-Curves")
            area.type = old_type
            
            return {"FINISHED"}
        else:
            area.type = old_type
            return {"CANCELLED"}

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
            use_oss = api.use_oss()[0]
            area = bpy.context.area
            old_type = area.type
            area.type = 'GRAPH_EDITOR'
            area.spaces[0].dopesheet.show_only_selected = use_oss

            # Get data ready for bake
            prefs = api.get_preferences()
            frange = api.get_frame_range()
            frame_const = bpy.context.scene.frame_current
            step = prefs.bake_framestep

            # Basic checks
            if api.get_visible_fcurves() is None:
                self.report({"WARNING"}, f"There are no F-Curves available")
                area.type = old_type
                return {"CANCELLED"}

            if bpy.context.mode == "POSE" or bpy.context.mode == "OBJECT":
                pass
            else:
                self.report({"ERROR"}, "This tool only works in Object or Pose Mode")
                area.type = old_type
                return {"CANCELLED"}
            
            baketime = time.time()
            phase1_baketime = baketime
            phase2_baketime = baketime
            phase3_baketime = baketime

            # Create an array containing frame numbers within range
            frames_to_remove = list(range(frange[0], frange[1]+1))

            # Prune frames from step
            frames_to_keep = frames_to_remove[0::step]
            pruned = [i for i in frames_to_remove if i not in frames_to_keep]

            api.dprint(f"Frames to keep: {frames_to_keep}")
            api.dprint(f"Frames to remove: {pruned}")

            visible = api.get_visible_fcurves()

            if prefs.bake_method == "NLA":
                bpy.ops.graph.reveal()
                visible = api.get_visible_fcurves()
                for i, curve in enumerate(visible):
                    if len(curve.keyframe_points):
                        api.dprint(f"Pruning curve: {str(curve.data_path)}", col="yellow")
                        if not re.search("(location$|rotation_quaternion$|rotation_euler$|scale$)", curve.data_path):
                            api.dprint(f"--- This is not a transform F-Curve. Inserting keys...", col="blue")
                            for ins in frames_to_remove:
                                curve.keyframe_points.insert(ins, curve.evaluate(ins), options={"FAST"})
                bpy.ops.graph.select_all(action='DESELECT')
                api.dprint(f"Baking using NLA...")
                bpy.ops.nla.bake(frame_start=frange[0], frame_end=frange[1], bake_types={bpy.context.mode}, visual_keying=prefs.visual_keying, clear_constraints=prefs.clear_constraints, clear_parents=prefs.clear_parents, use_current_action = True, clean_curves=prefs.clean_curves)

                bpy.ops.graph.interpolation_type(type=prefs.bake_type)
                bpy.ops.graph.handle_type(type=prefs.bake_handle)
                bpy.ops.graph.select_all(action='DESELECT')

            if api.fcurve_overload(visible):
                area.type = old_type
                self.report({"ERROR"}, f"Preventing overload ({prefs.fcurve_scan_limit} FCurves max, {len(visible)} active)")
                return {"CANCELLED"}

            wm = bpy.context.window_manager
            wm.progress_begin(0, len(visible))

            if prefs.bake_method == "Newton-Raphson":
                api.dprint(f"Baking using Newton-Raphson...")

                api.dprint(f"PHASE 1: PRE-BAKE", col="orange")
                for cl, curve in enumerate(visible):

                    bpy.ops.graph.select_all(action='DESELECT')

                    api.dprint(f"Pre-sampling curve {str(curve.data_path)}...", col="yellow")

                    try:
                        first_key_frame = curve.keyframe_points[0]
                        last_key_frame = curve.keyframe_points[-1]
                    except IndexError:
                        continue

                    # If a new key is inserted before first_key_frame or last_key_frame, and either of them are automatic tangents, it's going to create a gigantic overshoot that will be part of the final bake. We don't want this.
                    # As an attempt to avoid this, if the very first key is beyond the frame range bounds, insert keys backwards to prevent the automatic overshooting.
                    api.dprint(f"{first_key_frame.co[0]} || {last_key_frame.co[0]}")
                    
                    if first_key_frame.co[0] > frange[1] or last_key_frame.co[0] < frange[0]: # If the baked segment starts at a starting/end constant on F-Curve
                        api.dprint(f"Start/End Segment Case")

                        # We need to freeze the right handle of last key otherwise if it's automatic it will make a giant overshoot
                        if first_key_frame.co[0] > frange[1]:
                            api.dprint(f"--- Segment starts at beginning of F-Curve")
                            first_key_frame.handle_left_type = "FREE"
                            first_key_frame.handle_left[1] = first_key_frame.co[1]
                            
                        elif last_key_frame.co[0] < frange[0]:
                            api.dprint(f"--- Segment starts at end of F-Curve")
                            last_key_frame.handle_right_type = "FREE"
                            last_key_frame.handle_right[1] = last_key_frame.co[1]
                    
                    if first_key_frame.co[0] > frange[0] and first_key_frame.co[0] < frange[1]:
                        curve.keyframe_points.insert(first_key_frame.co[0]-1, curve.evaluate(first_key_frame.co[0]-1), options={"FAST"})
                        first_key_frame.handle_left_type = "AUTO_CLAMPED"
                        first_key_frame.handle_right_type = "AUTO_CLAMPED"

                        curve.keyframe_points.insert(frange[0], curve.evaluate(first_key_frame.co[0]), options={"FAST"})

                    if last_key_frame.co[0] > frange[0] and last_key_frame.co[0] < frange[1]:
                        curve.keyframe_points.insert(last_key_frame.co[0]+1, curve.evaluate(last_key_frame.co[0]+1), options={"FAST"})
                        last_key_frame.handle_left_type = "AUTO_CLAMPED"
                        last_key_frame.handle_right_type = "AUTO_CLAMPED"

                        curve.keyframe_points.insert(frange[1], curve.evaluate(last_key_frame.co[0]), options={"FAST"})

                    curve.keyframe_points.insert(frange[0], curve.evaluate(frange[0]), options={"FAST"})
                    curve.keyframe_points.insert(frange[1], curve.evaluate(frange[1]), options={"FAST"})
                    wm.progress_update(cl)


                # Using a hacky marker workaround to select range since its faster
                bpy.context.scene.timeline_markers.new("aT_tmp", frame=-999) # If the user is not using markers, make one. therwise context will fail
                bpy.ops.marker.select_all(action='DESELECT')
                bpy.context.scene.timeline_markers.new("bakeL", frame=frange[0])
                bpy.context.scene.timeline_markers.new("bakeR", frame=frange[1])

                bpy.ops.graph.select_column(mode='MARKERS_BETWEEN')
                bpy.context.scene.timeline_markers.remove(bpy.context.scene.timeline_markers[-1])
                bpy.context.scene.timeline_markers.remove(bpy.context.scene.timeline_markers[-1])
                bpy.context.scene.timeline_markers.remove(bpy.context.scene.timeline_markers["aT_tmp"])

                if bpy.app.version > (4,0,0):
                    bpy.ops.graph.bake_keys()
                else:
                    bpy.ops.graph.sample()

                phase1_baketime = round(time.time() - baketime, 2)

            


            api.dprint(f"PHASE 2: TANGENT SOLVING", col="orange")
            for clen, curve in enumerate(visible):
                if len(curve.keyframe_points):
                    if prefs.bake_method == "Newton-Raphson":

                        bpy.ops.graph.select_all(action='DESELECT')
                        
                        if step > 1:
                            for ins in frames_to_keep:
                                api.dprint(f"[[[ FRAME {ins} ]]]")
                                x = []
                                y = []
                                substeps = prefs.newton_substeps

                                key_now = api.get_key_index_at_frame(curve, ins)
                                key_next = api.get_key_index_at_frame(curve, ins+step)

                                if curve.keyframe_points[key_now].interpolation == "BEZIER":
                                    for i, v in enumerate(range(0, substeps+1)):
                                        next_step = ins + step
                                        xapp = (((next_step-ins)/substeps)*(v))+ins
                                        x.append(xapp)
                                        y.append(curve.evaluate(xapp))

                                        api.dprint(f"X = {xapp}, Y = {curve.evaluate(xapp)}")


                                    pts = np.array([x,y]).T
                                    handles = api.get_control_points_from_best_fit(pts, err=prefs.newton_err)

                                    x_bez = []
                                    y_bez = []

                                    for bez in handles:
                                        for pt in bez:
                                            x_bez.append(pt[0])
                                            y_bez.append(pt[1])
                                    api.dprint(f"Left Control Point: {x_bez[:2][1], y_bez[:2][1]}")
                                    api.dprint(f"Right Control Point: {x_bez[2:4][0], y_bez[2:4][0]}")

                                    curve.keyframe_points[key_now].handle_right_type = "FREE"
                                    curve.keyframe_points[key_now].handle_right[0] = x_bez[:2][1]
                                    curve.keyframe_points[key_now].handle_right[1] = y_bez[:2][1]

                                    curve.keyframe_points[key_next].handle_left_type = "FREE"
                                    curve.keyframe_points[key_next].handle_left[0] = x_bez[2:4][0]
                                    curve.keyframe_points[key_next].handle_left[1] = y_bez[2:4][0]

                                    if prefs.newton_autoalign:
                                        curve.keyframe_points[key_now].handle_right_type = "ALIGNED"
                                        curve.keyframe_points[key_next].handle_left_type = "ALIGNED"
                                else:
                                    api.dprint(f"Key is not bezier. Skipping...")

                                wm.progress_update(clen)

                for ins in pruned:
                    try:
                        curve.keyframe_points.remove(curve.keyframe_points[api.get_key_index_at_frame(curve, ins)])
                    except IndexError:
                        pass

            phase2_baketime = round(time.time() - baketime,2)

            wm.progress_end()

            # Remove overalpping keys incase of a double bake (dumb workaround)
            bpy.ops.graph.select_all(action='SELECT')
            bpy.ops.graph.clean(threshold=0)
            bpy.ops.graph.select_all(action='DESELECT')
                
            area.type = old_type
            api.dprint(f"{frange[1] - frange[0]} frames with {len(visible)} F-Curves solved in {phase2_baketime}s (prebake {phase1_baketime}s)", col="green")
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
            self.report({"ERROR"}, "This tool only works in Pose Mode")
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
            self.report({"ERROR"}, "This tool only works in Pose Mode")
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
            self.report({"ERROR"}, "This tool only works in Pose Mode")
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
            self.report({"ERROR"}, "This tool only works in Pose Mode")
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

    def invoke(self, context, event):
        prefs = api.get_preferences()
        pose_bypass = False
        arm_object = ""

        area = bpy.context.area
        old = area.type
        area.type = 'VIEW_3D'

        if event.shift:
            arm_object = context.active_object
            if bpy.context.mode == "POSE" and "aTCursorGizmoBridge" in bpy.context.active_object.data.bones:
                bpy.ops.pose.select_all(action='DESELECT')
                bpy.context.active_object.data.bones.active = bpy.context.active_object.data.bones["aTCursorGizmoBridge"]
                area.type = old
                return {"FINISHED"}

            elif bpy.context.mode == "OBJECT" and "aTCursorGizmo" in bpy.data.objects:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects["aTCursorGizmo"].select_set(True)
                area.type = old
                return {"FINISHED"}
            
            area.type = old
            return {"CANCELLED"}
            
        else:
            bpy.ops.view3d.snap_cursor_to_selected()

            if bpy.context.mode == "POSE" and bpy.context.active_object.type == "ARMATURE":
                pose_bypass = True
                arm_object = context.active_object
                if "aTCursorGizmoBridge" not in bpy.context.active_object.data.bones:
                    bpy.ops.object.editmode_toggle() # EDIT
                    bpy.ops.armature.select_all(action='DESELECT')
                    bpy.ops.armature.bone_primitive_add(name="aTCursorGizmoBridge") 
                    
                    bpy.context.active_object.data.edit_bones.active = arm_object.data.edit_bones["aTCursorGizmoBridge"]

                    # Place this bone in a collection that's going to be visible
                    if bpy.app.version > (4,0,0):
                        tcol = bpy.context.active_object.data.collections.new("aT_temp_col")
                        tcol.assign(arm_object.data.edit_bones["aTCursorGizmoBridge"])

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

                    if "aT_temp_col" in arm_object.data.collections:
                        arm_object.data.collections.remove(arm_object.data.collections["aT_temp_col"])
                        
                    bpy.ops.object.posemode_toggle() # POSE

            area.type = old
                    
            return {"FINISHED"}
    
@persistent
def gizmo_func(self, context):
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
        else:
            area.type = old_type
            return {"CANCELLED"}
            
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

cls = (clipboard, rot_scores,
ABRA_OT_nudge_left,
ABRA_OT_nudge_right,
ABRA_OT_key_selected,
ABRA_OT_key_visible,
ABRA_OT_key_copy,
ABRA_OT_key_paste,
ABRA_OT_key_copy_pose,
ABRA_OT_key_paste_pose,
ABRA_OT_key_delete,
ABRA_OT_switch_rotation,
ABRA_OT_rotation_switcher,
ABRA_OT_global_offset,
ABRA_OT_share_active_key_timing,
ABRA_OT_share_common_key_timing,
ABRA_OT_copy_timing,
ABRA_OT_key_shapekeys,
ABRA_OT_key_armature,
ABRA_OT_delete_static_channels,
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
ABRA_OT_paste_timing,
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