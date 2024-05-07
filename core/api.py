import bpy, blf, addon_utils, os, math, importlib.util
import numpy as np
from . import api
vp_text = None

def get_preferences():
    """Returns AddonPreferences type"""
    name = __package__.split(".")[0]
    return bpy.context.preferences.addons[name].preferences

def dprint(text, col=None):
    prefs = get_preferences()
    if prefs.dev_debug:
        color = '\x1b[1;30;40m'
        if col  == 'red':
            color = '\x1b[7;31;40m'
        elif col == 'yellow':
            color = '\x1b[7;33;40m'
        elif col == 'green':
            color = '\x1b[7;32;40m'
        elif col == 'blue':
            color = '\x1b[7;34;40m'
        elif col == 'cyan':
            color = '\x1b[7;36;40m'
        elif col == 'purple':
            color = '\x1b[7;35;40m'
        elif col == 'white':
            color = '\x1b[7;37;40m'
        else:
            color = '\x1b[1;30;40m'

        print(color + 'ABRATOOLS DEBUG:' + '\x1b[0m ' + str(text))

def get_frame_range():
    prefs = get_preferences()

    if prefs.use_preview_range and bpy.context.scene.use_preview_range:
        return [bpy.context.scene.frame_preview_start, bpy.context.scene.frame_preview_end]
    else:
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
    
def get_standard_curves():
    gsf = get_selected_fcurves()
    if len(gsf):
        return gsf
    else:
        return bpy.context.visible_fcurves

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
    curves = get_visible_fcurves()
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

        if minimum == None or maximum == None:
            return [0,0]
        elif minimum > maximum:
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
    key_coords = [curve.keyframe_points[key].co[0] , curve.keyframe_points[key].co[1]]
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

def get_key_index_at_frame(curve, frame):
    """Return the index of the key at the given frame."""
    for k in range(len(curve.keyframe_points)):
        if frame == curve.keyframe_points[k].co[0]:
            return k
    return -1

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

def select_keys_on_column(selected_only=True):
    """Selects keyframes that lie on the playhead. Do note that this function preserves channel selections and only affects keyframe selection."""
    if selected_only:
        curves = get_selected_fcurves()
        if curves:
            for curve in curves:
                if len (curve.keyframe_points):
                    key_index = get_key_index_at_frame(curve,bpy.context.scene.frame_current)
                    key = curve.keyframe_points[key_index]
                    if key.co[0] == bpy.context.scene.frame_current:
                        key.select_control_point = True
    else:
        bpy.ops.graph.select_column(mode='CFRA')

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
    
    elif (type=="paste"):
        try:
            bpy.ops.graph.paste(merge='OVER_RANGE')
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
    prefs = get_preferences()
    area = bpy.context.area
    old_type = area.type
    old_mode = bpy.context.mode
    area.type = 'DOPESHEET_EDITOR'

    bpy.ops.object.mode_set(mode='OBJECT')

    dprint("Only show selected is "+ str(prefs.retime_onlyvisible))
    area.spaces[0].dopesheet.show_only_selected = prefs.retime_onlyvisible
    dprint("Show hidden objects is "+ str(prefs.retime_onlyvisible))
    area.spaces[0].dopesheet.show_hidden = prefs.retime_hiddenobjects

    # Transform all selected keys
    bpy.ops.action.select_leftright(mode='RIGHT')
    dprint("Transforming keys "+ str(prefs.retime_frameoffset)+ " frames ahead")
    bpy.ops.transform.transform(mode='TIME_TRANSLATE', value=(prefs.retime_frameoffset, 0, 0, 0), orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False))

    # Select and transform markers
    if len(bpy.context.scene.timeline_markers):
        dprint("Moving markers")
        bpy.ops.marker.select_all(action='DESELECT')
        bpy.ops.marker.select_leftright(mode='RIGHT')
        if prefs.retime_markers:
            for marker in bpy.context.scene.timeline_markers:
                if marker.select:
                    bpy.ops.marker.move(frames=prefs.retime_frameoffset)
                    bpy.ops.marker.select_all(action='DESELECT')
                    break
    else:
        dprint("No markers in this scene")

    # Add to end frame range
    dprint("Extending frame range")
    bpy.context.scene.frame_end += int(prefs.retime_frameoffset)

    # Cleanup
    dprint("Cleaning up selections")
    bpy.ops.action.select_all(action='DESELECT')
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
                    api.dprint("Detected graph editor with: "+ str(space.dopesheet.show_only_selected))
                    if space.dopesheet.show_only_selected == False:
                        use_selected = False
                        break
        elif area.type == 'DOPESHEET_EDITOR':
            for space in area.spaces:
                if space.type == "DOPESHEET_EDITOR":
                    api.dprint("Detected dope sheet with: "+ str(space.dopesheet.show_only_selected))
                    if space.dopesheet.show_only_selected == False:
                        reveal_curves = True
                        use_selected = False
                        break

    return [use_selected, reveal_curves]

