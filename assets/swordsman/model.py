import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

VOXEL_SIZE = 0.015  # 1.5 cm per voxel

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def setup_materials():
    materials = {}
    
    mat_configs = {
        'M_Steel': {
            'base_color': (0.70, 0.74, 0.80, 1.0),
            'metallic': 0.88,
            'roughness': 0.22,
            'specular': 0.5
        },
        'M_SteelDark': {
            'base_color': (0.22, 0.25, 0.30, 1.0),
            'metallic': 0.85,
            'roughness': 0.32,
            'specular': 0.5
        },
        'M_GoldAccent': {
            'base_color': (0.96, 0.72, 0.10, 1.0),
            'metallic': 0.92,
            'roughness': 0.18,
            'specular': 0.6
        },
        'M_GambesonNavy': {
            'base_color': (0.03, 0.06, 0.16, 1.0),
            'metallic': 0.0,
            'roughness': 0.85,
            'specular': 0.2
        },
        'M_GambesonTrim': {
            'base_color': (0.10, 0.25, 0.55, 1.0),
            'metallic': 0.0,
            'roughness': 0.75,
            'specular': 0.3
        },
        'M_LeatherBrown': {
            'base_color': (0.14, 0.07, 0.04, 1.0),
            'metallic': 0.02,
            'roughness': 0.75,
            'specular': 0.3
        },
        'M_Skin': {
            'base_color': (0.92, 0.68, 0.52, 1.0),
            'metallic': 0.0,
            'roughness': 0.55,
            'specular': 0.4
        },
        'M_HairBrown': {
            'base_color': (0.12, 0.06, 0.03, 1.0),
            'metallic': 0.0,
            'roughness': 0.70,
            'specular': 0.3
        },
        'M_EyeBlue': {
            'base_color': (0.04, 0.38, 0.95, 1.0),
            'metallic': 0.0,
            'roughness': 0.15,
            'specular': 0.9
        },
        'M_EyeWhite': {
            'base_color': (0.96, 0.96, 0.96, 1.0),
            'metallic': 0.0,
            'roughness': 0.40,
            'specular': 0.5
        },
        'M_CircletGem': {
            'base_color': (0.95, 0.05, 0.15, 1.0),
            'metallic': 0.1,
            'roughness': 0.15,
            'specular': 0.9,
            'emission_color': (0.95, 0.05, 0.15, 1.0),
            'emission_strength': 2.2
        }
    }
    
    for name, cfg in mat_configs.items():
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        output = nodes.new(type='ShaderNodeOutputMaterial')
        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        if 'Base Color' in bsdf.inputs:
            bsdf.inputs['Base Color'].default_value = cfg['base_color']
        if 'Metallic' in bsdf.inputs:
            bsdf.inputs['Metallic'].default_value = cfg.get('metallic', 0.0)
        if 'Roughness' in bsdf.inputs:
            bsdf.inputs['Roughness'].default_value = cfg.get('roughness', 0.5)
            
        spec_input = bsdf.inputs.get('Specular IOR Level') or bsdf.inputs.get('Specular')
        if spec_input:
            spec_input.default_value = cfg.get('specular', 0.5)
            
        if 'emission_color' in cfg:
            em_col = bsdf.inputs.get('Emission Color') or bsdf.inputs.get('Emission')
            if em_col:
                em_col.default_value = cfg['emission_color']
            em_str = bsdf.inputs.get('Emission Strength')
            if em_str:
                em_str.default_value = cfg.get('emission_strength', 1.0)
                
        materials[name] = mat
        
    return materials

