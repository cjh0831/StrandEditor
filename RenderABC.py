import os
import bpy
import math
import numpy as np
import struct
import array


data_path = "E:\\YDNB\\NeuralHDHair\\mh2usc_hair\\mh2usc_abc_big"      # <------------------- path
output_path = "E:\\YDNB\\NeuralHDHair\\mh2usc_hair\\output"

for file in os.listdir(data_path):
    hairstyle_id = file.split(".")[0]   # <------------------- strand id

    hair_file = f"{data_path}\\{file}"
    object_name = "hair"
    if not os.path.exists(hair_file):
        continue

    bpy.ops.wm.alembic_import(filepath=hair_file, relative_path=True)
    bpy.data.curves[object_name].bevel_depth = 0.0008

    bpy.data.curves[object_name].materials.append(bpy.data.materials['hair_material'])

    bpy.ops.render.render()
    os.makedirs(f"{output_path}/{hairstyle_id}", exist_ok=True)
    bpy.data.images["Render Result"].save_render(f"{output_path}/{hairstyle_id}/render.png")
    
    bpy.data.objects.remove(bpy.data.objects["hairOxForm"])
    bpy.data.curves.remove(bpy.data.curves[object_name])
