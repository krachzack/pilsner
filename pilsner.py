import json
import bpy
import os
from os.path import expanduser

PLACEMENT_FILE = expanduser('~/out.json')

class PilsnerOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "scene.pilsner"
    bl_label = "Autolayout with pilsner"

    @classmethod
    def poll(cls, context):
        return True

    def __init__(self):
        print("Starting Pilsner")

    def __del__(self):
        print("Stopping Pilsner")

    def invoke(self, context, event):
        self.execute(context)
        return {'OK'}

    def execute(self, context):
        self.clearMeshes()

        # Invoke global lager executable
        placementsJson = os.popen('lager dustsucker').read()
        entities = json.loads(placementsJson)

        for ent in entities:
            for placement in ent['placements']:
                print(placement)

                position = placement['pose']['position'];
                scale = placement['pose']['scale'];
                orientation = placement['pose']['orientation'];

                className = placement['name'];

                parent = self.make_placed_obj_parent(className, position, scale, orientation)

                bpy.ops.import_scene.obj(filepath = placement['model'])

                for placed_obj in bpy.context.selected_objects:
                    placed_obj.parent = parent
                    #bpy.ops.group.objects_add_active(group=className)
                    #placed_obj.name = "Holodrio"
                    #group.objects.link(placed_obj)
                    #placed_obj.delta_scale = [0.1, 0.1, 0.1]

        return {'OK'}

    """
    Creates a parent for the groups in the loaded obj and sets the transformation
    as specified in the JSON
    """
    def make_placed_obj_parent(self, className, position, scale, orientation):
        # Create object with empty mesh
        empty_mesh = bpy.data.meshes.new(className)
        parent = bpy.data.objects.new(className, empty_mesh)

        # And link it with the current scene
        bpy.context.scene.objects.link(parent)

        parent.location = position
        parent.scale = scale
        parent.rotation_euler = orientation

        return parent

    """
    Removes all objects currently in the scene
    See: http://blenderscripting.blogspot.co.at/2012/03/deleting-objects-from-scene.html
    """
    def clearMeshes(self):
        # gather list of items of interest.
        candidate_list = [item.name for item in bpy.data.objects if item.type == "MESH"]

        # select them only.
        for object_name in candidate_list:
            bpy.data.objects[object_name].select = True

        # remove all selected.
        bpy.ops.object.delete()

        # remove the meshes, they have no users anymore.
        for item in bpy.data.meshes:
            bpy.data.meshes.remove(item)


def register():
    bpy.utils.register_class(PilsnerOperator)


def unregister():
    bpy.utils.unregister_class(PilsnerOperator)

if __name__ == "__main__":
    register()
    #bpy.ops.scene.pilsner('INVOKE_DEFAULT')
