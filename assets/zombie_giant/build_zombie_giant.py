"""
Deterministic Procedural Builder for Zombie Giant / Fat Abomination
Authentic Trove / Cube World / Astra 6 Micro-Voxel Aesthetic
Author: Trove Voxel Artisan & Technical Animator
"""

import bpy
import bmesh
import math
import os
import base64
from mathutils import Vector, Matrix, Euler

VOXEL_SIZE = 0.015  # 1.5 cm per voxel

def reset_scene():
    """Clear scene objects and orphan data."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Ensure a collection exists
    if not bpy.data.collections:
        col = bpy.data.collections.new("Collection")
        bpy.context.scene.collection.children.link(col)

def create_materials():
    """Create authentic retro stylized micro-voxel materials with AgX tonemapping safeguards."""
    materials = {}
    
    mat_specs = {
        'M_BileFlesh': {
            'base_color': (0.25, 0.32, 0.17, 1.0),
            'roughness': 0.55,
            'metallic': 0.0,
            'specular': 0.3,
        },
        'M_RotDark': {
            'base_color': (0.10, 0.13, 0.08, 1.0),
            'roughness': 0.70,
            'metallic': 0.0,
            'specular': 0.2,
        },
        'M_PutridFat': {
            'base_color': (0.36, 0.35, 0.18, 1.0),
            'roughness': 0.45,
            'metallic': 0.0,
            'specular': 0.4,
        },
        'M_Viscera': {
            'base_color': (0.18, 0.02, 0.03, 1.0),
            'roughness': 0.30,
            'metallic': 0.05,
            'specular': 0.5,
        },
        'M_BloodFresh': {
            'base_color': (0.42, 0.015, 0.02, 1.0),
            'roughness': 0.18,
            'metallic': 0.10,
            'specular': 0.6,
        },
        'M_BloodDark': {
            'base_color': (0.12, 0.012, 0.015, 1.0),
            'roughness': 0.65,
            'metallic': 0.05,
            'specular': 0.3,
        },
        'M_Bone': {
            'base_color': (0.62, 0.58, 0.46, 1.0),
            'roughness': 0.50,
            'metallic': 0.0,
            'specular': 0.35,
        },
        'M_BoneHighlight': {
            'base_color': (0.78, 0.74, 0.62, 1.0),
            'roughness': 0.40,
            'metallic': 0.0,
            'specular': 0.45,
        },
        'M_IronStaples': {
            'base_color': (0.14, 0.14, 0.13, 1.0),
            'roughness': 0.35,
            'metallic': 0.85,
            'specular': 0.5,
        },
        'M_Rust': {
            'base_color': (0.32, 0.14, 0.07, 1.0),
            'roughness': 0.80,
            'metallic': 0.20,
            'specular': 0.2,
        },
        'M_EyeGlow': {
            'base_color': (0.95, 0.15, 0.02, 1.0),
            'roughness': 0.20,
            'metallic': 0.0,
            'specular': 0.5,
            'emission_color': (0.95, 0.15, 0.02, 1.0),
            'emission_strength': 2.2,  # AgX safe saturated crimson/amber
        },
        'M_EyeDecayed': {
            'base_color': (0.18, 0.20, 0.12, 1.0),
            'roughness': 0.80,
            'metallic': 0.0,
            'specular': 0.1,
        },
        'M_SlamShockwave': {
            'base_color': (0.40, 0.35, 0.28, 1.0),
            'roughness': 0.85,
            'metallic': 0.0,
            'specular': 0.2,
        }
    }
    
    for name, spec in mat_specs.items():
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            # Base Color
            bsdf.inputs["Base Color"].default_value = spec['base_color']
            # Roughness
            if "Roughness" in bsdf.inputs:
                bsdf.inputs["Roughness"].default_value = spec['roughness']
            # Metallic
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = spec['metallic']
            # Specular
            spec_socket = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
            if spec_socket:
                spec_socket.default_value = spec['specular']
            # Emission
            if 'emission_color' in spec:
                em_col = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
                if em_col:
                    em_col.default_value = spec['emission_color']
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = spec['emission_strength']
        materials[name] = mat
        
    return materials

def add_box(vox_dict, x0, x1, y0, y1, z0, z1, mat_name, bone_name):
    """Fill an axis-aligned box with voxels [x0, x1], [y0, y1], [z0, z1] inclusive."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                vox_dict[(x, y, z)] = (mat_name, bone_name)

