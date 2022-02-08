import bpy
from os.path import basename, dirname
from bpy.types import AddonPreferences
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty

from ..core import key, quickView
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
            ('other', 'Other', '', '', 4),

        ],
        default='home'
    )

    abraon: BoolProperty(
        name = "AbraTools State",
        description = "For internal use. Checks whether AbraTools has overridden the preferences panel",
        default = False
    )

    viewloc: BoolProperty(
        name = quickView.ABRA_OT_visible_loc.bl_label,
        description = quickView.ABRA_OT_visible_loc.bl_description,
        default = True
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

    ##################

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

    vis_keyshape: BoolProperty(
        name = key.ABRA_OT_key_shapekeys.bl_label,
        description = key.ABRA_OT_key_shapekeys.bl_description,
        default = True
    )

    vis_keypath: BoolProperty(
        name = key.ABRA_OT_tangent_keypath.bl_label,
        description = key.ABRA_OT_tangent_keypath.bl_description,
        default = True
    )

    vis_rangesel: BoolProperty(
        name = key.ABRA_OT_range_to_selection.bl_label,
        description = key.ABRA_OT_range_to_selection.bl_description,
        default = True
    )

    ##################

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

    def draw(self, context):
        prefs = bpy.context.preferences.addons["abTools"].preferences
        layout = self.layout
        layout.label(text="AbraTools works using a customized preferences page. In order to access it, click the button below.")
        rowAppend = layout.row()
        rowAppend.scale_y = 3
        rowAppend.operator("at.toggleprefs",text="Enter Toolshelf",icon="ASSET_MANAGER")

cls = (AbraToolsPrefs,)