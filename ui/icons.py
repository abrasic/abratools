import bpy.utils.previews, os

icons_coll = {}

icons = bpy.utils.previews.new()
icons_dir = os.path.join(os.path.dirname(__file__), "icons")
icons.load("logo", os.path.join(icons_dir, "logo.png"), 'IMAGE')

icons.load("copy_keys", os.path.join(icons_dir, "copy_keys.png"), 'IMAGE')
icons.load("create_path", os.path.join(icons_dir, "create_path.png"), 'IMAGE')
icons.load("delete_path", os.path.join(icons_dir, "delete_path.png"), 'IMAGE')
icons.load("delete_keys", os.path.join(icons_dir, "delete_keys.png"), 'IMAGE')
icons.load("isolate_curves", os.path.join(icons_dir, "isolate_curves.png"), 'IMAGE')
icons.load("key_all_shapes", os.path.join(icons_dir, "key_all_shapes.png"), 'IMAGE')
icons.load("key_selected", os.path.join(icons_dir, "key_selected.png"), 'IMAGE')
icons.load("key_visible", os.path.join(icons_dir, "key_visible.png"), 'IMAGE')
icons.load("key_whole_armature", os.path.join(icons_dir, "key_whole_armature.png"), 'IMAGE')
icons.load("paste_keys", os.path.join(icons_dir, "paste_keys.png"), 'IMAGE')
icons.load("range_to_selection", os.path.join(icons_dir, "range_to_selection.png"), 'IMAGE')
icons.load("view_const", os.path.join(icons_dir, "view_const.png"), 'IMAGE')
icons.load("view_loc", os.path.join(icons_dir, "view_loc.png"), 'IMAGE')
icons.load("view_props", os.path.join(icons_dir, "view_props.png"), 'IMAGE')
icons.load("view_rot", os.path.join(icons_dir, "view_rot.png"), 'IMAGE')
icons.load("view_scale", os.path.join(icons_dir, "view_scale.png"), 'IMAGE')
icons.load("view_shapes", os.path.join(icons_dir, "view_shapes.png"), 'IMAGE')

icons_coll["icons"] = icons