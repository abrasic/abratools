import bpy, blf, gpu
from bgl import *
from gpu_extras.batch import batch_for_shader

opacity = 3.0

class AT_Draw:
    def __init__(self, original_x=0, original_y=20):
        self.font_info = {
            "font_id": 0,
            "handler": None,
        }
        self.original_x = original_x
        self.original_y = original_y
        self.str = []
        self.font_info["font_id"] = 0

        self.add_handler()

    def notif_fade_out():
        global opacity #TODO: ew
        if opacity > 0.0:
            opacity += -0.1
        else:
            opacity = 0.0
        return 0.1

    def label(self, string):
        global opacity
        opacity = 3.0
        self.remove_text()
        self.str.append(string)
        self.add_handler()

    def add_handler(self):
        handler = bpy.app.driver_namespace.get('draw_text')
        if not handler:
            handler = bpy.types.SpaceView3D.draw_handler_add(
                self.draw_callback_px, (None, None), 'WINDOW', 'POST_PIXEL')
            dns = bpy.app.driver_namespace
            dns['draw_text'] = handler
            self.redraw_regions()

    def draw_callback_px(self, scene, context):
        
        npanel_width = bpy.context.area.regions[3].width
        width = bpy.context.area.width - npanel_width 
        font_id = self.font_info["font_id"]

        # Init label
        blf.size(font_id, 20, 70)
        blf.color(font_id, 1.0, 1.0, 1.0, opacity)
        blf.position(font_id, ((width/2)-130)+self.original_x, self.original_y-7, 0)
        blf.shadow(font_id, 5, *[0.0, 0.0, 0.0], opacity)
        blf.shadow_offset(font_id, 2, -2)
        blf.enable(font_id, blf.SHADOW)
        
        # Init rect
        glEnable(GL_BLEND)
        
        vertices = (
            (((width/2)-175)+self.original_x, self.original_y+10), (((width/2)-145)+self.original_x,  self.original_y+10),
            (((width/2)-175)+self.original_x, self.original_y-10),(((width/2)-145)+self.original_x, self.original_y-10))

        indices = (
            (0, 1, 2), (2, 1, 3))

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

        for string in self.str:
            
            # Draw rect then label
            shader.uniform_float("color", (1.0, 1.0, 1.0, opacity))
            batch.draw(shader)
            blf.draw(font_id, string)
            
            # Init and draw aT icon
            blf.size(font_id, 20, 60)
            blf.color(font_id, 0.0, 0.0, 0.0, opacity)
            blf.shadow(font_id, 0, *[0.0, 0.0, 0.0], 0.0)
            blf.shadow_offset(font_id, 0, 0)
            blf.position(font_id, ((width/2)-170)+self.original_x, self.original_y-5, 0)
            blf.draw(font_id, "aT")
            glDisable(GL_BLEND)

    def redraw_regions(self):
        for area in bpy.context.window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()

    def remove_text(self):
        handler = bpy.app.driver_namespace.get('draw_text')
        if handler:
            bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
            del bpy.app.driver_namespace['draw_text']
            self.redraw_regions()

            