import bpy, math

def get_frame_range():
    return [bpy.context.scene.frame_start, bpy.context.scene.frame_end]

def get_current_frame():
    return bpy.context.scene.frame_current

def get_visible_fcurves():
    arg = bpy.context.visible_fcurves
    return None if arg == [] else arg

def get_selected_fcurves(visible=False):
    if visible:
        return bpy.context.selected_visible_fcurves
    else:
        return bpy.context.selected_editable_fcurves

def get_fcurve_data_path(curve):
    return curve.data_path

def set_keyset(str):
    """Changes active KeyingSet"""
    bpy.context.scene.keying_sets_all.active = bpy.context.scene.keying_sets_all[str]

def get_keyset():
    return bpy.context.scene.keying_sets_all.active

def get_selected_keys(curve):
    """Function will return an index of selected keyframes"""

    keysIndex = []
    k = curve.keyframe_points

    for i, k in k.items():
        if k.select_control_point:
            keysIndex.append(i)

    return keysIndex if keysIndex else None

def get_key_coords(curve, key):
    """Returns [x,y] coordinates of key from specified curve"""
    return [curve.keyframe_points[key].co[0] , curve.keyframe_points[key].co[1]]

def get_key_handle_coords(curve, key):
    """Returns [x1, y1, x2, y2] coordinates of left/right key handles"""
    return [curve.keyframe_points[key].handle_left[0], curve.keyframe_points[key].handle_left[1], curve.keyframe_points[key].handle_right[0], curve.keyframe_points[key].handle_left[1]]

def get_handle_distance(curve, key):
    """Returns [x1, y1, x2, y2] distance of handles from key"""
    key_coords = get_key_coords(curve, key)
    handle_coords = get_key_handle_coords(curve, key)
    x1 = abs(key_coords[0] - handle_coords[0])
    y1 = abs(key_coords[1] - handle_coords[1])
    x2 = abs(key_coords[0] - handle_coords[2])
    y2 = abs(key_coords[1] - handle_coords[3])

    return [x1, y1, x2, y2]

def get_handle_hypotenuse(curve, key):
    """Returns [hypotenuse, hypotenuse] of both key handles"""
    distances = get_handle_distance(curve, key)
    hypoX = (math.sqrt(distances[0]) + math.sqrt(math.degrees(distances[1]))) ** 2
    hypoY = (math.sqrt(distances[2]) + math.sqrt(math.degrees(distances[3]))) ** 2
    return [hypoX, hypoY]

def set_handle_angle(curve, key, angle, weight):
    """Sets the handle by angle relative to the key."""
    keyCoords = get_key_coords(curve, key)
    adjacent = weight*(math.cos(angle))
    opposite = weight*(math.sin(angle))
    curve.keyframe_points[key].handle_left_type = "FREE"
    curve.keyframe_points[key].handle_right_type = "FREE"
    curve.keyframe_points[key].handle_right = [keyCoords[0]+adjacent, keyCoords[1]+opposite]

def get_key_from_curve_index(curve, int):
    """Returns the key on specified curve index, NOT SELECTED INDEX"""
    return curve.keyframe_points[int]

def get_key_from_selected_index(curve, int):
    """Returns the key on specified selected index"""
    return get_selected_keys(curve)[int]

def get_selection_left_neighbour(curve, keys):
    """Returns the left neighbour of a key selection. Essentially this is the first key to the left that is not selected. Returns None if selection contains no neighbour."""
    # IMPORTANT! This function requires an ARRAY of keys!
    # IMPORTANT! This function will always return one Keyframe. If you have Keyframes [1, 2, 3, 4] and you select [2, 4], it will return Keyframe 1.
    keyBefore = curve.keyframe_points[keys[0]]
    keyN = curve.keyframe_points[keys[0]-1]
    return keyN if keyBefore.co[0] > keyN.co[0] else None

def get_selection_right_neighbour(curve, keys):
    """Returns the right neighbour of a key selection. Essentially this is the first key to the right that is not selected. Returns None if selection contains no neighbour."""
    # IMPORTANT! This function requires an ARRAY of keys!
    # IMPORTANT! This function will always return one Keyframe. If you have Keyframes [1, 2, 3, 4] and you select [2, 4], it will return Keyframe 1.
    keyBefore = curve.keyframe_points[keys[0]]
    try:
        keyN = curve.keyframe_points[keys[0]+1]
        return keyN
    except IndexError:
        return None


def get_key_left_neighbour(curve, key):
    """Returns the left neighbour of a key."""
    keyBefore = curve.keyframe_points[key]
    keyN = curve.keyframe_points[key-1]
    if keyN:
        return keyN if keyBefore.co[0] > keyN.co[0] else None
    else:
        return None

def get_key_right_neighbour(curve, key):
    """Returns the right neighbour of a key."""
    try:
        keyLen = len(curve.keyframe_points)
        keyT = curve.keyframe_points[key]
        return keyT
    except IndexError:
        return None

    
def insert_key(keys, x, y, select=False):
    """Inserts a key on specified key array"""
    k = keys.insert(x, y)

    k.select_control_point = select
    k.select_left_handle = select
    k.select_right_handle = select
    return k

def set_area(area, type=None):
    area = bpy.context.area
    area.type = 'GRAPH_EDITOR'

    if type=="ui":
        area.ui_type = 'GRAPH_EDITOR'

def set_tangent(tan):
    area = bpy.context.area
    old_type = area.type
    area.type = 'GRAPH_EDITOR'
    if get_selected_fcurves():
        bpy.ops.graph.handle_type(type=tan)
    area.type = old_type
    
def key_clipboard(self, type=None):
    area = bpy.context.area
    old_type = area.type
    area.type = 'GRAPH_EDITOR'
    
    if (type=="copy"):
        if get_visible_fcurves():
            bpy.ops.graph.select_all(action='DESELECT')
            bpy.ops.graph.select_column(mode='CFRA')
            try:
                bpy.ops.graph.copy()
            except RuntimeError:
                self.report({"INFO"}, "No keys on playhead")
            bpy.ops.graph.select_all(action='DESELECT')
    
    elif (type=="paste"):
        try:
            bpy.ops.graph.paste()
        except RuntimeError:
            self.report({"INFO"}, "No keys to paste")
            
    area.type = old_type
 
def get_selected_bones():
    """Returns int of total bones selected. If user is not in pose mode, 0 is returned"""
    if bpy.context.mode == "POSE":
        return len(bpy.context.selected_pose_bones)
    else:
        return 0