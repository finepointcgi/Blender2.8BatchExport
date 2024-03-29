bl_info = {
    "name": "Batch Exporter",
    "description": "",
    "author": "Mitch McCollum",
    "version": (1, 8, 17),
    "blender": (2, 80, 0),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}


import bpy
import os
import platform
import subprocess

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

class Utilities():
    FilePath = ""
    
    def make_path_absolute(self,key): 
    #""" Prevent Blender's relative paths of doom """ 
    # This can be a collection property or addon preferences 
        props = bpy.context.scene.my_tool
        sane_path = lambda p: os.path.abspath(bpy.path.abspath(p)) 
        
        if key in props and props[key].startswith('//'): 
            props[key] = sane_path(props[key]) 

u = Utilities()

class MyProperties(PropertyGroup):

    
    batchRenameBool: BoolProperty(
        name="Batch Rename",
        description="Batch Rename",
        default = False
        )
        

        
    batchApplyBool: BoolProperty(
        name="Apply Transform",
        description="Apply Position",
        default = False
        )
 

    BulkRename: StringProperty(
        name="Name",
        description=":",
        default="",
        maxlen=1024,      
        )
    FilePath: StringProperty(
        name="File Path",
        description=":",
        default="",
        maxlen=1024,
        subtype='DIR_PATH',
        update = lambda s,c: u.make_path_absolute('FilePath'),
    )
    
    my_enum: EnumProperty(
        name="FileType:",
        description="What File Format",
        items=[ ('F', "FBX", ""),
                ('O', "OBJ", ""),
               ]
        )
    Engine: EnumProperty(
        name="Engine",
        description="What Engine",
        items=[ ('None', "None", ""),
                ('Unity', "Unity", ""),
                ('Unreal', "Unreal", ""),
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
        global Filepath
        
        index = 0
        for ob in objs:
            index += 1
            if mytool.batchRenameBool == True:
                ob.name = mytool.BulkRename + str(index)
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob
            
            #store object location then zero it out
            
            location = ob.location.copy()
            if mytool.batchApplyBool == True:
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            if mytool.Engine == "Unity":
                FixRotationForUnity3D()
                    
            bpy.ops.object.location_clear()
            bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
            #export fbx
            if mytool.FilePath != "":
                if mytool.my_enum == "F":
                    u.FilePath = mytool.FilePath + ob.name + '.fbx'
                else:
                    u.FilePath = mytool.FilePath + ob.name + '.obj'
            else:
                if mytool.my_enum == "F":
                    u.FilePath = bpy.path.abspath("//") + ob.name + '.fbx'
                else:
                    u.FilePath = mytool.FilePath + ob.name + '.obj'
                    
            print("Wrote to: " + u.FilePath)
            if mytool.my_enum == 'F':
                if mytool.Engine == "Unreal":
                    bpy.ops.export_scene.fbx(filepath=u.FilePath, use_selection=True, global_scale = 100)
                bpy.ops.export_scene.fbx(filepath=u.FilePath, use_selection=True)
            else:
                bpy.ops.export_scene.obj(filepath=u.FilePath, use_selection=True)
            
            #restore location
            ob.location = location
        ##FBX  
        #reselect originally selected objects  
        for ob in objs:
            ob.select_set(state=True)
        return { 'FINISHED' }
    

    
    def FixRotationForUnity3D(self):
        bpy.ops.object.transform_apply(rotation = True)

        bpy.ops.transform.rotate(value = -1.5708, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
        bpy.ops.transform.rotate(value = -3.1416, axis = (0, 1, 0), constraint_axis = (False, True, False), constraint_orientation = 'GLOBAL')

        bpy.ops.object.transform_apply(rotation = True)

        bpy.ops.transform.rotate(value = 1.5708, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
        bpy.ops.transform.rotate(value = 3.1416, axis = (0, 0, 1), constraint_axis = (False, False, True), constraint_orientation = 'GLOBAL')
    
   

class WM_OT_OpenFileLocation(Operator):
    bl_idname = "wm.open_file_location"
    bl_label = "Open File Location"

    def execute(self,context):
        global Filepath
        if u.FilePath == "":
            u.FilePath = bpy.path.abspath("//")
            
        if platform.system() == "Windows":
            os.startfile(u.FilePath)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", FilePath])
        else:
            subprocess.Popen(["xdg-open", FilePath])
        
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
        layout.label(text="Batch Rename:")
        layout.prop(mytool, "batchRenameBool")
        layout.prop(mytool, "BulkRename")
        
        layout.label(text=" ")
        layout.label(text="Export Options:")
        layout.prop(mytool, "batchApplyBool")
        layout.prop(mytool, "Engine")
        
        layout.label(text=" ")        
        layout.label(text="Export Location:")
        layout.prop(mytool, "FilePath")
        layout.prop(mytool, "my_enum")
        layout.operator("wm.batch_export")
        layout.operator("wm.open_file_location")
        #layout.menu(OBJECT_MT_CustomMenu.bl_idname, text="Presets", icon="SCENE")
        layout.separator()

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    MyProperties,
    WM_OT_BatchExport,
    OBJECT_MT_CustomMenu,
    OBJECT_PT_CustomPanel,
    WM_OT_OpenFileLocation
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