def is_bone_visible(bone, layers):
    """Returns Bool. Determines if the bone is visible via active bone layers."""
    if bpy.app.version[0] >= 4:
        for layer in layers:
            try:
                if bone.collections[layer]:
                    return True
            except KeyError:
                    return False
    else:
        for layer in layers:
            if bone.layers[layer]:
                return True
            else:
                return False
            
def get_custom_scripts():
    files = []
    """Returns array consisting of [str file.py, str script_info name, str icon name]. Retrieves python files located in <root>/scripts."""
    custom_scripts = os.path.join(os.path.dirname(__file__), os.pardir, "scripts")
    for file in os.listdir(custom_scripts):
        if os.path.splitext(file)[1] == ".py":
            
            spec = importlib.util.spec_from_file_location("atools_" + os.path.splitext(file)[0],custom_scripts + "\\" + file)
            modu = importlib.util.module_from_spec(spec)
            
            spec.loader.exec_module(modu) # Accesses file
            
            try:
                if modu.script_info:
                    if modu.script_info.name:
                        files.append([file, modu.script_info.name, modu.script_info.icon])
            except AttributeError:
                pass
            
    return files

def fcurve_overload(fcurves):
    """Returns bool. True if F-Curve/array length exceeds user-specified scan limit. """
    prefs = get_preferences()
    if prefs.fcurve_scan_limit == 0:
        return False
    elif len(fcurves) > prefs.fcurve_scan_limit:
        return True
    else:
        return False
        
def select_keys_in_range(min,max):
    bpy.ops.graph.select_box(mode="SET",xmin=min-1,xmax=max+1,ymin=-2**30,ymax=2**30, include_handles=False, use_curve_selection=True)
    
    return None

def are_keys_selected(curves):
    """Returns bool. True if any keyframes are selected from fcurves given."""
    for curve in curves:
        for key in curve.keyframe_points:
            if key.select_control_point:
                return True
            
    return False

def get_control_points_from_best_fit(pts, err):
    """Returns bezier curve that would best fit the given points"""

    ctrl_left = np_normalize(pts[1] - pts[0])
    ctrl_right = np_normalize(pts[-2] - pts[-1])
    return fit_curve(pts, ctrl_left, ctrl_right, err)

### Global Offset Delta 
# Courtesy of AnimAide ( rip :'( )
def get_curve_delta(context, obj, curve):
    frame = bpy.context.scene.frame_current
    nla_frame = int(bpy.context.object.animation_data.nla_tweak_strip_time_to_scene(frame))
    diff = nla_frame - frame

    try:
        val = obj.path_resolve(curve.data_path)
    except:
        val = None

    if val:
        try:
            target = val[curve.array_index]
        except TypeError:
            target = val
        return target - curve.evaluate(frame-diff)
    else:
        return 0
    
def write_text(text):
    global vp_text
    def callback(self, context):
        blf.position(0, 45, 45, 0)
        blf.color(0, 1, 0.17, 0.17, 0.75)
        blf.size(0, 16.0)
        blf.draw(0, text)

    if not vp_text:
        vp_text = bpy.types.SpaceView3D.draw_handler_add(callback, (None, None), 'WINDOW', 'POST_PIXEL')

def remove_text():
    global vp_text

    if vp_text:
        bpy.types.SpaceView3D.draw_handler_remove(vp_text, 'WINDOW')
        vp_text = None

### CURVE FITTING FUNCTIONS
# Courtesy of https://stackoverflow.com/questions/75489204

def q(p,t):
    return (1.0-t)**3 * p[0] + 3*(1.0-t)**2 * t * p[1] + 3*(1.0-t)* t**2 * p[2] + t**3 * p[3]

