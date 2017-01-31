import json
import bpy
import os
from os.path import expanduser

PLACEMENT_FILE = expanduser('~/out.json')

class PilsnerOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "scene.pilsner"
    bl_label = "Load Pils JSON into current scene"
    file_watching_ready = False

    @classmethod
    def poll(cls, context):
        return True

    def __init__(self):
        print("Starting Pilsner")

    def __del__(self):
        print("Stopping Pilsner")

    def invoke(self, context, event):
        self.execute(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        self.last_placement_mtime = os.stat(PLACEMENT_FILE).st_mtime

        self.clearMeshes()

        with open(PLACEMENT_FILE) as json_data:
            entities = json.load(json_data)

            for ent in entities:
                class_name = ent['meta']['id'];
                position = ent['pose']['position'];
                scale = ent['pose']['scale'];
                orientation = ent['pose']['orientation'];

                entity_obj = self.make_placed_obj_parent(class_name, position, scale, orientation)

                for placement in ent['placements']:
                    pl_position = placement['pose']['position']
                    pl_scale = placement['pose']['scale']
                    pl_orientation = placement['pose']['orientation']
                    pl_mesh = placement['mesh']

                    parent = self.make_placed_obj_parent(placement['name'], pl_position, pl_scale, pl_orientation)
                    parent.parent = entity_obj

                    if pl_mesh.endswith(".obj") or pl_mesh.endswith(".OBJ"):
                        bpy.ops.import_scene.obj(filepath = pl_mesh)
                    else:
                        bpy.ops.import_scene.fbx(filepath = pl_mesh)

                    for placed_obj in bpy.context.selected_objects:
                        placed_obj.parent = parent

        return {'RUNNING_MODAL'}

    def execute_if_placements_changed(self, context):
        print("Checking if placement changed")

        new_placement_time = os.stat(PLACEMENT_FILE).st_mtime

        if new_placement_time != self.last_placement_mtime:
            self.last_placement_mtime = new_placement_time
            self.execute(context)

    def modal(self, context, event):
        print(event.type)

        if event.type == 'ESC':
            return {'FINISHED'}
        else:
            self.execute_if_placements_changed(context)
            return {'RUNNING_MODAL'}

    """
    Creates a parent for the groups in the loaded obj and sets the transformation
    as specified in the JSON
    """
    def make_placed_obj_parent(self, class_name, position, scale, orientation):
        position = (position[0], position[2], position[1])
        scale = (scale[0], scale[2], scale[1])

        # Create object with empty mesh
        empty_mesh = bpy.data.meshes.new(class_name)
        parent = bpy.data.objects.new(class_name, empty_mesh)

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

    """
    Sets up unix style signal handling to re-execute the operator when the
    placement file changed. Will probably not work with windows.
    """
    def init_file_watching(self):
        if self.file_watching_ready == False:
            def handler():
                print("Re-running pilsner since placement file changed")
                self()

            self.file_watching_ready = True


def register():
    bpy.utils.register_class(PilsnerOperator)


def unregister():
    bpy.utils.unregister_class(PilsnerOperator)

if __name__ == "__main__":
    register()
    bpy.ops.scene.pilsner('INVOKE_DEFAULT')
