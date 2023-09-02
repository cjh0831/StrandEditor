import os
import bpy
import math
import numpy as np
import struct
import array


data_path = "F:/work/hair/Hair/abc"      # <------------------- path
output_path = "F:/work/hair/output"

for index in range(600):
    hairstyle_id = str(index+1)   # <------------------- strand id

    hair_file = f"{data_path}/DB{hairstyle_id}_hair.abc"
    object_name = "hair"
    if not os.path.exists(hair_file):
        continue

    bpy.ops.wm.alembic_import(filepath=hair_file, relative_path=True)
    bpy.data.curves[object_name].bevel_depth = 0.0008
    bpy.data.curves[object_name].bevel_resolution = 8
    bpy.data.curves[object_name].materials.append(bpy.data.materials['hair_material'])

    bpy.ops.render.render()
    bpy.data.images["Render Result"].save_render(f"{output_path}/DB{hairstyle_id}/render.png")
    
    bpy.data.objects.remove(bpy.data.objects[object_name])
    bpy.data.curves.remove(bpy.data.curves[object_name])
