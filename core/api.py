import bpy, addon_utils, math

def dprint(text, col=None):
    prefs = bpy.context.preferences.addons["abTools"].preferences
    if prefs.dev_debug:
        color = '\x1b[1;30;40m'
        match col:
            case 'red':
                color = '\x1b[7;31;40m'
            case 'yellow':
                color = '\x1b[7;33;40m'
            case 'green':
                color = '\x1b[7;32;40m'
            case 'blue':
                color = '\x1b[7;34;40m'
            case 'cyan':
                color = '\x1b[7;36;40m'
            case 'purple':
                color = '\x1b[7;35;40m'
            case 'white':
                color = '\x1b[7;37;40m'
            case _:
                color = '\x1b[1;30;40m'

        print(color + 'ABRATOOLS DEBUG:' + '\x1b[0m ' + text)

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

def get_range_from_selected_keys():
    """Returns [min, max] of frame range of leftmost and rightmost selected keys"""
    curves = get_selected_fcurves()
    minimum = None
    maximum = None
    if curves:
        for curve in curves:
            keys = get_selected_keys(curve)
            if keys:
                firstKey = get_key_coords(curve, keys[0])[0]
                lastKey = get_key_coords(curve, keys[-1])[0]
                if not minimum or firstKey < minimum:
                    minimum = firstKey
                if not maximum or lastKey > maximum:
                    maximum = lastKey
                    
        if minimum > maximum:
            omax = minimum
            minimum = maximum
            maximum = omax

    return [minimum, maximum]

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

def select_bones_from_set(int):
    """Selects bones from selection set of active object."""
    bpy.context.object.active_selection_set = int
    bpy.ops.pose.selection_set_select()

def rename_active_selection_set(str):
    active = bpy.context.active_object
    active.selection_sets[active.active_selection_set].name = str

def add_set_from_selected_bones():
    """Creates a new selection set and assign selected bones to it"""
    active = bpy.context.active_object

    if active.type == "ARMATURE" and bpy.context.mode == "POSE":
        bpy.ops.pose.selection_set_add()
        bpy.ops.pose.selection_set_assign()
        rename_active_selection_set("New Set " + str(active.active_selection_set))

def delete_active_selection_set():
    active = bpy.context.active_object

    if active.type == "ARMATURE" and bpy.context.mode == "POSE":
        bpy.ops.pose.selection_set_remove()

    
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
    only_show_selected = use_oss()
    area.type = 'GRAPH_EDITOR'
    area.spaces[0].dopesheet.show_only_selected = only_show_selected[0]

    if only_show_selected[1]:
        bpy.ops.graph.reveal() # Dopesheet elements cannot be hidden; this is so you expect all visible keys to be removed

    if (type=="copy"):
        if get_visible_fcurves():
            if not get_selected_fcurves():
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

    elif (type=="delete"):
        try:
            curves = get_visible_fcurves()
            curves_are_active = False
            if curves:
                for curve in curves:
                    if curve.select:
                        curves_are_active = True
                        break
            if curves_are_active:
                bpy.ops.graph.delete()
            else:
                bpy.ops.graph.select_column(mode='CFRA')
                bpy.ops.graph.delete()
        except RuntimeError:
            self.report({"INFO"}, "No keys to delete")

            
    area.type = old_type

def retime_keys():
    prefs = bpy.context.preferences.addons["abTools"].preferences
    area = bpy.context.area
    old_type = area.type
    old_mode = bpy.context.mode
    area.type = 'DOPESHEET_EDITOR'

    bpy.ops.object.mode_set(mode='OBJECT')

    dprint("Only show selected is set to "+ str(prefs.retime_onlyvisible))
    area.spaces[0].dopesheet.show_only_selected = prefs.retime_onlyvisible
    dprint("Show hidden objects "+ str(prefs.retime_onlyvisible))
    area.spaces[0].dopesheet.show_hidden = prefs.retime_hiddenobjects

    # Transform all selected keys
    bpy.ops.action.select_leftright(mode='RIGHT')
    dprint("Transforming keys "+ str(prefs.retime_frameoffset)+ "frames ahead")
    bpy.ops.transform.transform(mode='TIME_TRANSLATE', value=(prefs.retime_frameoffset, 0, 0, 0), orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False))

    # Select and transform markers
    dprint("Moving markers")
    if prefs.retime_markers and len(bpy.context.scene.timeline_markers):
        bpy.ops.marker.select_leftright(mode='RIGHT')
        bpy.ops.marker.move(frames=prefs.retime_frameoffset)

    # Add to end frame range
    dprint("Extending frame range")
    bpy.context.scene.frame_end += int(prefs.retime_frameoffset)

    # Cleanup
    dprint("Cleaning up selections")
    bpy.ops.action.select_all(action='DESELECT')
    #bpy.ops.marker.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode=old_mode)
    area.type = old_type
    dprint("Done")
    return True
 
def get_selected_bones():
    """Returns int of total bones selected. If user is not in pose mode, 0 is returned"""
    if bpy.context.mode == "POSE":
        return len(bpy.context.selected_pose_bones)
    else:
        return 0

def is_addon_enabled(name):
    """Returns bool. Checks if addon "name" is installed and enabled. Used for third-party functions."""
    try:
        if bpy.context.preferences.addons[name]:
            return True
        else:
            return False
    except KeyError:
        return False

def enable_addon(self, name):
    try:
        addon_utils.enable(name, default_set=True)
    except ModuleNotFoundError:
        self.report({"INFO"}, "Module not found")

def use_oss():
    """Returns [bool, bool]. Runs through all time-based areas in the active screen and look for OSS. If it's off, immediately break and return false to use for key management."""
    use_selected = True
    reveal_curves = False
    for area in bpy.context.screen.areas:
        if area.type == 'GRAPH_EDITOR':
            for space in area.spaces:
                if space.type == "GRAPH_EDITOR":
                    print("Detected graph editor with: "+ str(space.dopesheet.show_only_selected))
                    if space.dopesheet.show_only_selected == False:
                        use_selected = False
                        break
        elif area.type == 'DOPESHEET_EDITOR':
            for space in area.spaces:
                if space.type == "DOPESHEET_EDITOR":
                    print("Detected dope sheet with: "+ str(space.dopesheet.show_only_selected))
                    if space.dopesheet.show_only_selected == False:
                        reveal_curves = True
                        use_selected = False
                        break

    return [use_selected, reveal_curves]