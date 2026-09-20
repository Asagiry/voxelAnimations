import bpy
import bmesh
import math
import os
import base64
from mathutils import Vector, Euler

# Constants
VOXEL_SIZE = 0.012
TARGET_DIR = r"C:\Users\Voimax\Documents\antigravity\noble-fermi\assets\katana_pro"

# Clear existing data
bpy.ops.wm.read_factory_settings(use_empty=True)

if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)

# --- Materials ---
materials = {}
def create_mat(name, color, emission=None, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        if emission:
            bsdf.inputs['Emission Color'].default_value = emission[0]
            bsdf.inputs['Emission Strength'].default_value = emission[1]
    materials[name] = mat
    return mat

create_mat("BladeSpine", (0.3, 0.3, 0.35, 1.0), metallic=0.9, roughness=0.2)
create_mat("BladeEdge", (0.9, 0.9, 0.95, 1.0), metallic=0.9, roughness=0.1)
create_mat("Habaki", (0.8, 0.6, 0.1, 1.0), metallic=1.0, roughness=0.3)
create_mat("Tsuba", (0.1, 0.1, 0.1, 1.0), metallic=0.8, roughness=0.6)
create_mat("Samegawa", (0.9, 0.9, 0.9, 1.0), roughness=0.9)
create_mat("TsukaIto", (0.05, 0.05, 0.1, 1.0), roughness=0.8)
create_mat("Trail", (0.0, 1.0, 1.0, 1.0), emission=((0.0, 1.0, 1.0, 1.0), 2.0))

# --- Voxel Builder ---
voxels = [] # (x,y,z, mat_name, vgroup)

# Hilt (Tsuka) - 20 voxels long
for z in range(-20, 0):
    mat = "TsukaIto" if z % 2 == 0 else "Samegawa"
    voxels.append((0, 0, z, mat, "Hilt"))
    voxels.append((1, 0, z, mat, "Hilt"))
    voxels.append((-1, 0, z, mat, "Hilt"))

# Guard (Tsuba)
for x in range(-3, 4):
    for y in range(-2, 3):
        if not (abs(x)==3 and abs(y)==2):
            voxels.append((x, y, 0, "Tsuba", "Hilt"))

# Habaki
for z in range(1, 3):
    voxels.append((0, 0, z, "Habaki", "Blade_Bone"))
    voxels.append((1, 0, z, "Habaki", "Blade_Bone"))
    voxels.append((-1, 0, z, "Habaki", "Blade_Bone"))

# Blade - 65 voxels long, with Sori (curve)
for z in range(3, 68):
    y_offset = int((z/68.0)**2 * 6) # simple curve
    
    # Spine
    voxels.append((0, y_offset, z, "BladeSpine", "Blade_Bone"))
    voxels.append((-1, y_offset, z, "BladeSpine", "Blade_Bone"))
    voxels.append((1, y_offset, z, "BladeSpine", "Blade_Bone"))
    
    # Edge
    voxels.append((0, y_offset+1, z, "BladeEdge", "Blade_Bone"))
    if z < 66:
        voxels.append((0, y_offset+2, z, "BladeEdge", "Blade_Bone"))

# Trail
for z in range(10, 60, 2):
    y_offset = int((z/68.0)**2 * 6) + 3
    voxels.append((0, y_offset, z, "Trail", "Trail_Bone"))
    voxels.append((0, y_offset+1, z+1, "Trail", "Trail_Bone"))
    voxels.append((0, y_offset+2, z+2, "Trail", "Trail_Bone"))

# Create Mesh
mesh = bpy.data.meshes.new("KatanaMesh")
obj = bpy.data.objects.new("Katana", mesh)
bpy.context.collection.objects.link(obj)

bm = bmesh.new()

mat_indices = {}
for i, (name, mat) in enumerate(materials.items()):
    mesh.materials.append(mat)
    mat_indices[name] = i

vgroup_data = {"Hilt": [], "Blade_Bone": [], "Trail_Bone": []}

for x, y, z, mat_name, vgroup in voxels:
    vs = []
    r = VOXEL_SIZE / 2
    cx, cy, cz = x * VOXEL_SIZE, y * VOXEL_SIZE, z * VOXEL_SIZE
    
    # 8 vertices of voxel
    verts = [
        bm.verts.new((cx-r, cy-r, cz-r)),
        bm.verts.new((cx+r, cy-r, cz-r)),
        bm.verts.new((cx+r, cy+r, cz-r)),
        bm.verts.new((cx-r, cy+r, cz-r)),
        bm.verts.new((cx-r, cy-r, cz+r)),
        bm.verts.new((cx+r, cy-r, cz+r)),
        bm.verts.new((cx+r, cy+r, cz+r)),
        bm.verts.new((cx-r, cy+r, cz+r)),
    ]
    
    faces = [
        (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
        (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)
    ]
    
    face_start = len(bm.faces)
    for face in faces:
        try:
            f = bm.faces.new([verts[i] for i in face])
            f.material_index = mat_indices[mat_name]
        except ValueError:
            pass # ignore dupes if any
            
    # Record vertex indices for weights
    for v in verts:
        vgroup_data[vgroup].append(v)

bm.verts.index_update()
vgroup_indices = {name: [v.index for v in verts] for name, verts in vgroup_data.items()}

bm.to_mesh(mesh)
bm.free()

for vg_name, indices in vgroup_indices.items():
    vg = obj.vertex_groups.new(name=vg_name)
    vg.add(indices, 1.0, 'REPLACE')
    
# SHADING FLAT
for poly in mesh.polygons:
    poly.use_smooth = False

# --- Armature & Rigging ---
arm_data = bpy.data.armatures.new("Armature")
arm_obj = bpy.data.objects.new("Armature", arm_data)
bpy.context.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')

root = arm_data.edit_bones.new("Root")
root.head = (0, 0, 0)
root.tail = (0, 0.1, 0)

hilt = arm_data.edit_bones.new("Hilt")
hilt.head = (0, 0, -20 * VOXEL_SIZE)
hilt.tail = (0, 0, 0)
hilt.parent = root

blade = arm_data.edit_bones.new("Blade_Bone")
blade.head = (0, 0, 0)
blade.tail = (0, 0, 68 * VOXEL_SIZE)
blade.parent = hilt

trail = arm_data.edit_bones.new("Trail_Bone")
trail.head = (0, 0, 0)
trail.tail = (0, 0.2, 30 * VOXEL_SIZE)
trail.parent = blade

bpy.ops.object.mode_set(mode='OBJECT')

obj.parent = arm_obj
mod = obj.modifiers.new(name="Armature", type='ARMATURE')
mod.object = arm_obj

# --- Animation ---
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 60
bpy.context.scene.render.fps = 30

arm_obj.animation_data_create()
action = bpy.data.actions.new(name="Iaido_Crescent_Slash")
arm_obj.animation_data.action = action

def insert_kf(pb, frame):
    pb.keyframe_insert(data_path="location", frame=frame)
    pb.keyframe_insert(data_path="rotation_euler", frame=frame)
    pb.keyframe_insert(data_path="scale", frame=frame)

pb_root = arm_obj.pose.bones["Root"]
pb_hilt = arm_obj.pose.bones["Hilt"]
pb_blade = arm_obj.pose.bones["Blade_Bone"]
pb_trail = arm_obj.pose.bones["Trail_Bone"]

for pb in [pb_root, pb_hilt, pb_blade, pb_trail]:
    pb.rotation_mode = 'XYZ'

# F1-15: Ready focus stance
pb_root.rotation_euler = (0, 0, 0)
pb_trail.scale = (0, 0, 0)
insert_kf(pb_root, 1)
insert_kf(pb_trail, 1)

pb_root.rotation_euler = (0.2, 0, -0.2)
insert_kf(pb_root, 15)
insert_kf(pb_trail, 15)

# F16-24: Slash
pb_root.rotation_euler = (math.radians(-90), 0, math.radians(45))
pb_trail.scale = (1, 1, 1)
insert_kf(pb_root, 24)
insert_kf(pb_trail, 24)

# F25-36: Climax
pb_root.rotation_euler = (math.radians(-110), 0, math.radians(60))
pb_trail.scale = (0, 0, 0)
insert_kf(pb_root, 36)
insert_kf(pb_trail, 36)

# F37-48: Flick
pb_root.rotation_euler = (math.radians(-90), 0, math.radians(80))
insert_kf(pb_root, 48)

# F49-60: Return
pb_root.rotation_euler = (0, 0, 0)
insert_kf(pb_root, 60)
insert_kf(pb_trail, 60)

# Set rendering frame to 24
bpy.context.scene.frame_set(24)

# --- Render Setup ---
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.view_settings.view_transform = 'AgX'
bpy.context.scene.view_settings.look = 'AgX - High Contrast'

cam_target = bpy.data.objects.new("CamTarget", None)
bpy.context.collection.objects.link(cam_target)
cam_target.location = (0, 0.5, 0)

cam_data = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
cam.location = (1.5, 0.5, 0.8)

# Add TrackTo constraint
track = cam.constraints.new(type='TRACK_TO')
track.target = cam_target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# Lighting (3-point)
light1_data = bpy.data.lights.new(name="Light1", type='AREA')
light1_data.energy = 2000
light1 = bpy.data.objects.new(name="Light1", object_data=light1_data)
bpy.context.collection.objects.link(light1)
light1.location = (2, -1, 2)
light1_track = light1.constraints.new(type='TRACK_TO')
light1_track.target = cam_target
light1_track.track_axis = 'TRACK_NEGATIVE_Z'
light1_track.up_axis = 'UP_Y'

light2_data = bpy.data.lights.new(name="Light2", type='AREA')
light2_data.energy = 1500
light2 = bpy.data.objects.new(name="Light2", object_data=light2_data)
bpy.context.collection.objects.link(light2)
light2.location = (-2, 1, 1)
light2_track = light2.constraints.new(type='TRACK_TO')
light2_track.target = cam_target
light2_track.track_axis = 'TRACK_NEGATIVE_Z'
light2_track.up_axis = 'UP_Y'

light3_data = bpy.data.lights.new(name="Light3", type='AREA')
light3_data.energy = 1500
light3 = bpy.data.objects.new(name="Light3", object_data=light3_data)
bpy.context.collection.objects.link(light3)
light3.location = (0, -2, -1)
light3_track = light3.constraints.new(type='TRACK_TO')
light3_track.target = cam_target
light3_track.track_axis = 'TRACK_NEGATIVE_Z'
light3_track.up_axis = 'UP_Y'

# Render
render_path = os.path.join(TARGET_DIR, "katana_render.png")
bpy.context.scene.render.filepath = render_path
bpy.context.scene.render.resolution_x = 1024
bpy.context.scene.render.resolution_y = 1024
bpy.ops.render.render(write_still=True)

# Export GLB
glb_path = os.path.join(TARGET_DIR, "katana.glb")
bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB', export_animations=True)

# Save Blend
blend_path = os.path.join(TARGET_DIR, "katana.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

# JS Export
with open(glb_path, "rb") as f:
    glb_data = f.read()
b64 = base64.b64encode(glb_data).decode('utf-8')
js_path = os.path.join(TARGET_DIR, "katana_data.js")
with open(js_path, "w") as f:
    f.write(f'window.KATANA_PRO_BASE64 = "{b64}";\n')

print("ALL DONE")
