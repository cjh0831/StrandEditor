import os
import bpy
import math
import numpy as np

num = 20
result_path = "E:\\YDNB\\NeuralHDHair\\test_result"      # <------------------- path

for dir in os.listdir(result_path):
    run_dir = os.path.join(result_path, dir)   # <------------------- strand id
    
    hair_file = f"{run_dir}/hair.abc"

    bpy.ops.wm.alembic_import(filepath=hair_file, relative_path=True)
    bpy.data.curves["hair"].bevel_depth = 0.0008
    bpy.data.curves["hair"].materials.append(bpy.data.materials['hair_material'])
    
    output_path = os.path.join(run_dir, "render")
    os.makedirs(output_path, exist_ok=True)

    bpy.data.objects["front_camera"].rotation_euler[0] = math.pi / 2
    bpy.data.objects["sun_light"].rotation_euler[0] = 1.453
    camera_location = np.array([0, -0.41, 1.592])
    light_location = np.array([0, -2, 2])

    for i in range(num):
        
        rotate = 2 * math.pi / num * i
        rotate_mat = np.array([[math.cos(rotate), -math.sin(rotate), 0], [math.sin(rotate), math.cos(rotate), 0], [0, 0, 1]])
        
        bpy.data.objects["front_camera"].location = camera_location.dot(rotate_mat)
        bpy.data.objects["sun_light"].location = light_location.dot(rotate_mat)

        bpy.data.objects["front_camera"].rotation_euler[2] = -rotate
        bpy.data.objects["sun_light"].rotation_euler[2] = -rotate
        
        bpy.ops.render.render()
        bpy.data.images["Render Result"].save_render(f"{output_path}/render1_{i}.png")

    bpy.data.objects["front_camera"].rotation_euler[0] = math.pi / 3
    bpy.data.objects["sun_light"].rotation_euler[0] = 70 / 180 * math.pi
    camera_location = np.array([0, -0.41, 1.85])
    light_location = np.array([0, -2, 2.5])

    for i in range(num):
        
        rotate = 2 * math.pi / num * i
        rotate_mat = np.array([[math.cos(rotate), -math.sin(rotate), 0], [math.sin(rotate), math.cos(rotate), 0], [0, 0, 1]])
        
        bpy.data.objects["front_camera"].location = camera_location.dot(rotate_mat)
        bpy.data.objects["sun_light"].location = light_location.dot(rotate_mat)

        bpy.data.objects["front_camera"].rotation_euler[2] = -rotate
        bpy.data.objects["sun_light"].rotation_euler[2] = -rotate
        
        bpy.ops.render.render()
        bpy.data.images["Render Result"].save_render(f"{output_path}/render2_{i}.png")


    bpy.data.objects.remove(bpy.data.objects["hairOxForm"])
    bpy.data.curves.remove(bpy.data.curves["hair"])