def build_abomination_voxels():
    """Build all voxel coordinates, assigning material and bone names."""
    vox = {}
    
    # -------------------------------------------------------------
    # 1. FEET / BOOTS (Detached with 1-voxel gap above at Z=5)
    # -------------------------------------------------------------
    # Left Boot (X centered at +5: X in [2, 7], Y in [-4, 4], Z in [0, 4])
    add_box(vox, 2, 7, -4, 4, 0, 4, 'M_RotDark', 'Foot.L')
    # Sole iron plating
    add_box(vox, 2, 7, -4, 4, 0, 0, 'M_IronStaples', 'Foot.L')
    # Toe cap reinforced with iron
    add_box(vox, 2, 7, 3, 4, 0, 2, 'M_IronStaples', 'Foot.L')
    # Toe spikes
    vox[(3, 5, 1)] = ('M_IronStaples', 'Foot.L')
    vox[(6, 5, 1)] = ('M_IronStaples', 'Foot.L')
    # Ankle wrap
    add_box(vox, 2, 7, -4, 4, 4, 4, 'M_Rust', 'Foot.L')
    
    # Right Boot (X centered at -5: X in [-7, -2], Y in [-4, 4], Z in [0, 4])
    add_box(vox, -7, -2, -4, 4, 0, 4, 'M_RotDark', 'Foot.R')
    add_box(vox, -7, -2, -4, 4, 0, 0, 'M_IronStaples', 'Foot.R')
    add_box(vox, -7, -2, 3, 4, 0, 2, 'M_IronStaples', 'Foot.R')
    vox[(-6, 5, 1)] = ('M_IronStaples', 'Foot.R')
    vox[(-3, 5, 1)] = ('M_IronStaples', 'Foot.R')
    add_box(vox, -7, -2, -4, 4, 4, 4, 'M_Rust', 'Foot.R')
    # Fresh bloodstains on right boot toe
    vox[(-5, 4, 2)] = ('M_BloodFresh', 'Foot.R')
    vox[(-4, 4, 1)] = ('M_BloodFresh', 'Foot.R')
    vox[(-5, 5, 1)] = ('M_BloodDark', 'Foot.R')
    
    # -------------------------------------------------------------
    # 2. LOWER LEGS (Z in [6, 11], 1v gap from boots at Z=5)
    # -------------------------------------------------------------
    # Left Lower Leg (X in [3, 7], Y in [-2, 2])
    add_box(vox, 3, 7, -2, 2, 6, 11, 'M_BileFlesh', 'LowerLeg.L')
    # Dark rot creases
    add_box(vox, 3, 7, -2, -2, 6, 11, 'M_RotDark', 'LowerLeg.L')
    # Shin bone spur protruding forward
    vox[(5, 3, 9)] = ('M_Bone', 'LowerLeg.L')
    vox[(5, 3, 8)] = ('M_BoneHighlight', 'LowerLeg.L')
    
    # Right Lower Leg (X in [-7, -3], Y in [-2, 2])
    add_box(vox, -7, -3, -2, 2, 6, 11, 'M_BileFlesh', 'LowerLeg.R')
    add_box(vox, -7, -3, -2, -2, 6, 11, 'M_RotDark', 'LowerLeg.R')
    # Exposed cracked bone on lateral right side
    vox[(-7, 0, 8)] = ('M_Bone', 'LowerLeg.R')
    vox[(-7, 0, 9)] = ('M_Bone', 'LowerLeg.R')
    vox[(-7, 0, 10)] = ('M_BoneHighlight', 'LowerLeg.R')
    vox[(-7, 1, 9)] = ('M_BloodDark', 'LowerLeg.R')
    
    # -------------------------------------------------------------
    # 3. UPPER LEGS / THIGHS (Z in [12, 17])
    # -------------------------------------------------------------
    # Left Thigh
    add_box(vox, 3, 7, -2, 2, 12, 17, 'M_BileFlesh', 'UpperLeg.L')
    add_box(vox, 2, 7, 1, 3, 13, 16, 'M_PutridFat', 'UpperLeg.L')  # Bulging quad fat
    
    # Right Thigh
    add_box(vox, -7, -3, -2, 2, 12, 17, 'M_BileFlesh', 'UpperLeg.R')
    add_box(vox, -7, -2, 1, 3, 13, 16, 'M_PutridFat', 'UpperLeg.R')
    # Autopsy staple on right thigh
    vox[(-5, 4, 15)] = ('M_IronStaples', 'UpperLeg.R')
    vox[(-4, 4, 15)] = ('M_IronStaples', 'UpperLeg.R')
    
    # -------------------------------------------------------------
    # 4. PELVIS & LOINCLOTH (Z in [18, 22], Bone: Hips)
    # -------------------------------------------------------------
    add_box(vox, -7, 7, -4, 2, 18, 22, 'M_RotDark', 'Hips')
    add_box(vox, -6, 6, -3, 1, 18, 22, 'M_BileFlesh', 'Hips')
    # Tattered loincloth hanging down in front
    add_box(vox, -4, 4, 3, 3, 15, 19, 'M_RotDark', 'Hips')
    add_box(vox, -3, 3, 3, 3, 14, 16, 'M_Rust', 'Hips')
    # Crude iron chain belt with buckle
    for x in range(-8, 9):
        vox[(x, 3, 20)] = ('M_IronStaples', 'Hips')
        vox[(x, -5, 20)] = ('M_IronStaples', 'Hips')
    for y in range(-4, 3):
        vox[(-8, y, 20)] = ('M_IronStaples', 'Hips')
        vox[(8, y, 20)] = ('M_IronStaples', 'Hips')
    # Heavy iron buckle
    add_box(vox, -1, 1, 4, 4, 19, 21, 'M_IronStaples', 'Hips')
    vox[(0, 4, 20)] = ('M_Rust', 'Hips')
    
    # -------------------------------------------------------------
    # 5. MASSIVE BLOATED GUT / BELLY (Z in [21, 33], Bone: Belly)
    # -------------------------------------------------------------
    # Stepped ellipsoidal dome bulging massively forward into +Y
    for x in range(-8, 9):
        for y in range(0, 11):
            for z in range(21, 34):
                # Normalized ellipsoid equation
                nx = x / 7.5
                ny = (y - 4.5) / 5.5
                nz = (z - 27.0) / 6.0
                dist_sq = nx * nx + ny * ny + nz * nz
                if dist_sq <= 1.05 and y >= 0:
                    mat = 'M_PutridFat' if y >= 4 else 'M_BileFlesh'
                    # Bottom crease in dark rot
                    if z <= 22 or y <= 1:
                        mat = 'M_RotDark'
                    vox[(x, y, z)] = (mat, 'Belly')
                    
    # Crude Autopsy Suture Incision (diagonal scar from (-5, y, 24) to (4, y, 31))
    suture_points = [
        (-5, 24), (-4, 25), (-3, 26), (-2, 27),
        (-1, 28), (0, 29), (1, 30), (2, 31), (3, 32), (4, 32)
    ]
    for sx, sz in suture_points:
        # Find outer front Y for this (sx, sz)
        front_y = max(y for (x, y, z) in vox.keys() if x == sx and z == sz and vox[(x, y, z)][1] == 'Belly')
        # Dark incision line
        vox[(sx, front_y, sz)] = ('M_BloodDark', 'Belly')
        # Staples crossing the cut every other step
        if (sx + sz) % 2 == 0:
            vox[(sx, front_y + 1, sz)] = ('M_IronStaples', 'Belly')
            vox[(sx - 1, front_y, sz)] = ('M_IronStaples', 'Belly')
            vox[(sx + 1, front_y, sz)] = ('M_IronStaples', 'Belly')
            
    # Visceral Gaping Tear / Ulcer (X in [-3, -1], Z in [25, 27])
    for tx in range(-3, 0):
        for tz in range(25, 28):
            front_y = max(y for (x, y, z) in vox.keys() if x == tx and z == tz and vox[(x, y, z)][1] == 'Belly')
            vox[(tx, front_y, tz)] = ('M_Viscera', 'Belly')
            vox[(tx, front_y - 1, tz)] = ('M_BloodDark', 'Belly')
            
    # Arterial blood dripping down from the visceral tear
    for dz in [24, 23, 22]:
        front_y = max(y for (x, y, z) in vox.keys() if x == -2 and z == dz and vox[(x, y, z)][1] == 'Belly')
        vox[(-2, front_y, dz)] = ('M_BloodFresh', 'Belly')
        vox[(-1, front_y, dz)] = ('M_BloodDark', 'Belly')
        
    # -------------------------------------------------------------
    # 6. CHEST & HUMPED UPPER BACK (Z in [27, 38], Bone: Chest)
    # -------------------------------------------------------------
    # Spine & Upper Torso Core
    add_box(vox, -8, 8, -5, 2, 27, 37, 'M_BileFlesh', 'Chest')
    add_box(vox, -7, 7, -4, 1, 27, 37, 'M_RotDark', 'Chest')
    # Exposed vertebrae down center of spine
    for sz in range(26, 35):
        vox[(0, -6, sz)] = ('M_Bone', 'Chest')
        vox[(0, -5, sz)] = ('M_BoneHighlight', 'Chest')
        
    # Massive Trapezius Humpback (Y in [-7, -2], Z in [35, 43])
    add_box(vox, -8, 8, -7, -2, 35, 41, 'M_RotDark', 'Chest')
    add_box(vox, -7, 7, -6, -2, 36, 42, 'M_BileFlesh', 'Chest')
    
    # Left Shoulder Hump details: Broken ribs jutting out from rotting back
    vox[(5, -7, 38)] = ('M_Bone', 'Chest')
    vox[(5, -7, 39)] = ('M_BoneHighlight', 'Chest')
    vox[(5, -8, 40)] = ('M_BoneHighlight', 'Chest')
    vox[(7, -6, 39)] = ('M_Bone', 'Chest')
    vox[(7, -7, 40)] = ('M_BoneHighlight', 'Chest')
    vox[(7, -7, 41)] = ('M_BoneHighlight', 'Chest')
    # Blood at rib bases
    vox[(5, -6, 38)] = ('M_BloodDark', 'Chest')
    vox[(7, -5, 39)] = ('M_BloodFresh', 'Chest')
    
    # Right Shoulder Hump details: Bolted rusted iron armor plate
    add_box(vox, -8, -4, -7, -3, 37, 42, 'M_IronStaples', 'Chest')
    vox[(-6, -7, 39)] = ('M_Rust', 'Chest')
    vox[(-5, -7, 41)] = ('M_Rust', 'Chest')
    vox[(-7, -7, 38)] = ('M_IronStaples', 'Chest')
    
    # -------------------------------------------------------------
    # 7. SUNKEN HUNCHBACK HEAD & UNDERBITE JAW (Bone: Head & Jaw)
    # -------------------------------------------------------------
    # Skull base sunken between trapezius humps: X in [-5, 5], Y in [-2, 6], Z in [36, 44]
    add_box(vox, -5, 5, -2, 5, 37, 44, 'M_BileFlesh', 'Head')
    
    # Asymmetry: Left side bloated flesh, Right side exposed skull bone
    add_box(vox, -5, -2, 1, 6, 38, 43, 'M_Bone', 'Head')  # Exposed bone right temple/cheek
    
    # Eyes:
    # Left Eye: Swollen shut necrotic orbital socket
    vox[(3, 6, 40)] = ('M_EyeDecayed', 'Head')
    vox[(3, 6, 41)] = ('M_EyeDecayed', 'Head')
    vox[(2, 6, 40)] = ('M_RotDark', 'Head')
    vox[(4, 6, 41)] = ('M_PutridFat', 'Head')
    
    # Right Eye: Glowing bloodlust crimson socket
    vox[(-3, 6, 41)] = ('M_EyeGlow', 'Head')
    vox[(-3, 5, 41)] = ('M_BloodDark', 'Head')  # Deep dark socket rim
    vox[(-4, 6, 41)] = ('M_Bone', 'Head')
    vox[(-2, 6, 41)] = ('M_Bone', 'Head')
    
    # Cranial Iron Suture Plate bolted on skull top
    add_box(vox, -2, 2, 0, 4, 45, 45, 'M_IronStaples', 'Head')
    vox[(0, 2, 45)] = ('M_Rust', 'Head')
    vox[(-2, 1, 45)] = ('M_IronStaples', 'Head')
    vox[(2, 3, 45)] = ('M_IronStaples', 'Head')
    
    # Mouth Interior (dark void)
    add_box(vox, -3, 3, 3, 5, 37, 38, 'M_BloodDark', 'Head')
    
    # Underbite Jaw (Bone: Jaw, hinged under skull: X in [-4, 4], Y in [0, 7], Z in [34, 37])
    add_box(vox, -4, 4, 0, 7, 34, 36, 'M_RotDark', 'Jaw')
    add_box(vox, -3, 3, 2, 7, 35, 36, 'M_BileFlesh', 'Jaw')
    # Giant upward crooked bone tusks
    # Left massive tusk
    vox[(3, 7, 37)] = ('M_Bone', 'Jaw')
    vox[(3, 7, 38)] = ('M_BoneHighlight', 'Jaw')
    vox[(3, 7, 39)] = ('M_BoneHighlight', 'Jaw')
    vox[(3, 6, 40)] = ('M_BoneHighlight', 'Jaw')
    # Right massive tusk
    vox[(-3, 7, 37)] = ('M_Bone', 'Jaw')
    vox[(-3, 7, 38)] = ('M_BoneHighlight', 'Jaw')
    vox[(-3, 7, 39)] = ('M_BoneHighlight', 'Jaw')
    vox[(-3, 6, 40)] = ('M_BoneHighlight', 'Jaw')
    vox[(-3, 6, 41)] = ('M_BoneHighlight', 'Jaw')
    # Intermediate jagged teeth
    for tx in [-1, 0, 1]:
        vox[(tx, 7, 37)] = ('M_BoneHighlight', 'Jaw')
        
    # -------------------------------------------------------------
    # 8. LEFT ARM: BLOATED SLAB & OVERSIZED CRUSHING FIST
    # -------------------------------------------------------------
    # Floating Pauldron (Bone: Shoulder.L, 1v gap from torso at X=9)
    add_box(vox, 9, 14, -3, 3, 35, 40, 'M_BileFlesh', 'Shoulder.L')
    add_box(vox, 10, 14, -2, 2, 36, 40, 'M_PutridFat', 'Shoulder.L')
    # Pauldron bone crest
    for pz in range(37, 41):
        vox[(12, 0, pz)] = ('M_Bone', 'Shoulder.L')
        
    # Left Upper Arm (Bone: UpperArm.L, 1v gap at Z=34)
    add_box(vox, 10, 14, -2, 2, 27, 33, 'M_BileFlesh', 'UpperArm.L')
    add_box(vox, 10, 14, 1, 2, 28, 32, 'M_PutridFat', 'UpperArm.L')
    
    # Left Forearm (Bone: Forearm.L, 1v gap at Z=26, swollen 6x6)
    add_box(vox, 10, 15, -2, 3, 18, 25, 'M_BileFlesh', 'Forearm.L')
    add_box(vox, 10, 15, 2, 3, 19, 24, 'M_PutridFat', 'Forearm.L')
    # Swollen dark rot veins
    vox[(15, 0, 21)] = ('M_RotDark', 'Forearm.L')
    vox[(15, 1, 22)] = ('M_RotDark', 'Forearm.L')
    vox[(15, 0, 23)] = ('M_RotDark', 'Forearm.L')
    # Rusted iron shackle around wrist
    add_box(vox, 9, 16, -3, 4, 18, 19, 'M_IronStaples', 'Forearm.L')
    # Broken dangling chain link
    vox[(16, 0, 17)] = ('M_IronStaples', 'Forearm.L')
    vox[(16, 0, 16)] = ('M_Rust', 'Forearm.L')
    
    # Left Crushing Fist (Bone: Hand.L, 1v gap at Z=17, massive 7x7x7 block)
    add_box(vox, 9, 16, -3, 4, 10, 16, 'M_RotDark', 'Hand.L')
    add_box(vox, 10, 15, -2, 3, 11, 15, 'M_BileFlesh', 'Hand.L')
    # Heavy closed knuckles facing forward (+Y)
    for kx in [10, 12, 14]:
        vox[(kx, 5, 14)] = ('M_IronStaples', 'Hand.L')
        vox[(kx, 5, 12)] = ('M_IronStaples', 'Hand.L')
        vox[(kx, 5, 13)] = ('M_BoneHighlight', 'Hand.L')  # Knuckle spike
        
    # -------------------------------------------------------------
    # 9. RIGHT ARM & COLOSSAL SPICED BONE CLEAVER
    # -------------------------------------------------------------
    # Right Shoulder Pauldron (Bone: Shoulder.R, X in [-14, -9])
    add_box(vox, -14, -9, -3, 3, 35, 40, 'M_IronStaples', 'Shoulder.R')
    add_box(vox, -13, -10, -2, 2, 36, 40, 'M_Rust', 'Shoulder.R')
    
    # Right Upper Arm (Bone: UpperArm.R, Z in [27, 33])
    add_box(vox, -14, -10, -2, 2, 27, 33, 'M_BileFlesh', 'UpperArm.R')
    
    # Right Forearm (Bone: Forearm.R, Z in [18, 25])
    add_box(vox, -14, -10, -2, 2, 18, 25, 'M_BileFlesh', 'Forearm.R')
    # Blood-soaked bandage wraps
    add_box(vox, -14, -10, -2, 2, 20, 22, 'M_RotDark', 'Forearm.R')
    vox[(-10, 0, 21)] = ('M_BloodDark', 'Forearm.R')
    vox[(-10, 1, 21)] = ('M_BloodFresh', 'Forearm.R')
    
    # Right Hand (Bone: Hand.R, grip around cleaver handle)
    add_box(vox, -13, -9, -2, 2, 13, 16, 'M_RotDark', 'Hand.R')
    
    # Colossal Jagged Bone Meat-Cleaver (Bone: Weapon, parented to Hand.R)
    # Handle / Shaft (extending through hand: X in [-12, -10], Y in [-1, 1], Z from 6 to 24)
    add_box(vox, -12, -10, -1, 1, 6, 24, 'M_Rust', 'Weapon')
    # Iron pommel spike
    add_box(vox, -12, -10, -1, 1, 4, 5, 'M_IronStaples', 'Weapon')
    vox[(-11, 0, 3)] = ('M_IronStaples', 'Weapon')
    
    # Heavy Cleaver Spine (Weathered ancient bone reinforced with iron)
    # Z in [20, 44], Y in [-3, 0], X in [-12, -10]
    add_box(vox, -12, -10, -3, 0, 20, 44, 'M_Bone', 'Weapon')
    # Iron banding clamps
    for bz in [22, 29, 36]:
        add_box(vox, -13, -9, -4, 1, bz, bz + 1, 'M_IronStaples', 'Weapon')
        vox[(-11, -4, bz)] = ('M_Rust', 'Weapon')
        
    # Massive Serrated Bone Blade & Hook (protruding forward into Y: [1, 6])
    for bz in range(21, 45):
        # Blade width widens towards the top
        max_y = 5 if bz < 35 else 6
        for by in range(1, max_y + 1):
            mat = 'M_Bone'
            if by == max_y:
                # Jagged serrated teeth
                mat = 'M_BoneHighlight' if bz % 2 == 0 else 'M_BloodFresh'
            vox[(-11, by, bz)] = (mat, 'Weapon')
            vox[(-12, by, bz)] = (mat, 'Weapon')
            
    # Forward Butcher Hook at top tip (Z in [42, 44], Y curving forward to 8)
    add_box(vox, -12, -10, 6, 8, 42, 44, 'M_BoneHighlight', 'Weapon')
    vox[(-11, 8, 41)] = ('M_BloodFresh', 'Weapon')
    vox[(-11, 7, 40)] = ('M_BloodDark', 'Weapon')
    
    # -------------------------------------------------------------
    # 10. GROUND IMPACT SHOCKWAVE VFX (Bone: Shockwave)
    # -------------------------------------------------------------
    # Concentric fractured earth and stone shards in front of the giant
    for sx in range(-9, 10):
        for sy in range(6, 19):
            dist = math.sqrt((sx * 0.8)**2 + ((sy - 12) * 0.9)**2)
            if 3.5 <= dist <= 7.0 and (sx + sy) % 2 == 0:
                vox[(sx, sy, 0)] = ('M_SlamShockwave', 'Shockwave')
                if dist <= 5.0 and (sx * sy) % 3 == 0:
                    vox[(sx, sy, 1)] = ('M_Bone', 'Shockwave')
                    
    return vox

