import bpy

head_model = "DB_Bust.obj"
object = bpy.ops.wm.obj_import(filepath=head_model)
materials_data = bpy.data.materials.new(name='head_material')
materials_data.diffuse_color = [0.285, 0.180, 0.090, 1]
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
materials_data.diffuse_color = [0.8, 0.184, 0.014, 1]
bpy.ops.transform.translate(value=(-0.0051, 0, 1.592), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, cursor_transform=True, release_confirm=True)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
