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
        return {'FINISHED'}

    def execute(self, context):
        self.clearMeshes()

        # Invoke global lager executable
        placementsJson = os.popen('lager dustsucker').read()
        entities = json.loads(placementsJson)

        # Create top level pilsner object
        pilsner_obj = self.make_placed_obj_parent("pilsner", [0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [1, 0, 0, 0])
        pilsner_obj.rotation_euler = [-1.5707, 0, 0]

        for ent in entities:
            className = ent['meta']['name'];
            position =  ent['pose']['position'];
            scale =  ent['pose']['scale'];
            orientation =  ent['pose']['orientation'];

            entity_obj = self.make_placed_obj_parent(className, position, scale, orientation)
            entity_obj.parent = pilsner_obj

            for placement in ent['placements']:
                pl_position = placement['pose']['position'];
                pl_scale = placement['pose']['scale'];
                pl_orientation = placement['pose']['orientation'];
                pl_mesh = placement['mesh']
                pl_name = placement['name']

                parent = self.make_placed_obj_parent(pl_name, pl_position, pl_scale, pl_orientation)
                parent.parent = entity_obj

                compensator = self.make_placed_obj_parent("compensator", [0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [1, 0, 0, 0])
                compensator.rotation_euler = [1.5707, 0, 0]
                compensator.parent = parent

                if pl_mesh.endswith(".obj") or pl_mesh.endswith(".OBJ"):
                    bpy.ops.import_scene.obj(filepath = pl_mesh)
                else:
                    bpy.ops.import_scene.fbx(filepath = pl_mesh)

                for placed_obj in bpy.context.selected_objects:
                    placed_obj.parent = compensator

        return {'FINISHED'}

    """
    Creates a parent for the groups in the loaded obj and sets the transformation
    as specified in the JSON
    """
    def make_placed_obj_parent(self, className, position, scale, orientation):
        # Blender has Y and Z flipped compared to OpenGL coordinate system
        position = (position[0], position[1], position[2])
        scale = (scale[0], scale[1], scale[2])

        # Create object with empty mesh
        empty_mesh = bpy.data.meshes.new(className)
        parent = bpy.data.objects.new(className, empty_mesh)

        # And link it with the current scene
        bpy.context.scene.objects.link(parent)

        parent.location = position
        parent.scale = scale
        parent.rotation_quaternion = orientation

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