def build_mesh_from_voxels(vox_dict, materials):
    """
    Build optimized micro-voxel geometry with exposed quad checking
    and planar quad dissolve per bone group.
    """
    scene = bpy.context.scene
    temp_objects = []
    
    # Group voxels by bone name
    bone_voxels = {}
    for pos, (mat_name, bone_name) in vox_dict.items():
        bone_voxels.setdefault(bone_name, {})[pos] = mat_name
        
    V = VOXEL_SIZE
    directions = [
        (( 1,  0,  0), [Vector((1,0,0)), Vector((1,1,0)), Vector((1,1,1)), Vector((1,0,1))]),  # +X
        ((-1,  0,  0), [Vector((0,1,0)), Vector((0,0,0)), Vector((0,0,1)), Vector((0,1,1))]),  # -X
        (( 0,  1,  0), [Vector((1,1,0)), Vector((0,1,0)), Vector((0,1,1)), Vector((1,1,1))]),  # +Y
        (( 0, -1,  0), [Vector((0,0,0)), Vector((1,0,0)), Vector((1,0,1)), Vector((0,0,1))]),  # -Y
        (( 0,  0,  1), [Vector((0,0,1)), Vector((1,0,1)), Vector((1,1,1)), Vector((0,1,1))]),  # +Z
        (( 0,  0, -1), [Vector((0,1,0)), Vector((1,1,0)), Vector((1,0,0)), Vector((0,0,0))]),  # -Z
    ]
    
    for bone_name, b_vox in bone_voxels.items():
        bm = bmesh.new()
        
        # Track materials used in this segment
        mat_indices = {}
        for mat_name in set(b_vox.values()):
            if mat_name in materials:
                mat_indices[mat_name] = len(mat_indices)
                
        for (vx, vy, vz), mat_name in b_vox.items():
            base_pos = Vector((vx * V, vy * V, vz * V))
            
            for (dx, dy, dz), face_offsets in directions:
                neighbor = (vx + dx, vy + dy, vz + dz)
                # Exposed if empty OR neighbor belongs to a DIFFERENT bone!
                is_exposed = False
                if neighbor not in vox_dict:
                    is_exposed = True
                elif vox_dict[neighbor][1] != bone_name:
                    is_exposed = True
                    
                if is_exposed:
                    v_coords = [base_pos + offset * V for offset in face_offsets]
                    face_verts = []
                    for co in v_coords:
                        face_verts.append(bm.verts.new(co))
                    try:
                        face = bm.faces.new(face_verts)
                        face.material_index = mat_indices.get(mat_name, 0)
                    except ValueError:
                        pass  # Skip degenerate face
                        
        # Optimize planar coplanar voxel faces
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        bmesh.ops.dissolve_limit(bm, angle_limit=0.001, verts=bm.verts, edges=bm.edges, delimit={'MATERIAL'})
        
        part_mesh = bpy.data.meshes.new(f"Mesh_{bone_name}")
        bm.to_mesh(part_mesh)
        bm.free()
        
        part_obj = bpy.data.objects.new(f"Part_{bone_name}", part_mesh)
        scene.collection.objects.link(part_obj)
        
        # Add materials to object
        for mat_name in sorted(mat_indices, key=lambda k: mat_indices[k]):
            part_mesh.materials.append(materials[mat_name])
            
        # Create Vertex Group with full weight for this bone
        vg = part_obj.vertex_groups.new(name=bone_name)
        vg.add(list(range(len(part_mesh.vertices))), 1.0, 'REPLACE')
        
        temp_objects.append(part_obj)
        
    # Join all body segments into unified mesh
    bpy.ops.object.select_all(action='DESELECT')
    for obj in temp_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = temp_objects[0]
    bpy.ops.object.join()
    
    main_obj = bpy.context.view_layer.objects.active
    main_obj.name = "ZombieGiant_Mesh"
    
    # Ensure flat shading for authentic retro micro-voxel aesthetic
    for p in main_obj.data.polygons:
        p.use_smooth = False
        
    return main_obj

