import bpy

from . import prefs
from ..core import api

class ABRA_OT_mpathpanel(bpy.types.Operator):
    bl_label = "Motion Path Settings"
    bl_idname = "message.mpathpanel"
 
    def execute(self, context):
        self.report({'INFO'}, "Changes saved")
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 350)
 
    def draw(self, context):
        prefs = api.get_preferences()
        layout = self.layout
        if bpy.app.version < (3, 2, 0):
            layout.prop(prefs, "path_calc")
            if prefs.path_calc == "currentAdd":
                layout.prop(prefs, "path_add")
            layout.separator()
            
        else:
            active = bpy.context.active_object
            mode = bpy.context.mode

            if mode == "POSE":
                if active:
                    if active.pose:
                        layout.prop(active.pose.animation_visualization.motion_path, "type")
                        if active.pose.animation_visualization.motion_path.type == "RANGE":
                            layout.prop(active.pose.animation_visualization.motion_path, "frame_start")
                            layout.prop(active.pose.animation_visualization.motion_path, "frame_end")
                        if active.pose.animation_visualization.motion_path.type == "CURRENT_FRAME": 
                            layout.prop(active.pose.animation_visualization.motion_path, "frame_before")
                            layout.prop(active.pose.animation_visualization.motion_path, "frame_after")
                        layout.separator()
                        layout.prop(active.pose.animation_visualization.motion_path, "frame_step")
                        layout.prop(active.pose.animation_visualization.motion_path, "range")
                        layout.prop(prefs, "path_loc")
                    else:
                        layout.label(text="Active object does not support motion paths.")
                else:
                    layout.label(text="No active object is selected.")
            elif mode == "OBJECT":
                if active:
                    layout.prop(active.animation_visualization.motion_path, "type")
                    if active.animation_visualization.motion_path.type == "RANGE":
                        layout.prop(active.animation_visualization.motion_path, "frame_start")
                        layout.prop(active.animation_visualization.motion_path, "frame_end")
                    if active.animation_visualization.motion_path.type == "CURRENT_FRAME": 
                        layout.prop(active.animation_visualization.motion_path, "frame_before")
                        layout.prop(active.animation_visualization.motion_path, "frame_after")
                    layout.prop(active.animation_visualization.motion_path, "frame_step")
                    
                    layout.separator()
                    layout.prop(active.animation_visualization.motion_path, "range")
                    layout.prop(prefs, "path_loc")
                else:
                    layout.label(text="No active object is selected.")
            else:
                layout.label(text="Unsupported object")
                layout.label(text="Try selecting something in object/pose mode")

class ABRA_OT_retimepanel(bpy.types.Operator):
    bl_label = "Retime"
    bl_idname = "message.retimepanel"
    bl_options = {"REGISTER", "UNDO"}
 
    def execute(self, context):
        api.retime_keys()
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 350)
 
    def draw(self, context):
        prefs = api.get_preferences()
        layout = self.layout
        layout.prop(prefs, "retime_framestart", icon="TRIA_DOWN_BAR")
        layout.prop(prefs, "retime_frameoffset", icon="TRACKING_FORWARDS_SINGLE")
        layout.separator()
        layout.prop(prefs,"retime_onlyvisible")
        layout.prop(prefs,"retime_hiddenobjects")
        layout.prop(prefs,"retime_markers")

class ABRA_OT_offsetpanel(bpy.types.Operator):
    bl_label = "Global Offset"
    bl_idname = "message.offsetpanel"
    bl_options = {"REGISTER", "UNDO"}
 
    def execute(self, context):
        self.report({'INFO'}, "Changes saved")
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 122)
 
    def draw(self, context):
        prefs = api.get_preferences()
        layout = self.layout
        layout.prop(prefs, "offset_range_only")
        layout.prop(prefs, "offset_live_feedback")

class ABRA_OT_bakepanel(bpy.types.Operator):
    bl_label = "Bake Keys"
    bl_idname = "message.bakepanel"
    bl_options = {"REGISTER", "UNDO"}
 
    def execute(self, context):
        self.report({'INFO'}, "Changes saved")
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 250)
 
    def draw(self, context):
        prefs = api.get_preferences()
        layout = self.layout
        layout.prop(prefs, "bake_method")
        layout.prop(prefs, "bake_framestep")

        layout.separator()
        box = layout.box()
        if prefs.bake_method == "NLA":
            box.prop(prefs, "bake_type")
            box.prop(prefs, "bake_handle")
            box.prop(prefs, "visual_keying")
            box.prop(prefs, "clean_curves")
            box.prop(prefs, "clear_constraints")
            box.prop(prefs, "clear_parents")
        else:
            box.prop(prefs, "newton_err")
            box.prop(prefs, "newton_substeps")
            box.prop(prefs, "newton_autoalign")

class Set_Selector_Vars(bpy.types.PropertyGroup):
    renaming: bpy.props.BoolProperty(name="renaming", description="", default=False)
class Set_Selector(bpy.types.Operator):
    """Select this set of bones. You can also Shift + Click to add this set to your current selection"""
    bl_idname = "armature.set_selector"
    bl_label = "Set Selector"
    bl_options = {"REGISTER", "UNDO"}

    set_index: bpy.props.IntProperty(name="set_index", description="") # Acts as a bridge to tell operator what set to select

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        if not event.shift:
            bpy.ops.pose.select_all(action='DESELECT')

        api.select_bones_from_set(int(self.set_index))
        return {'FINISHED'}

    def execute(self, context):
        return {'FINISHED'}

