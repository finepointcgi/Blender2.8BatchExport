import bpy

bl_info={
"name": "Blender Batch Exporter",
"author": "Mitch McCollum",
"version": (1, 0),
"blender": (2, 80, 0),
"location": "",
"description": "Batch Exports objects to you blend file directory",
"warning": "",
"category": "Mesh"
}

class LayoutPanel(bpy.types.Panel):
    """Creates a Panel in the Sidebar"""
    bl_label = "Batch Exporter"
    bl_idname = "SCENE_PT_Batch_Exporter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BatchExport'
    
    
    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.operator("object.batchexporter", text = 'Batch Export')
        
        
class BatchExporter(bpy.types.Operator):
    bl_idname = "object.batchexporter"
    bl_label = "Invokes Batch Exporter"
    
    def execute(self,context):
        #store selection
        objs = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
               
        for ob in objs:
            
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob
            
            #store object location then zero it out
            location = ob.location.copy()
            bpy.ops.object.location_clear()
            
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
    

def register():
    bpy.utils.register_class(LayoutPanel)
    bpy.utils.register_class(BatchExporter)
        


def unregister():
    bpy.utils.unregister_class(HelloWorldPanel)
    bpy.utils.unregister_class(BatchExport)

if __name__ == "__main__":
    register()