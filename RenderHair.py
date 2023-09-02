import os
import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector
from mathutils import Euler
import struct
import array

def addStrand(vertices, edges, strand_data_xyz):
    
    # add first vertex of strand
    xyz_idx = 0 
    vec =  Vector((strand_data_xyz[xyz_idx], strand_data_xyz[xyz_idx+1], strand_data_xyz[xyz_idx+2]))
    vertices.append(vec) 
    
    num_verts_to_add = int(len(strand_data_xyz) / 3)
    edge_vidx = len(vertices)
    
    for i in range(1, num_verts_to_add):
        xyz_idx += 3
        vec =  Vector((strand_data_xyz[xyz_idx], strand_data_xyz[xyz_idx+1], strand_data_xyz[xyz_idx+2]))
        vertices.append(vec) 
        
        edges.append((edge_vidx-1, edge_vidx))
        edge_vidx += 1

data_path = "F:/work/hair/Hair/Hair"      # <------------------- path
output_path = "F:/work/hair/output"

for index in range(600):
    hairstyle_id = str(index+1)   # <------------------- strand id

    # -----------------------------------------
    # data of the mesh
    vertices = []  # XYZ coords
    edges = []
    faces = []

    hair_file = f"{data_path}/DB{hairstyle_id}_hair.hair"
    if not os.path.exists(hair_file):
        continue
    print(hair_file)

    fin = open(hair_file, "rb")
    fin.read(4) # skip signature hair

    hair_count = struct.unpack('i', fin.read(4))[0]
    print("hair_count = ", hair_count)
    point_count = struct.unpack('i', fin.read(4))[0]
    print("point_count = ", point_count)
    arrays = struct.unpack('i', fin.read(4))[0]
    print("arrays = ", arrays)
    d_segments = struct.unpack('i', fin.read(4))[0]
    print("d_segments = ", d_segments)
    d_thickness = struct.unpack('f', fin.read(4))[0]
    print("d_thickness = ", d_thickness)
    d_transparency = struct.unpack('f', fin.read(4))[0]
    print("d_transparency = ", d_transparency)
    d_color = struct.unpack('fff', fin.read(4 * 3))
    print("d_color = ", d_color)
    fin.read(88) # skip hair info

    segments = []
    for i in range(hair_count):
        segment = struct.unpack('h', fin.read(2))[0]
        segments.append(segment)

    points = []
    for i in range(point_count):
        point = struct.unpack('fff', fin.read(4 * 3))
        vertices.append(Vector((point[0], point[1], point[2])))

    fin.close()

    point_idx = 0

    left_point = np.array(range(point_count-1))
    right_point = left_point+1
    edges = np.array([left_point, right_point]).T
    no_next = []
    point_idx = 0
    for i in np.array(segments)[:-1]:
        point_idx += i
        no_next.append(point_idx)
        point_idx += 1
    edges = np.delete(edges, no_next, axis=0)
    edges = list(map(tuple, edges))

    print("Data read, creating hair object...")

    object_name = f"hair style {hairstyle_id}"

    # create the mesh
    hair_mesh = bpy.data.meshes.new(object_name)
    hair_mesh.from_pydata(vertices, edges, faces)
    hair_mesh.update()

    # create object from mesh
    hair_object = bpy.data.objects.new(object_name, hair_mesh)
    # get collection
    collection_name = 'USC-HairSalon (imported hair styles)'
    hair_collection = bpy.data.collections.get(collection_name)
    if hair_collection is None:
       hair_collection = bpy.data.collections.new(collection_name)
       bpy.context.scene.collection.children.link(hair_collection)
    # add object to scene collection
    hair_collection.objects.link(hair_object)

    # fix rotation (90° X-axis)
    hair_object.rotation_euler[0] = math.radians(90)
    #select object & apply rotation
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = hair_object
    hair_object.select_set(True)
    bpy.ops.object.transform_apply(rotation=True)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.object.convert(target='CURVE')
    bpy.data.curves[object_name].bevel_depth = 0.0008
    bpy.data.curves[object_name].bevel_resolution = 8
    bpy.data.curves[object_name].materials.append(bpy.data.materials['hair_material'])

    bpy.ops.render.render()
    bpy.data.images["Render Result"].save_render(f"{output_path}/DB100{hairstyle_id}/render.png")
    
    for i in range(10):
        index = "%02d" % (i+1)
        euler_file = f"{output_path}/DB1{index}{hairstyle_id}/euler.txt"
        with open(euler_file, "r") as file:
        
            strs = file.readline().split(" ")
            
            rotation = Euler((math.radians(-float(strs[0])), math.radians(float(strs[2])), math.radians(-float(strs[1]))), 'XYZ')
            bpy.data.objects[object_name].rotation_euler.x -= rotation.x
            bpy.data.objects[object_name].rotation_euler.y -= rotation.y
            bpy.data.objects[object_name].rotation_euler.z -= rotation.z
            bpy.data.objects["DB_Bust"].rotation_euler.x -= rotation.x
            bpy.data.objects["DB_Bust"].rotation_euler.y -= rotation.y
            bpy.data.objects["DB_Bust"].rotation_euler.z -= rotation.z

            bpy.ops.render.render()
            bpy.data.images["Render Result"].save_render(f"{output_path}/DB1{index}{hairstyle_id}/render.png")

            bpy.data.objects[object_name].rotation_euler.x += rotation.x
            bpy.data.objects[object_name].rotation_euler.y += rotation.y
            bpy.data.objects[object_name].rotation_euler.z += rotation.z
            bpy.data.objects["DB_Bust"].rotation_euler.x += rotation.x
            bpy.data.objects["DB_Bust"].rotation_euler.y += rotation.y
            bpy.data.objects["DB_Bust"].rotation_euler.z += rotation.z

    bpy.data.objects.remove(bpy.data.objects[object_name])
    bpy.data.curves.remove(bpy.data.curves[object_name])
    bpy.data.meshes.remove(bpy.data.meshes[object_name])
