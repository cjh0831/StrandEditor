import bpy

head_model = "DB_Bust.obj"
object = bpy.ops.wm.obj_import(filepath=head_model)
materials_data = bpy.data.materials.new(name='head_material')
bpy.data.meshes["DB_Bust"].materials.append(bpy.data.materials['head_material'])

light_data = bpy.data.lights.new(name='sun_light', type='SUN')
light_data.energy = 3
light_object = bpy.data.objects.new(name='sun_light', object_data=light_data)
light_object.location = (0, -2, 2)
light_object.rotation_euler = (1.453, 0, 0)
bpy.context.scene.collection.objects.link(light_object)

camera_data = bpy.data.cameras.new(name='front_camera')
camera_data.type = 'ORTHO'
camera_data.ortho_scale = 0.73
camera_object = bpy.data.objects.new(name="front_camera", object_data=camera_data)
camera_object.location = (-0.0051, -0.41, 1.592)
camera_object.rotation_euler = (1.57, 0, 0)
bpy.context.scene.collection.objects.link(camera_object)
bpy.context.scene.camera = camera_object

bpy.context.scene.render.resolution_x = 1024
bpy.context.scene.render.resolution_y = 1024

materials_data = bpy.data.materials.new(name='hair_material')
materials_data.diffuse_color = [0, 0, 0, 1]