def build_voxels_data():
    segments = {}

    def set_voxel(seg_name, x, y, z, mat_name):
        if seg_name not in segments:
            segments[seg_name] = {}
        segments[seg_name][(x, y, z)] = mat_name

    # ----------------------------------------------------
    # 1. PELVIS / HIPS (bone: 'Hips')
    # z: 13 to 15 (height 3). Base: 8x6x3. x in [-4, 3], y in [-3, 2]
    # ----------------------------------------------------
    for x in range(-4, 4):
        for y in range(-3, 3):
            for z in range(13, 16):
                # Default undergarment
                mat = 'M_GambesonNavy'
                # Belt transition at top rim z=15
                if z == 15 and (x in (-4, 3) or y in (-3, 2)):
                    mat = 'M_LeatherBrown'
                # Front fauld armor plate
                if y == 2 and z in (13, 14):
                    mat = 'M_Steel'
                    if x in (-1, 0) and z == 13:
                        mat = 'M_GoldAccent'
                # Side tassets
                if x in (-4, 3) and y in (-2, 1) and z in (13, 14):
                    mat = 'M_Steel'
                set_voxel('Hips', x, y, z, mat)

    # ----------------------------------------------------
    # 2. CHEST & TORSO (bone: 'Chest')
    # z: 17 to 24 (height 8). Base: 8x6x8. x in [-4, 3], y in [-3, 2]
    # ----------------------------------------------------
    for x in range(-4, 4):
        for y in range(-3, 3):
            for z in range(17, 25):
                mat = 'M_GambesonNavy'
                # Leather belt at z=17
                if z == 17:
                    mat = 'M_LeatherBrown'
                # Polished steel breastplate
                if y in (0, 1, 2) and z >= 18:
                    mat = 'M_Steel'
                    # Gold filigree collar trim
                    if z == 24 and y == 2 and x in range(-3, 3):
                        mat = 'M_GoldAccent'
                # Back leather harness straps
                if y == -3 and x in (-1, 0) and 18 <= z <= 23:
                    mat = 'M_LeatherBrown'
                set_voxel('Chest', x, y, z, mat)

    # Belt Buckle (extruded forward +1 voxel at y=3, z=17)
    for x in (-1, 0):
        set_voxel('Chest', x, 3, 17, 'M_GoldAccent')
        # Buckle frame sides
        set_voxel('Chest', x - 1, 3, 17, 'M_GoldAccent')
        set_voxel('Chest', x + 2, 3, 17, 'M_GoldAccent')
    # Extra belt thickness at y=3
    for x in (-3, -2, 1, 2):
        set_voxel('Chest', x, 3, 17, 'M_LeatherBrown')

    # Stepped breastplate ridge (relief +1 voxel forward at y=3, z in [20, 23])
    for z in range(20, 24):
        for x in range(-2, 2):
            mat = 'M_Steel'
            if x in (-1, 0) and z in (21, 22):
                mat = 'M_SteelDark'  # Center ridge shadow
            set_voxel('Chest', x, 3, z, mat)

    # ----------------------------------------------------
    # 3. HEAD, FACE, HAIR & CIRCLET (bone: 'Head')
    # Neck: z=25 (4 voxels: x in [-1, 0], y in [-1, 0])
    # Cranium base: 10x10x10. x in [-5, 4], y in [-5, 4], z in [26, 35]
    # ----------------------------------------------------
    # Neck link
    for x in (-1, 0):
        for y in (-1, 0):
            set_voxel('Head', x, y, 25, 'M_Skin')

    # Base Cranium
    for x in range(-5, 5):
        for y in range(-5, 5):
            for z in range(26, 36):
                # Inner volume
                mat = 'M_HairBrown'
                # Front face skin
                if y == 4 and x in range(-4, 4) and 26 <= z <= 32:
                    mat = 'M_Skin'
                # Side skin near jaw
                if y in (2, 3) and x in (-4, 3) and 26 <= z <= 28:
                    mat = 'M_Skin'
                set_voxel('Head', x, y, z, mat)

    # Face details (y = 4)
    # Mouth smirk
    set_voxel('Head', 0, 4, 27, 'M_LeatherBrown')
    set_voxel('Head', -1, 4, 27, 'M_LeatherBrown')

    # Eyes: sclera white & sapphire iris
    # Left eye: x in (1, 2), z in (29, 30)
    set_voxel('Head', 1, 4, 29, 'M_EyeBlue')
    set_voxel('Head', 2, 4, 29, 'M_EyeWhite')
    set_voxel('Head', 1, 4, 30, 'M_EyeBlue')
    set_voxel('Head', 2, 4, 30, 'M_EyeWhite')

    # Right eye: x in (-3, -2), z in (29, 30)
    set_voxel('Head', -2, 4, 29, 'M_EyeBlue')
    set_voxel('Head', -3, 4, 29, 'M_EyeWhite')
    set_voxel('Head', -2, 4, 30, 'M_EyeBlue')
    set_voxel('Head', -3, 4, 30, 'M_EyeWhite')

    # Eyebrows (extruded +1 voxel at y=5, z=31)
    for x in (0, 1, 2, 3):
        set_voxel('Head', x, 5, 31, 'M_HairBrown')
    for x in (-4, -3, -2, -1):
        set_voxel('Head', x, 5, 31, 'M_HairBrown')

    # Circlet / Headband (stepped +1 voxel relief around head at z=32, 33)
    # Front band at y=5
    for x in range(-5, 5):
        set_voxel('Head', x, 5, 32, 'M_Steel')
        set_voxel('Head', x, 5, 33, 'M_GoldAccent')
    # Sides band at x in (-5, 4), y in [-4, 4]
    for y in range(-4, 5):
        set_voxel('Head', -6, y, 32, 'M_Steel')
        set_voxel('Head', 5, y, 32, 'M_Steel')
    # Rear band at y = -6
    for x in range(-5, 5):
        set_voxel('Head', x, -6, 32, 'M_Steel')
    # Circlet Glowing Gem (centered on forehead: x in (-1, 0), y=5, z=32..33)
    for x in (-1, 0):
        set_voxel('Head', x, 5, 32, 'M_CircletGem')
        set_voxel('Head', x, 5, 33, 'M_CircletGem')

    # Layered 3D Hair volume
    # Bangs over forehead (y=5, z=34, x in range(-4, 4))
    for x in range(-4, 4):
        set_voxel('Head', x, 5, 34, 'M_HairBrown')
    # Falling lock tufts (y=5, z=33)
    for x in (-4, -3, 2, 3):
        set_voxel('Head', x, 5, 33, 'M_HairBrown')

    # Side locks (x in [-6, 5], y in [1, 3], z in [27, 31])
    for z in range(27, 32):
        for y in (1, 2, 3):
            set_voxel('Head', -6, y, z, 'M_HairBrown')
            set_voxel('Head', 5, y, z, 'M_HairBrown')

    # Back hair volume (+1 voxel extrusion at y = -6)
    for z in range(27, 35):
        for x in range(-4, 4):
            set_voxel('Head', x, -6, z, 'M_HairBrown')

    # Top Hair Spikes (z = 36)
    for x in range(-4, 4):
        for y in range(-4, 4):
            set_voxel('Head', x, y, 36, 'M_HairBrown')
    # Swept Anime Spikes (z = 37)
    for pt in [(-3, -1), (-2, 0), (-1, 1), (0, 0), (1, -1), (2, 0), (-2, -2), (1, 1)]:
        set_voxel('Head', pt[0], pt[1], 37, 'M_HairBrown')
    # Crown Spike (z = 38)
    for x in (-1, 0):
        for y in (-1, 0):
            set_voxel('Head', x, y, 38, 'M_HairBrown')

    # ----------------------------------------------------
    # 4. PAULDRONS (bones: 'Shoulder.L' and 'Shoulder.R')
    # 4x5x3 floating steel shoulder guards
    # ----------------------------------------------------
    # Left Pauldron: x in [5, 8], y in [-2, 2], z in [22, 24]
    for x in range(5, 9):
        for y in range(-2, 3):
            for z in range(22, 25):
                mat = 'M_Steel'
                # Gold trim on outer perimeter & top
                if x == 8 or y in (-2, 2) or z == 24:
                    mat = 'M_GoldAccent'
                set_voxel('Shoulder.L', x, y, z, mat)
    # Pauldron crest ridge
    for x in (6, 7):
        for y in (-1, 0, 1):
            set_voxel('Shoulder.L', x, y, 25, 'M_SteelDark')

    # Right Pauldron: x in [-9, -6], y in [-2, 2], z in [22, 24]
    for x in range(-9, -5):
        for y in range(-2, 3):
            for z in range(22, 25):
                mat = 'M_Steel'
                if x == -9 or y in (-2, 2) or z == 24:
                    mat = 'M_GoldAccent'
                set_voxel('Shoulder.R', x, y, z, mat)
    # Pauldron crest ridge
    for x in (-8, -7):
        for y in (-1, 0, 1):
            set_voxel('Shoulder.R', x, y, 25, 'M_SteelDark')

    # ----------------------------------------------------
    # 5. ARMS & FOREARMS (bones: 'UpperArm.L/R', 'Forearm.L/R')
    # ----------------------------------------------------
    # Left UpperArm (z in [18, 21], x in [5, 6], y in [-1, 0])
    for x in (5, 6):
        for y in (-1, 0):
            for z in range(18, 22):
                set_voxel('UpperArm.L', x, y, z, 'M_GambesonNavy')

    # Left Forearm (z in [14, 17], x in [5, 6], y in [-1, 0])
    for x in (5, 6):
        for y in (-1, 0):
            for z in range(14, 18):
                mat = 'M_Steel' if x == 6 else 'M_GambesonNavy'
                if z == 14:
                    mat = 'M_GoldAccent'  # Vambrace cuff
                set_voxel('Forearm.L', x, y, z, mat)

    # Right UpperArm (z in [18, 21], x in [-7, -6], y in [-1, 0])
    for x in (-7, -6):
        for y in (-1, 0):
            for z in range(18, 22):
                set_voxel('UpperArm.R', x, y, z, 'M_GambesonNavy')

    # Right Forearm (z in [14, 17], x in [-7, -6], y in [-1, 0])
    for x in (-7, -6):
        for y in (-1, 0):
            for z in range(14, 18):
                mat = 'M_Steel' if x == -7 else 'M_GambesonNavy'
                if z == 14:
                    mat = 'M_GoldAccent'
                set_voxel('Forearm.R', x, y, z, mat)

    # ----------------------------------------------------
    # 6. HANDS & GAUNTLETS (bones: 'Hand.L', 'Hand.R')
    # Chunky floating gauntlets: 4x4x4 voxels. z in [9, 12], y in [-2, 1]
    # RIGHT HAND: HOLLOW GRASP FIST CAVITY (x in [-7, -6], y in [-1, 0] is open!)
    # NO BAKED WEAPON - COMPLETELY EMPTY HANDS!
    # ----------------------------------------------------
    # RIGHT GAUNTLET (bone: 'Hand.R')
    # x in [-8, -5], y in [-2, 1], z in [9, 12]
    for x in range(-8, -4):
        for y in range(-2, 2):
            for z in range(9, 13):
                # HOLLOW CAVITY CHECK:
                # 2x2 channel through center of fist is empty for weapon handle!
                if x in (-7, -6) and y in (-1, 0):
                    continue  # Keep completely hollow!
                
                # Solid gauntlet armor around the grip channel
                mat = 'M_Steel'
                # Gold knuckle studs on back plate at z=12
                if y == -2 and z == 12:
                    mat = 'M_GoldAccent'
                # Gauntlet wrist border
                if z == 12:
                    mat = 'M_SteelDark'
                set_voxel('Hand.R', x, y, z, mat)

    # LEFT GAUNTLET (bone: 'Hand.L')
    # x in [4, 7], y in [-2, 1], z in [9, 12]
    for x in range(4, 8):
        for y in range(-2, 2):
            for z in range(9, 13):
                # HOLLOW CAVITY CHECK:
                if x in (5, 6) and y in (-1, 0):
                    continue  # Keep completely hollow for shield/offhand handle!
                
                mat = 'M_Steel'
                if y == -2 and z == 12:
                    mat = 'M_GoldAccent'
                if z == 12:
                    mat = 'M_SteelDark'
                set_voxel('Hand.L', x, y, z, mat)

    # ----------------------------------------------------
    # 7. LEGS & FEET (bones: 'UpperLeg.L/R', 'LowerLeg.L/R', 'Foot.L/R')
    # ----------------------------------------------------
    # Upper Legs (z in [9, 11])
    for z in range(9, 12):
        for y in (-1, 0):
            for x in (2, 3):
                set_voxel('UpperLeg.L', x, y, z, 'M_GambesonNavy')
            for x in (-4, -3):
                set_voxel('UpperLeg.R', x, y, z, 'M_GambesonNavy')

    # Lower Legs / Greaves (z in [5, 7])
    for z in range(5, 8):
        for y in (-1, 0):
            for x in (2, 3):
                set_voxel('LowerLeg.L', x, y, z, 'M_Steel')
            for x in (-4, -3):
                set_voxel('LowerLeg.R', x, y, z, 'M_Steel')

    # Boots / Sabatons (z in [0, 3], y in [-2, 3])
    # 4 wide x 6 long x 4 high armored sabatons. Lowest voxel at Z=0!
    # Left Boot: x in [1, 4]
    for x in range(1, 5):
        for y in range(-2, 4):
            for z in range(0, 4):
                mat = 'M_Steel'
                # Leather sole
                if z == 0:
                    mat = 'M_LeatherBrown'
                # Gold toe cap
                elif y == 3 and z in (1, 2):
                    mat = 'M_GoldAccent'
                # Ankle cuff accent
                elif z == 3 and y in (-2, 1):
                    mat = 'M_SteelDark'
                set_voxel('Foot.L', x, y, z, mat)

    # Right Boot: x in [-5, -2]
    for x in range(-5, -1):
        for y in range(-2, 4):
            for z in range(0, 4):
                mat = 'M_Steel'
                if z == 0:
                    mat = 'M_LeatherBrown'
                elif y == 3 and z in (1, 2):
                    mat = 'M_GoldAccent'
                elif z == 3 and y in (-2, 1):
                    mat = 'M_SteelDark'
                set_voxel('Foot.R', x, y, z, mat)

    return segments