def q_prime(p,t):
    return 3*(1.0-t)**2 * (p[1]-p[0]) + 6*(1.0-t) * t * (p[2]-p[1]) + 3*t**2 * (p[3]-p[2])

def q_prime_prime(p,t):
    return 6*(1.0-t) * (p[2]-2*p[1]+p[0]) + 6*(t) * (p[3]-2*p[2]+p[1])

def newton_raphson(bez, point, u):
    d = q(bez, u)-point
    numerator = (d * q_prime(bez, u)).sum()
    denominator = (q_prime(bez, u)**2 + d * q_prime_prime(bez, u)).sum()

    if denominator == 0.0:
        return u
    else:
        return u - numerator/denominator

def parametrize(pts):
    u = [0.0]
    for i in range(1, len(pts)):
        u.append(u[i-1] + np.linalg.norm(pts[i] - pts[i-1]))

    for i, v in enumerate(u):
        u[i] = u[i] / u[-1]

    return u

def reparametrize(bez, pts, u):
    return [newton_raphson(bez, point, u) for point, u in zip(pts, u)]

def generate_curve(pts, u, lt, rt):
    bez = [pts[0], None, None, pts[-1]]

    A = np.zeros((len(u), 2,2))
    for i, v in enumerate(u):
        A[i][0] = lt  * 3*(1-v)**2 * v
        A[i][1] = rt * 3*(1-v)    * v**2

    C = np.zeros((2,2))
    X = np.zeros(2)

    for i, (pt, u) in enumerate(zip(pts,u)):
        C[0][0] += np.dot(A[i][0], A[i][0])
        C[0][1] += np.dot(A[i][0], A[i][1])
        C[1][0] += np.dot(A[i][0], A[i][1])
        C[1][1] += np.dot(A[i][1], A[i][1])

        t = pt - q([pts[0], pts[0], pts[-1], pts[-1]], u)

        X[0] += np.dot(A[i][0], t)
        X[1] += np.dot(A[i][1], t)

    det_C0_C1 = C[0][0] * C[1][1] - C[1][0] * C[0][1]
    det_C0_X  = C[0][0] * X[1] - C[1][0] * X[0]
    det_X_C1  = X[0] * C[1][1] - X[1] * C[0][1]

    alpha_l = 0.0 if det_C0_C1 == 0 else det_X_C1 / det_C0_C1
    alpha_r = 0.0 if det_C0_C1 == 0 else det_C0_X / det_C0_C1

    segLength = np.linalg.norm(pts[0] - pts[-1])
    epsilon = 1.0e-6 * segLength
    if alpha_l < epsilon or alpha_r < epsilon:
        bez[1] = bez[0] + lt * (segLength / 3.0)
        bez[2] = bez[3] + rt * (segLength / 3.0)

    else:
        bez[1] = bez[0] + lt * alpha_l
        bez[2] = bez[3] + rt * alpha_r

    return bez

def get_max_error(pts, bez, u):
    max_dist = 0.0
    split = len(pts)/2
    for i, (point, u) in enumerate(zip(pts, u)):
        dist = ((q(bez,u)-point)**2).sum(-1)
        #dist = np.linalg.norm(q(bez, u)-point)**2
        if dist > max_dist:
            max_dist = dist
            split = i

    return max_dist, split

def fit_curve(pts, lt, rt, err):

    if len(pts) == 2:
        dist = np.linalg.norm(pts[0] - pts[1]) / 3.0
        bez = [pts[0], pts[0] + lt * dist, pts[1] + rt * dist, pts[1]]
        return [bez]

    u = parametrize(pts)
    bez = generate_curve(pts, u, lt, rt)

    max_err, split = get_max_error(pts, bez, u)
    if max_err < err:
        return [bez]
    
    if max_err < err**2:
        for i in range(20):
            up = reparametrize(bez, pts, u)
            bez = generate_curve(pts, up, lt, rt)
            max_err, split = get_max_error(pts, bez, up)

            if max_err < err:
                return [bez]
            u = up
    beziers = []
    ct = np_normalize(pts[split-1]-pts[split+1])
    beziers += fit_curve(pts[:split+1], lt, ct, err)
    beziers += fit_curve(pts[split:], -ct, rt, err)

    return beziers

def np_normalize(v):
    mg = math.sqrt(v.dot(v))
    if mg < np.finfo(float).eps:
        return v
    return v / mg