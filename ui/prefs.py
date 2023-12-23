import bpy
from os.path import basename, dirname
from bpy.types import AddonPreferences
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty

from ..core import key, quickView, api
from . import toolshelf
class AbraToolsPrefs(AddonPreferences):
    bl_idname = basename(dirname(dirname(__file__)))
    toolshelf_pages: EnumProperty(
        items=[
            ('home', 'Home', '', '', 0),
            None,
            ('quickview', 'Quick View', '', '', 1),
            ('fastkey', 'Keying', '', '', 2),
            ('tangents', 'Tangents', '', '', 3),
            ('selection', 'Selection', '', '', 4),
            ('other', 'Other', '', '', 5),
            ('custom', 'Scripts', '', '', 6),
            None,
            ('settings', 'Settings', '', '', 7),

        ],
        default='home'
    )

    abraon: BoolProperty(
        name = "AbraTools State",
        description = "For internal use. Checks whether AbraTools has overridden the preferences panel",
        default = False
    )

    vis_isolate: BoolProperty(
        name = quickView.ABRA_OT_isolate_curves.bl_label,
        description = quickView.ABRA_OT_isolate_curves.bl_description,
        default = True
    )

    isolate_curves: BoolProperty(
        name = "Isolate Curves Enabled",
        description = "For internal use. Checks if user enabled Isolate Curves",
        default = False
    )
    
    vis_auto_frame: BoolProperty(
        name = quickView.ABRA_OT_auto_frame.bl_label,
        description = quickView.ABRA_OT_auto_frame.bl_description,
        default = True
    )

    auto_frame: BoolProperty(
        name = "Auto Frame Enabled",
        description = "For internal use. Checks if user enabled Auto Frame",
        default = False
    )

    vis_overlay: BoolProperty(
        name = quickView.ABRA_OT_auto_overlay.bl_label,
        description = quickView.ABRA_OT_auto_overlay.bl_description,
        default = True
    )

    auto_overlay: BoolProperty(
        name = "Auto Overlay Enabled",
        description = "For internal use. Checks if user enabled Auto Overlay",
        default = False
    )

    vis_viewloc: BoolProperty(
        name = quickView.ABRA_OT_visible_loc.bl_label,
        description = quickView.ABRA_OT_visible_loc.bl_description,
        default = True
    )

    vis_viewrot: BoolProperty(
        name = quickView.ABRA_OT_visible_rot.bl_label,
        description = quickView.ABRA_OT_visible_rot.bl_description,
        default = True
    )

    vis_viewscl: BoolProperty(
        name = quickView.ABRA_OT_visible_scl.bl_label,
        description = quickView.ABRA_OT_visible_scl.bl_description,
        default = True
    )

    vis_viewshkey: BoolProperty(
        name = quickView.ABRA_OT_visible_keys.bl_label,
        description = quickView.ABRA_OT_visible_keys.bl_description,
        default = False
    )

    vis_viewprops: BoolProperty(
        name = quickView.ABRA_OT_visible_props.bl_label,
        description = quickView.ABRA_OT_visible_props.bl_description,
        default = False
    )

    vis_viewinfl: BoolProperty(
        name = quickView.ABRA_OT_visible_const.bl_label,
        description = quickView.ABRA_OT_visible_const.bl_description,
        default = False
    )

    vis_goto_left: BoolProperty(
        name = quickView.ABRA_OT_goto_keyframe_left.bl_label,
        description = quickView.ABRA_OT_goto_keyframe_left.bl_description,
        default = False
    )

    vis_goto_right: BoolProperty(
        name = quickView.ABRA_OT_goto_keyframe_right.bl_label,
        description = quickView.ABRA_OT_goto_keyframe_right.bl_description,
        default = False
    )

    ##################
    
    vis_keysel: BoolProperty(
        name = key.ABRA_OT_key_selected.bl_label,
        description = key.ABRA_OT_key_selected.bl_description,
        default = True
    )

    vis_keyvis: BoolProperty(
        name = key.ABRA_OT_key_visible.bl_label,
        description = key.ABRA_OT_key_visible.bl_description,
        default = True
    )

    vis_keycopy: BoolProperty(
        name = key.ABRA_OT_key_copy.bl_label,
        description = key.ABRA_OT_key_copy.bl_description,
        default = True
    )

    vis_keypaste: BoolProperty(
        name = key.ABRA_OT_key_paste.bl_label,
        description = key.ABRA_OT_key_paste.bl_description,
        default = True
    )

    vis_keycopypose: BoolProperty(
        name = key.ABRA_OT_key_copy_pose.bl_label,
        description = key.ABRA_OT_key_copy_pose.bl_description,
        default = True
    )

    vis_keypastepose: BoolProperty(
        name = key.ABRA_OT_key_paste_pose.bl_label,
        description = key.ABRA_OT_key_paste_pose.bl_description,
        default = True
    )

    vis_keydelete: BoolProperty(
        name = key.ABRA_OT_key_delete.bl_label,
        description = key.ABRA_OT_key_delete.bl_description,
        default = True
    )

    vis_keybake: BoolProperty(
        name = key.ABRA_OT_bake_keys.bl_label,
        description = key.ABRA_OT_bake_keys.bl_description,
        default = True,
    )

    vis_share_active: BoolProperty(
        name = key.ABRA_OT_share_active_key_timing.bl_label,
        description = key.ABRA_OT_share_active_key_timing.bl_description,
        default = True
    )

    vis_share_common: BoolProperty(
        name = key.ABRA_OT_share_common_key_timing.bl_label,
        description = key.ABRA_OT_share_common_key_timing.bl_description,
        default = True
    )

    vis_copy_timing: BoolProperty(
        name = key.ABRA_OT_copy_timing.bl_label,
        description = key.ABRA_OT_copy_timing.bl_description,
        default = True
    )
    
    vis_paste_timing: BoolProperty(
        name = key.ABRA_OT_paste_timing.bl_label,
        description = key.ABRA_OT_paste_timing.bl_description,
        default = True
    )

    vis_keyshape: BoolProperty(
        name = key.ABRA_OT_key_shapekeys.bl_label,
        description = key.ABRA_OT_key_shapekeys.bl_description,
        default = True
    )

    vis_keyarmature: BoolProperty(
        name = key.ABRA_OT_key_armature.bl_label,
        description = key.ABRA_OT_key_armature.bl_description,
        default = True
    )

    vis_keypath: BoolProperty(
        name = key.ABRA_OT_tangent_keypath.bl_label,
        description = key.ABRA_OT_tangent_keypath.bl_description,
        default = True
    )

    vis_keyretime: BoolProperty(
        name = key.ABRA_OT_key_retime.bl_label,
        description = key.ABRA_OT_key_retime.bl_description,
        default = False
    )

    ####### SELECTION #######

    vis_selchild: BoolProperty(
        name = key.ABRA_OT_select_children.bl_label,
        description = key.ABRA_OT_select_children.bl_description,
        default = True
    )

    vis_selparent: BoolProperty(
        name = key.ABRA_OT_select_parent.bl_label,
        description = key.ABRA_OT_select_parent.bl_description,
        default = True
    )

    vis_selmirror: BoolProperty(
        name = key.ABRA_OT_select_mirror.bl_label,
        description = key.ABRA_OT_select_mirror.bl_description,
        default = True
    )

    vis_selsiblings: BoolProperty(
        name = key.ABRA_OT_select_siblings.bl_label,
        description = key.ABRA_OT_select_siblings.bl_description,
        default = False
    )

    vis_cursor_gizmo: BoolProperty(
        name = key.ABRA_OT_cursor_gizmo.bl_label,
        description = key.ABRA_OT_cursor_gizmo.bl_description,
        default = False
    )

    cursor_gizmo: BoolProperty(
        name = "Cursor Gizmo Enabled",
        description = "For internal use. Checks if user enabled Cursor Gizmo",
        default = False
    )
    
    vis_available_axes: EnumProperty(
        name = "Toggleable Axes",
        description= "List of Axes to add to the toggle",
        items = (
            ("GLOBAL", "Global", ""),
            ("LOCAL", "Local", ""),
            ("NORMAL", "Normal", ""),
            ("GIMBAL", "Gimbal", ""),
            ("VIEW", "View", ""),
            ("CURSOR", "Cursor", ""),
            ("PARENT", "Parent", ""),
        ),
        default = {"GLOBAL", "LOCAL", "NORMAL"},
        options = {"ENUM_FLAG"},
    )

    vis_orient_switcher: BoolProperty(
        name = key.ABRA_OT_orient_switcher.bl_label,
        description = key.ABRA_OT_orient_switcher.bl_description,
        default = False
    )

    vis_cursortosel: BoolProperty(
        name = key.ABRA_OT_cursor_to_selected.bl_label,
        description = key.ABRA_OT_cursor_to_selected.bl_description,
        default = False
    )

    vis_toggle_cursor: BoolProperty(
        name = key.ABRA_OT_toggle_cursor_pivot.bl_label,
        description = key.ABRA_OT_toggle_cursor_pivot.bl_description,
        default = False
    )

    vis_selsets: BoolProperty(
        name = key.ABRA_OT_selection_sets.bl_label,
        description = key.ABRA_OT_selection_sets.bl_description,
        default = True
    )

    vis_selswaprigmode: BoolProperty(
        name = key.ABRA_OT_swap_rig_mode.bl_label,
        description = key.ABRA_OT_swap_rig_mode.bl_description,
        default = False
    )

    ####### TANGENTS #######

    vis_tanfree: BoolProperty(
        name = key.ABRA_OT_tangent_free.bl_label,
        description = key.ABRA_OT_tangent_free.bl_description,
        default = False
    )

    vis_tanaligned: BoolProperty(
        name = key.ABRA_OT_tangent_aligned.bl_label,
        description = key.ABRA_OT_tangent_aligned.bl_description,
        default = True
    )

    vis_tanvector: BoolProperty(
        name = key.ABRA_OT_tangent_vector.bl_label,
        description = key.ABRA_OT_tangent_vector.bl_description,
        default = False
    )

    vis_tanauto: BoolProperty(
        name = key.ABRA_OT_tangent_auto.bl_label,
        description = key.ABRA_OT_tangent_auto.bl_description,
        default = True
    )

    vis_tanautoclamp: BoolProperty(
        name = key.ABRA_OT_tangent_autoclamp.bl_label,
        description = key.ABRA_OT_tangent_autoclamp.bl_description,
        default = True
    )

    ####### OTHER #########

    vis_rangesel: BoolProperty(
        name = key.ABRA_OT_range_to_selection.bl_label,
        description = key.ABRA_OT_range_to_selection.bl_description,
        default = True
    )

    vis_rangemarkers: BoolProperty(
        name = key.ABRA_OT_range_to_markers.bl_label,
        description = key.ABRA_OT_range_to_markers.bl_description,
        default = True
    )

    ####### MOTION PATH #########

    path_calc: bpy.props.EnumProperty(
        name = "Range",
        items = (
            ("range", "Start to End", "Create motion paths for frame range"),
            ("currentEnd", "Current to End", "Create motion paths for the current frame to end of frame range"),
            ("currentAdd", "Current to Amount", "Create motion paths for the current frame to specified amount of frames ahead"),
        ),
        default = "range",
    )

    path_add: bpy.props.IntProperty(
        name = "Frames Ahead",
        description = "The amount of frames from the current frame to calculate a motion path. For example, if your current frame is 20 and Frames Ahead is 25, it will create a motion path for frames 20 to 45",
        default = 24,
        min = 1,
    )

    path_loc: bpy.props.EnumProperty(
        name = "Bone Path",
        items = (
            ("HEADS", "Heads", "Motion paths are baked on bone heads"),
            ("TAILS", "Tails", "Motion paths are baked on bone tails"),
        ),
        default = "TAILS",
    )

    ####### SETTINGS #######

    header_col: bpy.props.FloatVectorProperty(  
        name = "Header Color",
        subtype = 'COLOR',
        size = 4,
        min = 0.0, max = 1.0,
        description = "The color of the header while AbraTools is in use",
        update = toolshelf.updateHeader
    )

    button_width: bpy.props.FloatProperty(
        name = "Header Button Width",
        min = 0.8, max = 2.0,
        default = 1.0,
        description = "Sets the width of buttons in the toolshelf"
    )

    panel_scale: bpy.props.FloatProperty(
        name = "Menu Width Scale",
        min = 0.4, max = 2.0,
        default = 1.0,
        description = "Changes the maximum width of panels in the menu"
    )

    use_preview_range: bpy.props.BoolProperty(
        name = "Use Preview Range",
        default = False,
        description = "Certain tools utilize the current frame range for their tasks. When this is enabled, it will utilize the preview range instead, so long as it's available"
    )

    fcurve_scan_limit: bpy.props.IntProperty(
        name = "F-Curve Scan Limit",
        default = 0,
        description = "Prevents software hanging by blocking execution for specific tools that are looping through an exceeded amount of F-Curves (ex. Go To Previous/Next Keyframe). 0 disables this option.",
        min = 0
    )

    dev_debug: bpy.props.BoolProperty(
        name = "Debug Mode",
        default = False,
        description = "Developer use only. Prints additional content to the Blender console"
    )

    ######## RETIME PANEL #########
    retime_framestart: IntProperty(
        name = "Frame Start",
        description = "The frame that will retime all keys to the right of it",
        default = 0
    )

    retime_frameoffset: IntProperty(
        name = "Frame Offset",
        description = "The amount of frames the keys will be moved by",
        default = 0
    )

    retime_onlyvisible: BoolProperty(
        name = "Retime Selected",
        description = "Retimes keys of selected objects only. When disabled, it will retime all keys instead",
        default = False
    )

    retime_hiddenobjects: BoolProperty(
        name = "Retime Hidden Objects",
        description = "Retime hidden objects",
        default = True
    )

    retime_markers: BoolProperty(
        name = "Retime Markers",
        description = "Retime timeline markers",
        default = True
    )

    ######## BAKING PANEL ########

    bake_framestep: IntProperty(
        name = "Frame Step",
        description = "How many frames ahead until another key is baked",
        default = 2,
        min = 1
    )

    visual_keying: BoolProperty(
        name = "Visual Keying",
        description = "Bake out final/evaluated transforms, such as from F-Curve modifiers",
        default = False,
    )

    clean_curves: BoolProperty(
        name = "Clean Curves",
        description = "After baking, redundant/static keys will be removed",
        default = False,
    )

    clear_constraints: BoolProperty(
        name = "Clear Constraints",
        description = "After baking, constraints on selected objects will be removed",
        default = False,
    )

    clear_parents: BoolProperty(
        name = "Clear Parents",
        description = "After baking, parents on objects will be cleared",
        default = False,
    )

    bake_type: EnumProperty(
        name = "Interpolation",
        description = "The type of interpolation that baked keys will use. In most cases, Bezier is recommended",
        items = (
            ("CONSTANT", "Constant", "Baked keys will be set with a stepped/constant interpolation"),
            ("LINEAR", "Linear", "Baked keys will be set with a linear interpolation"),
            ("BEZIER", "Bezier", "Baked keys will be set with a Bezier interpolation"),
        ),
        default = "BEZIER",
    )

    bake_handle: EnumProperty(
        name = "Handle",
        description = "The type of handles that baked keys will use. In most cases, Automatic is recommended",
        items = (
            ("FREE", "Free", "Free"),
            ("ALIGNED", "Aligned", "Aligned"),
            ("VECTOR", "Vector", "Vector"),
            ("AUTO", "Automatic", "Automatic"),
            ("AUTO_CLAMPED", "Auto Clamped", "Auto Clamped"),
        ),
        default = "AUTO",
    )

cls = (AbraToolsPrefs,)