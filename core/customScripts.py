import bpy, re, os, importlib.util, traceback
from . import api

class ABRA_OT_open_scripts_path(bpy.types.Operator):
    bl_idname = "screen.at_open_scripts_path"
    bl_label = "Open Custom Scripts Path"
    whichpath : bpy.props.StringProperty()

    def execute(self, context):
        os.startfile(os.path.join(os.path.dirname(__file__), os.pardir, "scripts"))

        return {'FINISHED'}

class ABRA_OT_execute_script(bpy.types.Operator):
    bl_idname = "screen.at_exec"
    bl_label = "Run Custom Script"
    bl_description = ""
    bl_options = {"REGISTER"}

    file: bpy.props.StringProperty(
        name="file",
        default = ""
    )

    def execute(self, context):
        api.dprint(f"Executing file {self.file}")

        custom_scripts = os.path.join(os.path.dirname(__file__), os.pardir, "scripts")
        spec = importlib.util.spec_from_file_location("atools_" + os.path.splitext(self.file)[0],custom_scripts + "\\" + self.file)
        modu = importlib.util.module_from_spec(spec)
        
        spec.loader.exec_module(modu) # Accesses file

        area = bpy.context.area
        old_type = area.type
        area.type = modu.script_info.context

        try:
            modu.execute() # Executes code from that file
        except Exception as e:
            self.report({'ERROR'}, "[aT] " + str(e))
            area.type = old_type
            return {"CANCELLED"}
        
        area.type = old_type
        return {"FINISHED"}
    
cls = (ABRA_OT_open_scripts_path,ABRA_OT_execute_script,)