import bpy
import math
import os
import base64

# Configuration
ASSET_NAME = "GeminiPro"
VOXEL_SIZE = 0.012
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()

def get_output_path(filename):
    return os.path.join(OUTPUT_DIR, filename)

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes: bpy.data.meshes.remove(block)
    for block in bpy.data.materials: bpy.data.materials.remove(block)
    for block in bpy.data.textures: bpy.data.textures.remove(block)
    for block in bpy.data.images: bpy.data.images.remove(block)

# --- Materials ---
materials = {}
def create_material(name, color, emission_color=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.8
    if emission_color and emission_strength > 0:
        bsdf.inputs['Emission Color'].default_value = emission_color
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    materials[name] = mat
    return mat

def setup_materials():
    create_material('void_black', (0.02, 0.01, 0.03, 1.0))
    create_material('obsidian_grey', (0.1, 0.1, 0.12, 1.0))
    create_material('starlight_silver', (0.8, 0.8, 0.9, 1.0))
    create_material('astral_purple', (0.3, 0.0, 0.8, 1.0), (0.6, 0.1, 1.0, 1.0), 2.0)
    create_material('astral_cyan', (0.0, 0.8, 1.0, 1.0), (0.0, 0.8, 1.0, 1.0), 2.5)
    create_material('vortex_energy', (0.4, 0.1, 1.0, 1.0), (0.5, 0.2, 1.0, 1.0), 2.2)

# --- Voxel Generation ---
def generate_voxels():
    voxels = {}
    
    def add_voxel(x, y, z, mat):
        voxels[(x, y, z)] = mat

    # Handle (z from 0 to 60)
    for z in range(0, 60):
        for x in range(-1, 2):
            for y in range(-1, 2):
                if (x == 0 and y == 0) or (abs(x) + abs(y) <= 1):
                    add_voxel(x, y, z, 'obsidian_grey' if z % 10 > 2 else 'starlight_silver')

    # Blade Base / Joint (z=55 to 65)
    for z in range(55, 65):
        for x in range(-3, 4):
            for y in range(-2, 3):
                add_voxel(x, y, z, 'void_black')
    
    # Inner glowing core at joint
    for z in range(58, 62):
        for x in range(-1, 2):
            add_voxel(x, 0, z, 'astral_purple')

    # The Scythe Blade (curves forward along y axis)
    # Starts at z=60, y=0, goes up and forward
    for i in range(40):
        z_base = 60 + int(i * 0.8)
        y_base = 2 + int(i * 1.5)
        # Blade thickness
        thickness = max(1, 4 - int(i / 10))
        width = max(1, 3 - int(i / 15))
        
        for dy in range(thickness * 3):
            for dx in range(-width, width + 1):
                y = y_base + dy
                z = z_base - (dy // 3)
                if dy == thickness * 3 - 1:
                    mat = 'astral_cyan' # Cutting edge
                elif dx == 0 and dy % 4 == 0:
                    mat = 'astral_purple' # Runes on blade
                else:
                    mat = 'void_black'
                
                # Assign to group 'scythe_body'
                voxels[(dx, y, z)] = (mat, 'scythe_body')

    # Add Runic Ring 1
    # Horizontal ring around the joint
    r1 = 12
    for angle in range(0, 360, 10):
        rad = math.radians(angle)
        cx = int(r1 * math.cos(rad))
        cy = int(r1 * math.sin(rad))
        cz = 60
        mat = 'astral_cyan' if angle % 30 == 0 else 'astral_purple'
        for dx in (0,1):
            for dy in (0,1):
                voxels[(cx+dx, cy+dy, cz)] = (mat, 'runic_ring_1')
                
    # Add Runic Ring 2 (vertical)
    r2 = 15
    for angle in range(0, 360, 10):
        rad = math.radians(angle)
        cy = int(r2 * math.cos(rad))
        cz = 60 + int(r2 * math.sin(rad))
        cx = 0
        mat = 'astral_cyan' if angle % 40 == 0 else 'astral_purple'
        for dx in (-1,0,1):
            for dy in (0,1):
                voxels[(cx+dx, cy+dy, cz)] = (mat, 'runic_ring_2')

    # Vortex Attack (A large disc, usually hidden, shown during attack)
    # Centered at (0, 30, 60)
    vortex_r = 30
    for r in range(5, vortex_r, 2):
        for angle in range(0, 360, 15):
            rad = math.radians(angle + r*10) # Spiral
            vx = int(r * math.cos(rad))
            vy = 30 + int(r * math.sin(rad))
            vz = 60
            if r % 3 == 0:
                for dz in (-1,0,1):
                    voxels[(vx, vy, vz+dz)] = ('vortex_energy', 'vortex_attack')
                
    # Ensure all voxels have a group (default to scythe_body if not specified)
    final_voxels = {}
    for pos, data in voxels.items():
        if isinstance(data, tuple):
            final_voxels[pos] = data
        else:
            final_voxels[pos] = (data, 'scythe_body')
            
    return final_voxels

def create_voxel_mesh(name, voxels_dict, VOXEL_SIZE=0.012):
    DIRECTIONS = [
        (( 1,  0,  0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
        ((-1,  0,  0), [(0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1)]),
        (( 0,  1,  0), [(1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)]),
        (( 0, -1,  0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
        (( 0,  0,  1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
        (( 0,  0, -1), [(0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)]),
    ]
    
    vertices = []
    polygons = []
    mat_indices = []
    vgroup_indices = []
    
    mat_map = list(materials.keys())
    
    # For quick lookup
    voxel_pos = set(voxels_dict.keys())
    
    vertex_count = 0
    for pos, (mat_name, vgroup) in voxels_dict.items():
        x, y, z = pos
        mat_idx = mat_map.index(mat_name)
        
        for d, corners in DIRECTIONS:
            n_pos = (x + d[0], y + d[1], z + d[2])
            if n_pos not in voxel_pos:
                # Exposed face
                for vx, vy, vz in corners:
                    vertices.append(((x + vx) * VOXEL_SIZE, (y + vy) * VOXEL_SIZE, (z + vz) * VOXEL_SIZE))
                polygons.append([vertex_count, vertex_count + 1, vertex_count + 2, vertex_count + 3])
                mat_indices.append(mat_idx)
                vgroup_indices.append(vgroup)
                vertex_count += 4
                
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], polygons)
    mesh.update()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    for mat_name in mat_map:
        obj.data.materials.append(materials[mat_name])
        
    for poly, mat_idx in zip(obj.data.polygons, mat_indices):
        poly.material_index = mat_idx
        
    # Vertex Groups
    for group_name in set(vgroup_indices):
        obj.vertex_groups.new(name=group_name)
        
    for i, vgroup in enumerate(vgroup_indices):
        # 4 vertices per poly
        obj.vertex_groups[vgroup].add([i*4, i*4+1, i*4+2, i*4+3], 1.0, 'ADD')
        
    # Optimization
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.dissolve_limited(angle_limit=0.0001)
    bpy.ops.mesh.tris_convert_to_quads()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return obj

# --- Rigging & Animation ---
def setup_rig(obj):
    armature_data = bpy.data.armatures.new("ArmatureData")
    armature = bpy.data.objects.new("Armature", armature_data)
    bpy.context.collection.objects.link(armature)
    
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    
    def add_bone(name, head, tail, parent=None):
        bone = armature.data.edit_bones.new(name)
        bone.head = head
        bone.tail = tail
        if parent:
            bone.parent = armature.data.edit_bones[parent]
        return bone

    # Bones
    add_bone('root', (0,0,0), (0,0,0.1))
    add_bone('scythe_body', (0,0,0), (0,0,0.5), 'root')
    
    # Rings around joint
    add_bone('runic_ring_1', (0, 0, 60*VOXEL_SIZE), (0, 0, 60*VOXEL_SIZE + 0.1), 'scythe_body')
    add_bone('runic_ring_2', (0, 0, 60*VOXEL_SIZE), (0, 0, 60*VOXEL_SIZE + 0.1), 'scythe_body')
    
    # Vortex Attack
    add_bone('vortex_attack', (0, 30*VOXEL_SIZE, 60*VOXEL_SIZE), (0, 30*VOXEL_SIZE, 60*VOXEL_SIZE + 0.1), 'scythe_body')
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Bind Mesh to Armature
    obj.parent = armature
    modifier = obj.modifiers.new(type='ARMATURE', name='Armature')
    modifier.object = armature
    
    return armature

def animate_rig(armature):
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    # Create action
    action = bpy.data.actions.new(name="Attack_Vortex")
    armature.animation_data_create()
    armature.animation_data.action = action
    
    def insert_key(bone_name, prop, frame, value):
        pb = armature.pose.bones[bone_name]
        pb.rotation_mode = 'XYZ'
        if prop == 'rotation_euler':
            pb.rotation_euler = value
        elif prop == 'scale':
            pb.scale = value
        elif prop == 'location':
            pb.location = value
        pb.keyframe_insert(data_path=prop, frame=frame)
        
    # Idle & Rings Rotation (Frames 1-60)
    for f in (1, 60):
        insert_key('scythe_body', 'rotation_euler', f, (0, 0, 0))
        
    insert_key('runic_ring_1', 'rotation_euler', 1, (0, 0, 0))
    insert_key('runic_ring_1', 'rotation_euler', 60, (0, 0, math.radians(360)))
    
    insert_key('runic_ring_2', 'rotation_euler', 1, (0, 0, 0))
    insert_key('runic_ring_2', 'rotation_euler', 60, (math.radians(360), 0, 0))
    
    # Hide vortex normally
    insert_key('vortex_attack', 'scale', 1, (0.01, 0.01, 0.01))
    
    # Attack Animation (Frames 60 - 90)
    # Wind up
    insert_key('scythe_body', 'rotation_euler', 65, (math.radians(-30), 0, math.radians(45)))
    insert_key('vortex_attack', 'scale', 65, (0.01, 0.01, 0.01))
    
    # Swing & Vortex expand
    insert_key('scythe_body', 'rotation_euler', 75, (math.radians(90), math.radians(30), math.radians(-180)))
    insert_key('vortex_attack', 'scale', 75, (1.0, 1.0, 1.0))
    insert_key('vortex_attack', 'rotation_euler', 75, (0, 0, math.radians(360)))
    
    # Hold & Spin Vortex
    insert_key('scythe_body', 'rotation_euler', 85, (math.radians(90), math.radians(30), math.radians(-180)))
    insert_key('vortex_attack', 'scale', 85, (1.2, 1.2, 1.2))
    insert_key('vortex_attack', 'rotation_euler', 85, (0, 0, math.radians(720)))
    
    # Recovery
    insert_key('scythe_body', 'rotation_euler', 100, (0, 0, 0))
    insert_key('vortex_attack', 'scale', 100, (0.01, 0.01, 0.01))
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 100
    bpy.context.scene.frame_set(75) # Set to peak attack for render

# --- Render Setup ---
def setup_render(mesh_obj, armature, voxels_dict):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - High Contrast'
    
    # Background opaque dark grey
    scene.render.film_transparent = False
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.01, 0.01, 0.015, 1)
    
    # Lighting
    key_light = bpy.data.lights.new(name="KeyLight", type='AREA')
    key_light.energy = 500
    key_light.size = 2.0
    key_obj = bpy.data.objects.new(name="KeyLight", object_data=key_light)
    bpy.context.collection.objects.link(key_obj)
    
    rim_light = bpy.data.lights.new(name="RimLight", type='AREA')
    rim_light.energy = 800
    rim_light.size = 3.0
    rim_light.color = (0.2, 0.5, 1.0)
    rim_obj = bpy.data.objects.new(name="RimLight", object_data=rim_light)
    bpy.context.collection.objects.link(rim_obj)
    
    # Camera
    cam_data = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    
    # Framing: evaluate depsgraph to get deformed bounding box at current frame
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = mesh_obj.evaluated_get(depsgraph)
    
    verts = [v.co for v in eval_obj.data.vertices]
    if verts:
        matrix = eval_obj.matrix_world
        xs = [(matrix @ v).x for v in verts]
        ys = [(matrix @ v).y for v in verts]
        zs = [(matrix @ v).z for v in verts]
        center = ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, (min(zs) + max(zs)) / 2.0)
        span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 0.5)
    else:
        center = (0, 0, 0)
        span = 1.0

    cam_target = bpy.data.objects.new("CamTarget", None)
    cam_target.location = center
    bpy.context.collection.objects.link(cam_target)
    
    # Position camera
    cam.location = (center[0] + span * 1.5, center[1] - span * 1.5, center[2] + span * 0.75)
    
    track = cam.constraints.new(type='TRACK_TO')
    track.target = cam_target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    # Position lights
    key_obj.location = (center[0] + span, center[1] - span, center[2] + span)
    rim_obj.location = (center[0] - span*1.5, center[1] + span*1.5, center[2] + span*0.5)
    
    for obj in [key_obj, rim_obj]:
        t = obj.constraints.new(type='TRACK_TO')
        t.target = cam_target
        t.track_axis = 'TRACK_NEGATIVE_Z'
        t.up_axis = 'UP_Y'
        
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.filepath = get_output_path(f"{ASSET_NAME}_render.png")

# --- Main Execution ---
def main():
    clear_scene()
    setup_materials()
    voxels = generate_voxels()
    obj = create_voxel_mesh(ASSET_NAME, voxels, VOXEL_SIZE)
    armature = setup_rig(obj)
    animate_rig(armature)
    setup_render(obj, armature, voxels)
    
    # Save Render
    bpy.ops.render.render(write_still=True)
    
    # Save Blend
    bpy.ops.wm.save_as_mainfile(filepath=get_output_path(f"{ASSET_NAME}.blend"))
    
    # Export GLB
    glb_path = get_output_path(f"{ASSET_NAME}.glb")
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_animations=True
    )
    
    # Export JS
    with open(glb_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    with open(get_output_path(f"{ASSET_NAME}_data.js"), "w") as f:
        f.write(f'window.ASSET_NAME_BASE64 = "data:model/gltf-binary;base64,{b64}";\n')

if __name__ == "__main__":
    main()