def build_armature():
    """Create the skeletal armature with all standard sockets and hierarchy."""
    V = VOXEL_SIZE
    arm_data = bpy.data.armatures.new("ZombieGiant_Armature")
    arm_obj = bpy.data.objects.new("ZombieGiant_Rig", arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones
    
    def add_bone(name, head, tail, parent_name=None):
        b = eb.new(name)
        b.head = Vector(head)
        b.tail = Vector(tail)
        if parent_name and parent_name in eb:
            b.parent = eb[parent_name]
            b.use_connect = False
        return b
        
    # Root & Core Spine
    add_bone('Root', (0, 0, 0), (0, 0, 0.15))
    add_bone('Hips', (0, 0, 20 * V), (0, 0, 25 * V), 'Root')
    add_bone('Belly', (0, 3 * V, 26 * V), (0, 8 * V, 26 * V), 'Hips')
    add_bone('Spine', (0, 0, 25 * V), (0, 0, 32 * V), 'Hips')
    add_bone('Chest', (0, 0, 32 * V), (0, 0, 38 * V), 'Spine')
    add_bone('Neck', (0, 1 * V, 37 * V), (0, 2 * V, 39 * V), 'Chest')
    add_bone('Head', (0, 2 * V, 39 * V), (0, 2 * V, 45 * V), 'Neck')
    add_bone('Jaw', (0, 3 * V, 36 * V), (0, 6 * V, 36 * V), 'Head')
    
    # Standard Sockets
    add_bone('Socket_Head', (0, 2 * V, 45 * V), (0, 2 * V, 47 * V), 'Head')
    add_bone('Socket_Back', (0, -6 * V, 36 * V), (0, -8 * V, 36 * V), 'Chest')
    
    # Left Arm
    add_bone('Shoulder.L', (7 * V, 0, 37 * V), (11 * V, 0, 37 * V), 'Chest')
    add_bone('UpperArm.L', (12 * V, 0, 35 * V), (12 * V, 0, 26 * V), 'Shoulder.L')
    add_bone('Forearm.L', (12 * V, 0, 25 * V), (12 * V, 0, 17 * V), 'UpperArm.L')
    add_bone('Hand.L', (12 * V, 0, 16 * V), (12 * V, 0, 9 * V), 'Forearm.L')
    add_bone('Socket_Hand_L', (12 * V, 0, 12 * V), (12 * V, 1 * V, 12 * V), 'Hand.L')
    
    # Right Arm & Weapon
    add_bone('Shoulder.R', (-7 * V, 0, 37 * V), (-11 * V, 0, 37 * V), 'Chest')
    add_bone('UpperArm.R', (-12 * V, 0, 35 * V), (-12 * V, 0, 26 * V), 'Shoulder.R')
    add_bone('Forearm.R', (-12 * V, 0, 25 * V), (-12 * V, 0, 17 * V), 'UpperArm.R')
    add_bone('Hand.R', (-12 * V, 0, 16 * V), (-12 * V, 0, 12 * V), 'Forearm.R')
    add_bone('Socket_Hand_R', (-11 * V, 0, 14 * V), (-11 * V, 1 * V, 14 * V), 'Hand.R')
    add_bone('Weapon', (-11 * V, 0, 14 * V), (-11 * V, 0, 35 * V), 'Hand.R')
    
    # Left Leg
    add_bone('UpperLeg.L', (5 * V, 0, 18 * V), (5 * V, 0, 12 * V), 'Hips')
    add_bone('LowerLeg.L', (5 * V, 0, 11 * V), (5 * V, 0, 5 * V), 'UpperLeg.L')
    add_bone('Foot.L', (5 * V, 0, 4 * V), (5 * V, 3 * V, 0), 'LowerLeg.L')
    
    # Right Leg
    add_bone('UpperLeg.R', (-5 * V, 0, 18 * V), (-5 * V, 0, 12 * V), 'Hips')
    add_bone('LowerLeg.R', (-5 * V, 0, 11 * V), (-5 * V, 0, 5 * V), 'UpperLeg.R')
    add_bone('Foot.R', (-5 * V, 0, 4 * V), (-5 * V, 3 * V, 0), 'LowerLeg.R')
    
    # Shockwave VFX
    add_bone('Shockwave', (0, 14 * V, 0), (0, 14 * V, 4 * V), 'Root')
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

def animate_walk(arm_obj):
    """Animate a heavy, earth-shaking 36-frame walk cycle."""
    act = bpy.data.actions.new("Walk")
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = act
    
    pb = arm_obj.pose.bones
    for b in pb:
        b.rotation_mode = 'XYZ'
        
    def kf_rot(name, frame, rx, ry, rz):
        p = pb.get(name)
        if p:
            p.rotation_euler = (rx, ry, rz)
            p.keyframe_insert("rotation_euler", frame=frame)
            
    def kf_loc(name, frame, lx, ly, lz):
        p = pb.get(name)
        if p:
            p.location = (lx, ly, lz)
            p.keyframe_insert("location", frame=frame)
            
    def kf_scale(name, frame, sx, sy, sz):
        p = pb.get(name)
        if p:
            p.scale = (sx, sy, sz)
            p.keyframe_insert("scale", frame=frame)
            
    frames = [0, 9, 18, 27, 36]
    
    for f in range(0, 37):
        kf_scale('Shockwave', f, 0.001, 0.001, 0.001)
        
    # Frame 0: Passing stance (Left forward, Right back)
    kf_loc('Root', 0, 0, 0, 0)
    kf_rot('Root', 0, 0, 0, 0)
    kf_rot('Hips', 0, 0, 0, 0)
    kf_rot('Belly', 0, 0, 0, 0)
    kf_rot('Spine', 0, -0.05, 0, 0)
    kf_rot('Chest', 0, -0.05, 0, 0)
    kf_rot('Head', 0, 0.05, 0, 0)
    kf_rot('Jaw', 0, 0.05, 0, 0)
    kf_rot('UpperLeg.L', 0, 0.35, 0, 0)
    kf_rot('LowerLeg.L', 0, 0.10, 0, 0)
    kf_rot('Foot.L', 0, -0.25, 0, 0)
    kf_rot('UpperLeg.R', 0, -0.30, 0, 0)
    kf_rot('LowerLeg.R', 0, 0.30, 0, 0)
    kf_rot('Foot.R', 0, 0.15, 0, 0)
    kf_rot('UpperArm.L', 0, -0.30, 0, 0.1)
    kf_rot('Forearm.L', 0, 0.30, 0, 0)
    kf_rot('UpperArm.R', 0, 0.30, 0, -0.1)
    kf_rot('Forearm.R', 0, 0.20, 0, 0)
    kf_rot('Weapon', 0, 0, 0, 0)
    
    # Frame 9: Left Foot Impact Stomp (Thud!)
    kf_loc('Root', 9, 0, 0, -0.04)
    kf_rot('Hips', 9, -0.03, 0.10, 0.08)    # Roll towards planted foot
    kf_rot('Belly', 9, 0.06, -0.14, -0.12)  # Belly inertia lags right
    kf_rot('Chest', 9, -0.05, -0.08, -0.06)
    kf_rot('Head', 9, 0.08, 0.05, 0.04)
    kf_rot('Jaw', 9, 0.14, 0, 0)            # Jaw jiggles open
    kf_rot('UpperLeg.L', 9, 0.15, 0, 0)
    kf_rot('LowerLeg.L', 9, 0.20, 0, 0)
    kf_rot('Foot.L', 9, -0.35, 0, 0)
    kf_rot('UpperLeg.R', 9, -0.25, 0, 0)
    kf_rot('LowerLeg.R', 9, 0.45, 0, 0)
    kf_rot('Foot.R', 9, 0.20, 0, 0)
    kf_rot('UpperArm.L', 9, -0.15, 0, 0.15)
    kf_rot('Forearm.L', 9, 0.35, 0, 0)
    kf_rot('UpperArm.R', 9, 0.15, 0, -0.15)
    kf_rot('Forearm.R', 9, 0.25, 0, 0)
    
    # Frame 18: Passing stance (Right forward, Left back)
    kf_loc('Root', 18, 0, 0, 0.01)
    kf_rot('Hips', 18, 0, 0, 0)
    kf_rot('Belly', 18, -0.02, 0, 0)
    kf_rot('Chest', 18, -0.05, 0, 0)
    kf_rot('Head', 18, 0.05, 0, 0)
    kf_rot('Jaw', 18, 0.05, 0, 0)
    kf_rot('UpperLeg.L', 18, -0.30, 0, 0)
    kf_rot('LowerLeg.L', 18, 0.30, 0, 0)
    kf_rot('Foot.L', 18, 0.15, 0, 0)
    kf_rot('UpperLeg.R', 18, 0.35, 0, 0)
    kf_rot('LowerLeg.R', 18, 0.10, 0, 0)
    kf_rot('Foot.R', 18, -0.25, 0, 0)
    kf_rot('UpperArm.L', 18, 0.30, 0, 0.1)
    kf_rot('Forearm.L', 18, 0.20, 0, 0)
    kf_rot('UpperArm.R', 18, -0.30, 0, -0.1)
    kf_rot('Forearm.R', 18, 0.30, 0, 0)
    
    # Frame 27: Right Foot Impact Stomp (Thud!)
    kf_loc('Root', 27, 0, 0, -0.04)
    kf_rot('Hips', 27, -0.03, -0.10, -0.08)   # Roll towards right foot
    kf_rot('Belly', 27, 0.06, 0.14, 0.12)     # Belly inertia lags left
    kf_rot('Chest', 27, -0.05, 0.08, 0.06)
    kf_rot('Head', 27, 0.08, -0.05, -0.04)
    kf_rot('Jaw', 27, 0.14, 0, 0)
    kf_rot('UpperLeg.R', 27, 0.15, 0, 0)
    kf_rot('LowerLeg.R', 27, 0.20, 0, 0)
    kf_rot('Foot.R', 27, -0.35, 0, 0)
    kf_rot('UpperLeg.L', 27, -0.25, 0, 0)
    kf_rot('LowerLeg.L', 27, 0.45, 0, 0)
    kf_rot('Foot.L', 27, 0.20, 0, 0)
    kf_rot('UpperArm.L', 27, 0.15, 0, 0.15)
    kf_rot('Forearm.L', 27, 0.25, 0, 0)
    kf_rot('UpperArm.R', 27, -0.15, 0, -0.15)
    kf_rot('Forearm.R', 27, 0.35, 0, 0)
    
    # Frame 36: Seamless loop to Frame 0
    kf_loc('Root', 36, 0, 0, 0)
    kf_rot('Root', 36, 0, 0, 0)
    kf_rot('Hips', 36, 0, 0, 0)
    kf_rot('Belly', 36, 0, 0, 0)
    kf_rot('Spine', 36, -0.05, 0, 0)
    kf_rot('Chest', 36, -0.05, 0, 0)
    kf_rot('Head', 36, 0.05, 0, 0)
    kf_rot('Jaw', 36, 0.05, 0, 0)
    kf_rot('UpperLeg.L', 36, 0.35, 0, 0)
    kf_rot('LowerLeg.L', 36, 0.10, 0, 0)
    kf_rot('Foot.L', 36, -0.25, 0, 0)
    kf_rot('UpperLeg.R', 36, -0.30, 0, 0)
    kf_rot('LowerLeg.R', 36, 0.30, 0, 0)
    kf_rot('Foot.R', 36, 0.15, 0, 0)
    kf_rot('UpperArm.L', 36, -0.30, 0, 0.1)
    kf_rot('Forearm.L', 36, 0.30, 0, 0)
    kf_rot('UpperArm.R', 36, 0.30, 0, -0.1)
    kf_rot('Forearm.R', 36, 0.20, 0, 0)
    kf_rot('Weapon', 36, 0, 0, 0)
    
    # Push to NLA Track
    track = arm_obj.animation_data.nla_tracks.new()
    track.name = "Walk"
    strip = track.strips.new("Walk", 0, act)
    strip.action = act
    return act

def animate_attack(arm_obj):
    """
    Animate a 50-frame brutal colossal Cleaver Cleave & Chop (Замах и Сокрушительный Удар тесаком).
    Dense keyframing every 2-3 frames ensures the quaternion SLERP trajectory is strictly locked
    to the arc: wind-up behind back -> hoist high above right shoulder -> violent downward chop into dirt.
    """
    act = bpy.data.actions.new("Attack")
    arm_obj.animation_data.action = act
    
    pb = arm_obj.pose.bones
    for b in pb:
        b.rotation_mode = 'XYZ'
        
    def kf_rot(name, frame, rx, ry, rz):
        p = pb.get(name)
        if p:
            p.rotation_euler = (rx, ry, rz)
            p.keyframe_insert("rotation_euler", frame=frame)
            
    def kf_loc(name, frame, lx, ly, lz):
        p = pb.get(name)
        if p:
            p.location = (lx, ly, lz)
            p.keyframe_insert("location", frame=frame)
            
    def kf_scale(name, frame, sx, sy, sz):
        p = pb.get(name)
        if p:
            p.scale = (sx, sy, sz)
            p.keyframe_insert("scale", frame=frame)
            
    # Shockwave initial hidden state
    for f in range(0, 27):
        kf_scale('Shockwave', f, 0.001, 0.001, 0.001)

    # -------------------------------------------------------------------------
    # PHASE 1: ASYMMETRIC MASSIVE WIND-UP / HOIST (Frames 0 to 20)
    # The right arm pulls BACKWARDS behind the right shoulder and heaves high!
    # -------------------------------------------------------------------------
    # Frame 0: Ready Stance
    kf_loc('Root', 0, 0, 0, 0)
    kf_rot('Root', 0, 0, 0, 0)
    kf_rot('Hips', 0, 0, 0, 0)
    kf_rot('Belly', 0, 0, 0, 0)
    kf_rot('Spine', 0, -0.08, 0, 0)
    kf_rot('Chest', 0, -0.08, 0, 0)
    kf_rot('Head', 0, 0.08, 0, 0)
    kf_rot('Jaw', 0, 0, 0, 0)
    kf_rot('UpperArm.R', 0, -0.25, 0.05, -0.15)
    kf_rot('Forearm.R', 0, 0.45, 0, 0)
    kf_rot('Hand.R', 0, 0, 0, 0)
    kf_rot('Weapon', 0, 0.10, 0, 0)
    kf_rot('UpperArm.L', 0, -0.20, 0, 0.15)
    kf_rot('Forearm.L', 0, 0.40, 0, 0)
    kf_rot('Hand.L', 0, 0, 0, 0)
    kf_rot('UpperLeg.L', 0, 0.10, 0, 0.05)
    kf_rot('LowerLeg.L', 0, 0.15, 0, 0)
    kf_rot('Foot.L', 0, -0.15, 0, 0)
    kf_rot('UpperLeg.R', 0, 0.10, 0, -0.05)
    kf_rot('LowerLeg.R', 0, 0.15, 0, 0)
    kf_rot('Foot.R', 0, -0.15, 0, 0)

    # Frame 4: Arm drawing back, body begins twisting right
    kf_loc('Root', 4, 0, -0.02, -0.02)
    kf_rot('Hips', 4, 0.03, 0.02, -0.08)
    kf_rot('Spine', 4, 0.00, 0.02, -0.10)
    kf_rot('Chest', 4, 0.00, 0.02, -0.08)
    kf_rot('UpperArm.R', 4, -0.55, 0.10, -0.22)
    kf_rot('Forearm.R', 4, 0.65, 0, 0)
    kf_rot('Weapon', 4, 0.22, 0, 0.08)
    kf_rot('UpperArm.L', 4, -0.25, 0.05, 0.22)
    kf_rot('Forearm.L', 4, 0.50, 0, 0)

    # Frame 8: Drawing behind back, deep crouch
    kf_loc('Root', 8, 0, -0.04, -0.05)
    kf_rot('Hips', 8, 0.06, 0.04, -0.16)
    kf_rot('Belly', 8, 0.02, 0, -0.12)
    kf_rot('Spine', 8, 0.08, 0.04, -0.20)
    kf_rot('Chest', 8, 0.06, 0.04, -0.16)
    kf_rot('UpperArm.R', 8, -1.05, 0.18, -0.32)
    kf_rot('Forearm.R', 8, 0.85, 0, 0)
    kf_rot('Weapon', 8, 0.40, 0, 0.15)
    kf_rot('UpperArm.L', 8, -0.30, 0.10, 0.30)
    kf_rot('Forearm.L', 8, 0.65, 0, 0)

    # Frame 12: Reaching back and starting upward hoist
    kf_loc('Root', 12, 0, -0.06, -0.02)
    kf_rot('Hips', 12, 0.10, 0.05, -0.22)
    kf_rot('Spine', 12, 0.16, 0.05, -0.30)
    kf_rot('Chest', 12, 0.14, 0.05, -0.24)
    kf_rot('UpperArm.R', 12, -1.50, 0.25, -0.40)
    kf_rot('Forearm.R', 12, 1.00, 0, 0)
    kf_rot('Weapon', 12, 0.58, 0, 0.22)
    kf_rot('Head', 12, 0.15, 0, 0.08)
    kf_rot('Jaw', 12, 0.30, 0, 0)

    # Frame 16: Coiling high above right shoulder
    kf_loc('Root', 16, 0, -0.07, 0.02)
    kf_rot('Hips', 16, 0.15, 0.07, -0.26)
    kf_rot('Spine', 16, 0.25, 0.06, -0.38)
    kf_rot('Chest', 16, 0.22, 0.06, -0.32)
    kf_rot('UpperArm.R', 16, -1.95, 0.32, -0.48)
    kf_rot('Forearm.R', 16, 1.10, 0, 0)
    kf_rot('Weapon', 16, 0.72, 0, 0.28)
    kf_rot('UpperArm.L', 16, -0.35, 0.10, 0.38)
    kf_rot('Forearm.L', 16, 0.75, 0, 0)
    kf_rot('Head', 16, 0.24, 0, 0.14)
    kf_rot('Jaw', 16, 0.50, 0, 0)

    # Frame 20: Apex Wind-up (Massive cleaver tilted far back, jaw wide open)
    kf_loc('Root', 20, 0, -0.08, 0.04)
    kf_rot('Root', 20, 0.08, 0, -0.05)
    kf_rot('Hips', 20, 0.18, 0.08, -0.28)
    kf_rot('Belly', 20, -0.12, 0, -0.22)
    kf_rot('Spine', 20, 0.32, 0.06, -0.42)
    kf_rot('Chest', 20, 0.26, 0.06, -0.35)
    kf_rot('Neck', 20, 0.15, 0, -0.15)
    kf_rot('Head', 20, 0.28, 0, 0.18)
    kf_rot('Jaw', 20, 0.65, 0, 0)
    kf_rot('UpperArm.R', 20, -2.30, 0.40, -0.55)
    kf_rot('Forearm.R', 20, 1.15, 0, 0)
    kf_rot('Weapon', 20, 0.80, 0, 0.30)
    kf_rot('UpperArm.L', 20, -0.35, 0.10, 0.40)
    kf_rot('Forearm.L', 20, 0.75, 0, 0)

    # Frame 22: Apex tension hold (kinetic snap trigger)
    kf_loc('Root', 22, 0, -0.08, 0.04)
    kf_rot('Hips', 22, 0.18, 0.08, -0.28)
    kf_rot('Spine', 22, 0.32, 0.06, -0.42)
    kf_rot('UpperArm.R', 22, -2.30, 0.40, -0.55)
    kf_rot('Forearm.R', 22, 1.15, 0, 0)
    kf_rot('Weapon', 22, 0.80, 0, 0.30)

    # -------------------------------------------------------------------------
    # PHASE 2: EXPLOSIVE DOWNWARD CLEAVE & CHOP (Frames 23 to 27)
    # Dense intermediate keyframes every frame to guarantee perfect downward arc!
    # -------------------------------------------------------------------------
    # Frame 23: Torso snaps, cleaver begins violent downward plunge
    kf_loc('Root', 23, 0, -0.02, 0.02)
    kf_rot('Hips', 23, 0.12, 0.05, -0.18)
    kf_rot('Spine', 23, 0.20, 0.04, -0.25)
    kf_rot('UpperArm.R', 23, -1.90, 0.30, -0.45)
    kf_rot('Forearm.R', 23, 1.05, 0, 0)
    kf_rot('Weapon', 23, 0.60, 0, 0.20)

    # Frame 24: Arm sweeps over right shoulder
    kf_loc('Root', 24, 0, 0.04, -0.02)
    kf_rot('Hips', 24, 0.05, 0.02, -0.08)
    kf_rot('Spine', 24, 0.05, 0.02, -0.10)
    kf_rot('UpperArm.R', 24, -1.40, 0.20, -0.35)
    kf_rot('Forearm.R', 24, 0.90, 0, 0)
    kf_rot('Weapon', 24, 0.25, 0, 0.10)

    # Frame 25: Massive acceleration through strike plane (cutting edge leads!)
    kf_loc('Root', 25, 0, 0.10, -0.06)
    kf_rot('Hips', 25, -0.05, 0, 0.05)
    kf_rot('Spine', 25, -0.10, 0, 0.05)
    kf_rot('UpperArm.R', 25, -0.80, 0.10, -0.25)
    kf_rot('Forearm.R', 25, 0.70, 0, 0)
    kf_rot('Weapon', 25, -0.15, 0, -0.05)
    kf_rot('UpperArm.L', 25, 0.15, 0, 0.20)
    kf_rot('Forearm.L', 25, 0.50, 0, 0)

    # Frame 26: Supersonic slice just before ground contact
    kf_loc('Root', 26, 0, 0.15, -0.10)
    kf_rot('Hips', 26, -0.15, -0.03, 0.15)
    kf_rot('Spine', 26, -0.22, -0.03, 0.18)
    kf_rot('Chest', 26, -0.15, -0.03, 0.15)
    kf_rot('UpperArm.R', 26, -0.10, 0.05, -0.20)
    kf_rot('Forearm.R', 26, 0.50, 0, 0)
    kf_rot('Weapon', 26, -0.45, 0, -0.10)
    kf_rot('UpperArm.L', 26, 0.35, 0, 0.30)
    kf_rot('Forearm.L', 26, 0.35, 0, 0)

    # Frame 27: GROUND IMPACT / EARTH BURIAL!
    kf_loc('Root', 27, 0, 0.18, -0.12)
    kf_rot('Hips', 27, -0.20, -0.05, 0.22)
    kf_rot('Belly', 27, 0.28, -0.08, 0.16)
    kf_rot('Spine', 27, -0.30, -0.05, 0.25)
    kf_rot('Chest', 27, -0.20, -0.05, 0.20)
    kf_rot('Neck', 27, 0.10, 0, -0.05)
    kf_rot('Head', 27, 0.35, 0, -0.15)
    kf_rot('Jaw', 27, 0.25, 0, 0)
    kf_rot('UpperArm.R', 27, 0.80, 0, -0.18)
    kf_rot('Forearm.R', 27, 0.35, 0, 0)
    kf_rot('Weapon', 27, -0.65, 0, -0.12)
    kf_rot('UpperArm.L', 27, 0.45, 0, 0.35)
    kf_rot('Forearm.L', 27, 0.30, 0, 0)
    kf_rot('UpperLeg.L', 27, 0.45, 0, 0.10)
    kf_rot('LowerLeg.L', 27, 0.50, 0, 0)
    kf_rot('Foot.L', 27, -0.25, 0, 0)
    kf_rot('UpperLeg.R', 27, -0.15, 0, -0.10)
    kf_rot('LowerLeg.R', 27, 0.55, 0, 0)
    kf_rot('Foot.R', 27, 0.20, 0, 0)

    # -------------------------------------------------------------------------
    # PHASE 3: IMPACT OVERSHOOT & SHOCKWAVE ERUPTION (Frames 28 to 31)
    # -------------------------------------------------------------------------
    kf_loc('Root', 28, 0, 0.19, -0.13)
    kf_scale('Shockwave', 28, 1.40, 1.40, 1.15)
    kf_rot('Weapon', 28, -0.65, 0, -0.12)

    kf_scale('Shockwave', 30, 1.50, 1.50, 0.85)

    # -------------------------------------------------------------------------
    # PHASE 4: HIT-STOP & RECOIL TREMOR (Frames 32 to 38)
    # -------------------------------------------------------------------------
    kf_loc('Root', 32, 0, 0.19, -0.13)
    kf_rot('Spine', 32, -0.30, -0.05, 0.25)
    kf_rot('Weapon', 32, -0.65, 0, -0.12)

    tremors = [
        (33, -0.11, -0.28, -0.63),
        (34, -0.13, -0.32, -0.67),
        (35, -0.115, -0.29, -0.64),
        (36, -0.125, -0.31, -0.66),
        (37, -0.12, -0.30, -0.65)
    ]
    for tf, tz, tsp, twp in tremors:
        kf_loc('Root', tf, 0, 0.18, tz)
        kf_rot('Spine', tf, tsp, -0.05, 0.25)
        kf_rot('Weapon', tf, twp, 0, -0.12)

    kf_scale('Shockwave', 34, 1.2, 1.2, 0.5)
    kf_scale('Shockwave', 37, 0.001, 0.001, 0.001)
    for f in range(38, 51):
        kf_scale('Shockwave', f, 0.001, 0.001, 0.001)

    # -------------------------------------------------------------------------
    # PHASE 5: WRENCHING DISLODGE & RESET (Frames 39 to 50)
    # -------------------------------------------------------------------------
    kf_loc('Root', 39, 0, 0.14, -0.09)
    kf_rot('UpperArm.R', 39, 0.55, 0, -0.16)
    kf_rot('Weapon', 39, -0.50, 0, -0.08)

    kf_loc('Root', 41, 0, 0.10, -0.06)
    kf_rot('Hips', 41, -0.10, 0, 0.08)
    kf_rot('Belly', 41, 0.08, 0, 0.05)
    kf_rot('Spine', 41, -0.12, 0, 0.08)
    kf_rot('Chest', 41, -0.10, 0, 0.05)
    kf_rot('Head', 41, 0.15, 0, 0)
    kf_rot('UpperArm.R', 41, 0.35, 0, -0.15)
    kf_rot('Forearm.R', 41, 0.50, 0, 0)
    kf_rot('Weapon', 41, -0.30, 0, -0.05)
    kf_rot('UpperArm.L', 41, 0.10, 0, 0.15)

    kf_loc('Root', 44, 0, 0.06, -0.03)
    kf_rot('Hips', 44, -0.06, 0, 0.04)
    kf_rot('Spine', 44, -0.08, 0, 0.04)
    kf_rot('UpperArm.R', 44, 0.05, 0.02, -0.15)
    kf_rot('Forearm.R', 44, 0.48, 0, 0)
    kf_rot('Weapon', 44, -0.10, 0, 0)
    kf_rot('UpperArm.L', 44, -0.05, 0, 0.15)

    kf_loc('Root', 47, 0, 0.02, -0.01)
    kf_rot('Hips', 47, -0.02, 0, 0)
    kf_rot('Spine', 47, -0.08, 0, 0)
    kf_rot('UpperArm.R', 47, -0.18, 0.04, -0.18)
    kf_rot('Forearm.R', 47, 0.46, 0, 0)
    kf_rot('Weapon', 47, 0.05, 0, 0)
    kf_rot('UpperArm.L', 47, -0.15, 0, 0.15)

    kf_loc('Root', 50, 0, 0, 0)
    kf_rot('Root', 50, 0, 0, 0)
    kf_rot('Hips', 50, 0, 0, 0)
    kf_rot('Belly', 50, 0, 0, 0)
    kf_rot('Spine', 50, -0.08, 0, 0)
    kf_rot('Chest', 50, -0.08, 0, 0)
    kf_rot('Head', 50, 0.08, 0, 0)
    kf_rot('Jaw', 50, 0, 0, 0)
    kf_rot('UpperLeg.L', 50, 0.10, 0, 0.05)
    kf_rot('LowerLeg.L', 50, 0.15, 0, 0)
    kf_rot('Foot.L', 50, -0.15, 0, 0)
    kf_rot('UpperLeg.R', 50, 0.10, 0, -0.05)
    kf_rot('LowerLeg.R', 50, 0.15, 0, 0)
    kf_rot('Foot.R', 50, -0.15, 0, 0)
    kf_rot('UpperArm.R', 50, -0.25, 0.05, -0.15)
    kf_rot('Forearm.R', 50, 0.45, 0, 0)
    kf_rot('Weapon', 50, 0.10, 0, 0)
    kf_rot('UpperArm.L', 50, -0.20, 0, 0.15)
    kf_rot('Forearm.L', 50, 0.40, 0, 0)
    
    # Push to NLA Track
    track = arm_obj.animation_data.nla_tracks.new()
    track.name = "Attack"
    strip = track.strips.new("Attack", 0, act)
    strip.action = act
    return act

def setup_lighting():
    """Setup 3-point dramatic hero lighting with crimson rim accent."""
    scene = bpy.context.scene
    
    # 1. Key Light (Warm golden sunlight shining from front-left onto face, belly & cleaver)
    key_data = bpy.data.lights.new(name="KeyLight", type='SUN')
    key_data.energy = 5.5
    key_data.color = (1.0, 0.96, 0.88)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    scene.collection.objects.link(key_obj)
    dir_key = Vector((-0.6, -1.0, -0.5)).normalized()
    key_obj.rotation_euler = dir_key.to_track_quat('-Z', 'Y').to_euler()
    
    # 2. Fill Light (Cool azure sky fill from front-right)
    fill_data = bpy.data.lights.new(name="FillLight", type='SUN')
    fill_data.energy = 2.8
    fill_data.color = (0.55, 0.68, 0.88)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    scene.collection.objects.link(fill_obj)
    dir_fill = Vector((0.8, -0.9, -0.4)).normalized()
    fill_obj.rotation_euler = dir_fill.to_track_quat('-Z', 'Y').to_euler()
    
    # 3. Menacing Crimson Rim Light (Accentuates back hump, bone ribs & cleaver spine)
    rim_data = bpy.data.lights.new(name="RimLight", type='SUN')
    rim_data.energy = 3.5
    rim_data.color = (0.98, 0.20, 0.04)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    scene.collection.objects.link(rim_obj)
    dir_rim = Vector((-0.1, 1.2, -0.3)).normalized()
    rim_obj.rotation_euler = dir_rim.to_track_quat('-Z', 'Y').to_euler()

def setup_camera_evaluated(action_frame=28, resolution=(1024, 1024), margin=1.15):
    """
    Setup camera using evaluated depsgraph across the character mesh
    at the peak slam frame to guarantee the character fills 65%-80% of canvas.
    Never parents camera to any animated bones!
    """
    scene = bpy.context.scene
    scene.frame_set(action_frame)
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    
    depsgraph = bpy.context.evaluated_depsgraph_get()
    
    # Evaluate bounds from main character mesh
    main_mesh = bpy.data.objects.get("ZombieGiant_Mesh")
    all_corners = []
    if main_mesh:
        eval_obj = main_mesh.evaluated_get(depsgraph)
        mat = eval_obj.matrix_world
        all_corners.extend([mat @ Vector(corner) for corner in eval_obj.bound_box])
    else:
        for obj in scene.objects:
            if obj.type == 'MESH' and not obj.hide_render:
                eval_obj = obj.evaluated_get(depsgraph)
                mat = eval_obj.matrix_world
                all_corners.extend([mat @ Vector(corner) for corner in eval_obj.bound_box])
            
    if not all_corners:
        return None, None
        
    min_co = Vector((min(c.x for c in all_corners), min(c.y for c in all_corners), min(c.z for c in all_corners)))
    max_co = Vector((max(c.x for c in all_corners), max(c.y for c in all_corners), max(c.z for c in all_corners)))
    center = (min_co + max_co) * 0.5
    span = (max_co - min_co).length
    
    # Independent static CamTarget (centered on mid-body)
    cam_target = bpy.data.objects.new("CamTarget", None)
    scene.collection.objects.link(cam_target)
    cam_target.location = Vector((center.x, center.y, center.z + 0.02))
    
    # Independent static Camera
    cam_data = bpy.data.cameras.new("HeroCamera")
    cam_data.lens = 50.0  # 50mm portrait standard
    cam_obj = bpy.data.objects.new("HeroCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    # 35° elevated 3/4 isometric perspective from front-right (-X, +Y)
    fov_rad = cam_obj.data.angle
    dist = (span * 0.5) / math.tan(fov_rad * 0.5) * margin
    
    cam_dir = Vector((-0.55, 0.82, 0.46)).normalized()
    cam_obj.location = cam_target.location + cam_dir * dist
    
    tt = cam_obj.constraints.new('TRACK_TO')
    tt.target = cam_target
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'
    
    return cam_obj, cam_target

def render_beauty_shot(render_filepath, action_frame=28):
    """Configure Cycles AgX high contrast and render beauty shot."""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    
    # Cap samples for fast high-quality render
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    
    # AgX Color Management
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - High Contrast'
    
    scene.frame_set(action_frame)
    scene.render.filepath = render_filepath
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    
    print(f"Rendering beauty shot at frame {action_frame} to {render_filepath}...")
    bpy.ops.render.render(write_still=True)
    print("Beauty shot render complete!")

def export_glb_and_base64(glb_filepath, arm_obj):
    """Export glTF 2.0 binary with both Walk and Attack animation tracks."""
    # Ensure armature active and unselected action to let NLA export cleanly
    bpy.context.view_layer.objects.active = arm_obj
    arm_obj.animation_data.action = None
    
    print(f"Exporting GLB to {glb_filepath}...")
    bpy.ops.export_scene.gltf(
        filepath=glb_filepath,
        export_format='GLB',
        export_animations=True,
        export_animation_mode='NLA_TRACKS',
        export_nla_strips=True,
        export_bake_animation=True,
        export_skins=True,
        export_all_influences=False,
        export_apply=False,
        export_yup=True
    )
    print("GLB export complete!")
    
    # Generate _data.js
    data_js_path = glb_filepath.replace(".glb", "_data.js")
    with open(glb_filepath, "rb") as f:
        b64_str = base64.b64encode(f.read()).decode('utf-8')
    with open(data_js_path, "w", encoding="utf-8") as f:
        f.write(f'window.ZOMBIE_GIANT_BASE64 = "data:model/gltf-binary;base64,{b64_str}";\n')
    print(f"Base64 data written to {data_js_path} (length: {len(b64_str)} chars)")

def main():
    asset_dir = os.path.dirname(os.path.abspath(__file__))
    blend_path = os.path.join(asset_dir, "zombie_giant.blend")
    glb_path = os.path.join(asset_dir, "zombie_giant.glb")
    render_path = os.path.join(asset_dir, "zombie_giant_render.png")
    
    print("=== STARTING ZOMBIE GIANT PROCEDURAL GENERATION ===")
    reset_scene()
    
    # 1. Materials
    materials = create_materials()
    
    # 2. Voxel Geometry
    print("Building voxel coordinates...")
    vox_dict = build_abomination_voxels()
    print(f"Total active voxels: {len(vox_dict)}")
    
    # 3. Mesh Construction
    print("Generating optimized micro-voxel mesh with planar quad dissolve...")
    mesh_obj = build_mesh_from_voxels(vox_dict, materials)
    
    # 4. Rigging
    print("Building skeletal armature...")
    arm_obj = build_armature()
    
    # Parent mesh to armature
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE')
    
    # 5. Dual Animations
    print("Authoring 'Walk' animation (36 frames)...")
    animate_walk(arm_obj)
    
    print("Authoring 'Attack' animation (48 frames)...")
    animate_attack(arm_obj)
    
    # 6. Lighting & Camera
    print("Setting up dramatic hero lighting...")
    setup_lighting()
    
    print("Framing camera via evaluated depsgraph at peak slam frame (frame 28)...")
    setup_camera_evaluated(action_frame=28)
    
    # 7. Render Beauty Shot
    render_beauty_shot(render_path, action_frame=28)
    
    # 8. Export GLB & Base64
    export_glb_and_base64(glb_path, arm_obj)
    
    # 9. Save .blend file
    print(f"Saving Blender project to {blend_path}...")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    print("=== ZOMBIE GIANT ASSET GENERATION SUCCESSFUL ===")

if __name__ == "__main__":
    main()