MAT_ORDER = [
    'M_Steel', 'M_SteelDark', 'M_GoldAccent',
    'M_GambesonNavy', 'M_GambesonTrim', 'M_LeatherBrown',
    'M_Skin', 'M_HairBrown', 'M_EyeBlue', 'M_EyeWhite', 'M_CircletGem'
]

def generate_mesh_for_segment(seg_name, voxels, materials):
    # Generates a mesh with exposed boundary quads and runs planar dissolve
    mesh = bpy.data.meshes.new(f"Mesh_{seg_name}")
    obj = bpy.data.objects.new(f"Part_{seg_name}", mesh)
    bpy.context.scene.collection.objects.link(obj)

    # Attach ALL materials in the identical MAT_ORDER so slots match across objects
    for mat_name in MAT_ORDER:
        obj.data.materials.append(materials[mat_name])

    # 6 orthogonal face directions and standard vertex offsets
    face_dirs = [
        ((1, 0, 0),  [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
        ((-1, 0, 0), [(0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1)]),
        ((0, 1, 0),  [(1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)]),
        ((0, -1, 0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
        ((0, 0, 1),  [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
        ((0, 0, -1), [(0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])
    ]

    bm = bmesh.new()
    for (vx, vy, vz), mat_name in voxels.items():
        mat_idx = MAT_ORDER.index(mat_name)
        for (dx, dy, dz), vert_offsets in face_dirs:
            neighbor = (vx + dx, vy + dy, vz + dz)
            # Only create face if neighbor is empty
            if neighbor not in voxels:
                face_verts = []
                for ox, oy, oz in vert_offsets:
                    co = Vector(((vx + ox) * VOXEL_SIZE, (vy + oy) * VOXEL_SIZE, (vz + oz) * VOXEL_SIZE))
                    face_verts.append(bm.verts.new(co))
                face = bm.faces.new(face_verts)
                face.material_index = mat_idx

    # Dissolve coplanar faces while preserving sharp edges and material boundaries
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.dissolve_limit(bm, angle_limit=0.001, verts=bm.verts, edges=bm.edges, delimit={'MATERIAL'})

    bm.to_mesh(mesh)
    bm.free()

    # Assign 100% rigid weight to this segment's vertex group
    vg = obj.vertex_groups.new(name=seg_name)
    all_vert_indices = list(range(len(mesh.vertices)))
    if all_vert_indices:
        vg.add(all_vert_indices, 1.0, 'REPLACE')

    return obj

def build_character_armature():
    arm_data = bpy.data.armatures.new("Swordsman_Armature")
    arm_obj = bpy.data.objects.new("Armature", arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = arm_data.edit_bones

    # Bone definitions: (name, parent, head, tail)
    V = VOXEL_SIZE
    bones_info = [
        # Root & Spine chain
        ("Root", None, Vector((0, 0, 0)), Vector((0, 0, 4 * V))),
        ("Hips", "Root", Vector((0, 0, 13 * V)), Vector((0, 0, 16 * V))),
        ("Spine", "Hips", Vector((0, 0, 16 * V)), Vector((0, 0, 17 * V))),
        ("Chest", "Spine", Vector((0, 0, 17 * V)), Vector((0, 0, 25 * V))),
        ("Neck", "Chest", Vector((0, 0, 25 * V)), Vector((0, 0, 26 * V))),
        ("Head", "Neck", Vector((0, 0, 26 * V)), Vector((0, 0, 36 * V))),

        # Sockets on Chest & Head
        ("Socket_Head", "Head", Vector((0, 0, 36 * V)), Vector((0, 0, 39 * V))),
        ("Socket_Back", "Chest", Vector((0, -3 * V, 21 * V)), Vector((0, -6 * V, 21 * V))),

        # Left Arm chain
        ("Shoulder.L", "Chest", Vector((4 * V, 0, 23.5 * V)), Vector((8 * V, 0, 23.5 * V))),
        ("UpperArm.L", "Shoulder.L", Vector((6 * V, 0, 22 * V)), Vector((6 * V, 0, 18 * V))),
        ("Forearm.L", "UpperArm.L", Vector((6 * V, 0, 18 * V)), Vector((6 * V, 0, 14 * V))),
        ("Hand.L", "Forearm.L", Vector((6 * V, 0, 13 * V)), Vector((6 * V, 0, 9 * V))),
        ("Socket_Hand_L", "Hand.L", Vector((5.5 * V, -0.5 * V, 10.5 * V)), Vector((5.5 * V, -0.5 * V, 14.5 * V))),

        # Right Arm chain
        ("Shoulder.R", "Chest", Vector((-4 * V, 0, 23.5 * V)), Vector((-8 * V, 0, 23.5 * V))),
        ("UpperArm.R", "Shoulder.R", Vector((-6 * V, 0, 22 * V)), Vector((-6 * V, 0, 18 * V))),
        ("Forearm.R", "UpperArm.R", Vector((-6 * V, 0, 18 * V)), Vector((-6 * V, 0, 14 * V))),
        ("Hand.R", "Forearm.R", Vector((-6 * V, 0, 13 * V)), Vector((-6 * V, 0, 9 * V))),
        ("Socket_Hand_R", "Hand.R", Vector((-6.5 * V, -0.5 * V, 10.5 * V)), Vector((-6.5 * V, -0.5 * V, 14.5 * V))),

        # Left Leg chain
        ("UpperLeg.L", "Hips", Vector((3 * V, 0, 13 * V)), Vector((3 * V, 0, 9 * V))),
        ("LowerLeg.L", "UpperLeg.L", Vector((3 * V, 0, 8 * V)), Vector((3 * V, 0, 5 * V))),
        ("Foot.L", "LowerLeg.L", Vector((3 * V, 0, 4 * V)), Vector((3 * V, 3 * V, 0))),

        # Right Leg chain
        ("UpperLeg.R", "Hips", Vector((-3 * V, 0, 13 * V)), Vector((-3 * V, 0, 9 * V))),
        ("LowerLeg.R", "UpperLeg.R", Vector((-3 * V, 0, 8 * V)), Vector((-3 * V, 0, 5 * V))),
        ("Foot.R", "LowerLeg.R", Vector((-3 * V, 0, 4 * V)), Vector((-3 * V, 3 * V, 0))),
    ]

    for b_name, b_parent, b_head, b_tail in bones_info:
        eb = edit_bones.new(b_name)
        eb.head = b_head
        eb.tail = b_tail
        if b_parent:
            eb.parent = edit_bones[b_parent]

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

def assemble_swordsman():
    clear_scene()
    materials = setup_materials()
    segments_data = build_voxels_data()

    # Generate each segment object
    part_objects = []
    for seg_name, voxels in segments_data.items():
        part_obj = generate_mesh_for_segment(seg_name, voxels, materials)
        part_objects.append(part_obj)

    # Join all segments into a single unified character mesh
    bpy.ops.object.select_all(action='DESELECT')
    for obj in part_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = part_objects[0]
    bpy.ops.object.join()

    swordsman_mesh_obj = bpy.context.view_layer.objects.active
    swordsman_mesh_obj.name = "Swordsman_Mesh"

    # Enforce flat shading across all voxel polygons
    for poly in swordsman_mesh_obj.data.polygons:
        poly.use_smooth = False

    # Create Armature
    arm_obj = build_character_armature()

    # Parent mesh to armature with Armature modifier
    swordsman_mesh_obj.parent = arm_obj
    mod = swordsman_mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    mod.use_vertex_groups = True

    return arm_obj, swordsman_mesh_obj

def setup_preview_render(output_path):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - High Contrast'

    # Depsgraph evaluated framing
    depsgraph = bpy.context.evaluated_depsgraph_get()
    all_corners = []
    for obj in scene.objects:
        if obj.type == 'MESH' and not obj.hide_render:
            eval_obj = obj.evaluated_get(depsgraph)
            mat = eval_obj.matrix_world
            all_corners.extend([mat @ Vector(corner) for corner in eval_obj.bound_box])

    if all_corners:
        min_co = Vector((min(c.x for c in all_corners), min(c.y for c in all_corners), min(c.z for c in all_corners)))
        max_co = Vector((max(c.x for c in all_corners), max(c.y for c in all_corners), max(c.z for c in all_corners)))
        center = (min_co + max_co) * 0.5
        span = (max_co - min_co).length
    else:
        center = Vector((0, 0, 0.27))
        span = 0.65

    # Camera Target
    target = bpy.data.objects.new("CamTarget", None)
    scene.collection.objects.link(target)
    target.location = center

    # Hero Camera: elevated front-right 3/4 perspective
    # In Trove standards: Character faces +Y, up is +Z. Right hand is at -X.
    # Placing camera at (-X, +Y, +Z) looks directly at front face and right hand hollow fist!
    cam_data = bpy.data.cameras.new("HeroCamera")
    cam_data.lens = 45
    cam_obj = bpy.data.objects.new("HeroCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    fov_rad = cam_data.angle
    dist = (span * 0.5) / math.tan(fov_rad * 0.5) * 1.25
    # Elevated diagonal front-right perspective
    cam_obj.location = center + Vector((-dist * 0.52, dist * 0.72, dist * 0.45))

    tt = cam_obj.constraints.new('TRACK_TO')
    tt.target = target
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'

    # 3-Point Studio Lighting (calibrated for 0.5m miniature biped)
    # 1. Key Light (Warm Hero Light from front-right)
    key_light_data = bpy.data.lights.new(name="KeyLight", type='AREA')
    key_light_data.energy = 16.0
    key_light_data.size = 0.6
    key_light_data.color = (1.0, 0.96, 0.90)
    key_light = bpy.data.objects.new("KeyLight", key_light_data)
    scene.collection.objects.link(key_light)
    key_light.location = center + Vector((-span * 0.8, span * 1.0, span * 0.9))

    # 2. Fill Light (Cool Navy Fill from front-left)
    fill_light_data = bpy.data.lights.new(name="FillLight", type='AREA')
    fill_light_data.energy = 6.0
    fill_light_data.size = 0.8
    fill_light_data.color = (0.75, 0.85, 1.0)
    fill_light = bpy.data.objects.new("FillLight", fill_light_data)
    scene.collection.objects.link(fill_light)
    fill_light.location = center + Vector((span * 1.0, span * 0.8, span * 0.4))

    # 3. Rim / Hair Light (Sharp Back Rim highlighting hair & shoulders)
    rim_light_data = bpy.data.lights.new(name="RimLight", type='AREA')
    rim_light_data.energy = 14.0
    rim_light_data.size = 0.5
    rim_light_data.color = (0.92, 0.96, 1.0)
    rim_light = bpy.data.objects.new("RimLight", rim_light_data)
    scene.collection.objects.link(rim_light)
    rim_light.location = center + Vector((0.0, -span * 1.1, span * 0.8))

    # Dark studio background
    world = bpy.data.worlds.new("StudioWorld")
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.025, 0.025, 0.035, 1.0)
        bg_node.inputs['Strength'].default_value = 0.3
    scene.world = world

    # Render image
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    blend_path = os.path.join(base_dir, "swordsman.blend")
    preview_path = os.path.join(base_dir, "model_preview.png")

    print(f"--- Building Swordsman Base Class in {base_dir} ---")
    arm_obj, mesh_obj = assemble_swordsman()

    # Save Blend file
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Successfully saved blend file to: {blend_path}")

    # Setup preview camera & render
    setup_preview_render(preview_path)
    print(f"Successfully rendered preview to: {preview_path}")

if __name__ == "__main__":
    main()
