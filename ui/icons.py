import bpy.utils.previews, os

icons_coll = {}

icons = bpy.utils.previews.new()
icons_dir = os.path.join(os.path.dirname(__file__), "icons")
icons.load("logo", os.path.join(icons_dir, "logo.png"), 'IMAGE')
icons_coll["icons"] = icons