class Rename_Set(bpy.types.Operator):
    """Rename a selection set"""
    bl_idname = "armature.rename_set"
    bl_label = "Rename Set"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        context.scene.set_selection.renaming = not context.scene.set_selection.renaming
        return {'FINISHED'}

    def execute(self, context):
        return {'FINISHED'}

class Create_Set(bpy.types.Operator):
    """Create a selection set for the current selected bones"""
    bl_idname = "armature.create_set"
    bl_label = "Create Set"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        api.add_set_from_selected_bones()
        return {'FINISHED'}

    def execute(self, context):
        return {'FINISHED'}

class Delete_Set(bpy.types.Operator):
    """Deletes active selection set"""
    bl_idname = "armature.delete_set"
    bl_label = "Delete Set"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        api.delete_active_selection_set()
        return {'FINISHED'}

    def execute(self, context):
        return {'FINISHED'}

class Move_Up(bpy.types.Operator):
    """Moves up the active set in the list"""
    bl_idname = "armature.move_up"
    bl_label = "Move Up"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        bpy.ops.pose.selection_set_move(direction='UP')
        return {'FINISHED'}

    def execute(self, context):
        return {'FINISHED'}

class Move_Down(bpy.types.Operator):
    """Moves down the active set in the list"""
    bl_idname = "armature.move_down"
    bl_label = "Move Down"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        bpy.ops.pose.selection_set_move(direction='DOWN')
        return {'FINISHED'}

    def execute(self, context):
        return {'FINISHED'}

class Assign_Bones(bpy.types.Operator):
    """Assigns selected bones to active selection set"""
    bl_idname = "armature.assign_bones"
    bl_label = "Assign Bones"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        bpy.ops.pose.selection_set_assign()
        return {'FINISHED'}

    def execute(self, context):
        return {'FINISHED'}

class Remove_Bones(bpy.types.Operator):
    """Removes selected bones from active selection set"""
    bl_idname = "armature.remove_bones"
    bl_label = "Remove Bones"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        bpy.ops.pose.selection_set_unassign()
        bpy.ops.pose.select_all(action='DESELECT')
        api.select_bones_from_set(int(context.active_object.active_selection_set))
        return {'FINISHED'}

    def execute(self, context):
        return {'FINISHED'}

class ABRA_OT_selsetspanel(bpy.types.Operator):
    bl_label = "Selection Sets Panel"
    bl_idname = "message.selsetspanel"
 
    def execute(self, context):
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 350)
 
    def draw(self, context):
        layout = self.layout.row()
        colLeft = layout.column()
        colRight = layout.column()

        active = bpy.context.active_object
        mode = bpy.context.mode

        if api.is_addon_enabled("bone_selection_sets"):
            if mode == "POSE":
                row = layout.column()
                if len(active.selection_sets) > 0:
                    colRight.operator('armature.create_set', icon="ADD", text="")
                    colRight.operator('armature.delete_set', icon="REMOVE", text="")
                    colRight.operator('armature.rename_set', icon="OUTLINER_DATA_GP_LAYER", text="", depress=context.scene.set_selection.renaming)
                    colRight.separator()
                    colRight.operator('armature.move_up', icon="TRIA_UP", text="")
                    colRight.operator('armature.move_down', icon="TRIA_DOWN", text="")
                    colRight.separator()
                    colRight.operator('armature.assign_bones', icon="PINNED", text="")
                    colRight.operator('armature.remove_bones', icon="UNPINNED", text="")
                    for i, set in enumerate(active.selection_sets):
                        activeSet = active.selection_sets[active.active_selection_set]
                        if set.name == activeSet.name:
                            if context.scene.set_selection.renaming:
                                colLeft.prop(activeSet, "name", icon_only=True)
                                continue
                            else:
                                colLeft.operator('armature.set_selector', text=set.name,depress=True).set_index = i
                        else:
                            colLeft.operator_context = 'INVOKE_DEFAULT'
                            colLeft.operator('armature.set_selector', text=set.name).set_index = i
                else:
                    row.label(text="No selection sets exist for this armature.")
                    row.operator('armature.create_set', icon="ADD", text="Create a set from current selection")
            else:
                layout.label(text="This tool only supports Pose Mode")
        else:
            layout.label(text="Please enable 'Bone Selection Sets' addon to use")

class ABRA_OT_axispanel(bpy.types.Operator):
    bl_label = "Orientations"
    bl_idname = "message.axispanel"
 
    def execute(self, context):
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 90)
 
    def draw(self, context):
        prefs = api.get_preferences()

        layout = self.layout.row()
        colLeft = layout.column()

        colLeft.prop(prefs, "vis_available_axes")

cls = (ABRA_OT_mpathpanel,
ABRA_OT_selsetspanel,
ABRA_OT_retimepanel,
ABRA_OT_offsetpanel,
ABRA_OT_bakepanel,
ABRA_OT_axispanel,
Set_Selector,
Set_Selector_Vars,
Rename_Set,
Create_Set,
Delete_Set,
Move_Up,
Move_Down,
Assign_Bones,
Remove_Bones)