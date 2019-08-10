bl_info = {
    "name": "Batch Exporter",
    "description": "",
    "author": "Mitch McCollum",
    "version": (0, 0, 2),
    "blender": (2, 80, 0),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}


import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )


# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class MyProperties(PropertyGroup):

    batchRenameBool: BoolProperty(
        name="Batch Rename",
        description="Batch Rename",
        default = False
        )

 

    BulkRename: StringProperty(
        name="Name",
        description=":",
        default="",
        maxlen=1024,      
        )

    my_enum: EnumProperty(
        name="Dropdown:",
        description="Apply Data to attribute.",
        items=[ ('OP1', "Option 1", ""),
                ('OP2', "Option 2", ""),
                ('OP3', "Option 3", ""),
               ]
        )

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class WM_OT_BatchExport(Operator):
    bl_idname = "wm.batch_export"
    bl_label = "Batch Export"

    def execute(self,context):
        #store selection
        objs = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        scene = context.scene
        mytool = scene.my_tool
        
        index = 0
        for ob in objs:
            index += 1
            if mytool.batchRenameBool == True:
                ob.name = mytool.BulkRename + str(index)
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob
            
            #store object location then zero it out
            location = ob.location.copy()
            bpy.ops.object.location_clear()
            bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
            #export fbx
            filename = bpy.path.abspath("//") + ob.name + '.fbx'
            print("Wrote to: " + filename)
            bpy.ops.export_scene.fbx(filepath=filename, use_selection=True)
            
            #restore location
            ob.location = location
          
        #reselect originally selected objects  
        for ob in objs:
            ob.select_set(state=True)
        return { 'FINISHED' }

    

# ------------------------------------------------------------------------
#    Menus
# ------------------------------------------------------------------------

class OBJECT_MT_CustomMenu(bpy.types.Menu):
    bl_idname = "object.custom_menu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

        # Built-in operators
        layout.operator("object.select_all", text="Select/Deselect All").action = 'TOGGLE'
        layout.operator("object.select_all", text="Inverse").action = 'INVERT'
        layout.operator("object.select_random", text="Random")

# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class OBJECT_PT_CustomPanel(Panel):
    bl_idname = "object.custom_panel"
    bl_label = "Batch Exporter"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "BatchExport"
    bl_context = "objectmode"   


    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        layout.prop(mytool, "batchRenameBool")

        layout.prop(mytool, "BulkRename")
        layout.operator("wm.batch_export")
        #layout.menu(OBJECT_MT_CustomMenu.bl_idname, text="Presets", icon="SCENE")
        layout.separator()

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    MyProperties,
    WM_OT_BatchExport,
    OBJECT_MT_CustomMenu,
    OBJECT_PT_CustomPanel
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()