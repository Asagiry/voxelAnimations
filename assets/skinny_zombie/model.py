"""
Procedural 3D Voxel Modeler: Skinny Zombie (assets/skinny_zombie/model.py)
Authentic Trove/Cube World Chibi Biped Undead Monster.

Features:
- Emaciated, sunken silhouette with exposed hunched vertebrae and sharp ribcage (+1 to +2 relief).
- Asymmetrical decay: bare skeletal right arm & talons, desiccated gangrene left arm with wrist wraps.
- Bare skeletal foot with sharp bone talons on right; gaunt tattered boot on left.
- Sunken eye sockets with one burning necrotic/bloodlust glowing eye (M_EyeGlow, AgX safe).
- Gaping cranium fracture and dangling unhinged jaw with sharp needle fangs.
- Geometric curved claw slash VFX ribbons on ClawTrail.L and ClawTrail.R.
- Full Trove Biped Armature with standard sockets (Socket_Hand_R, Socket_Hand_L, Socket_Head, Socket_Back).
- Watertight boundary quad meshing with planar dissolve optimization.
- 1024x1024 Cycles AgX preview render.
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector

# ==============================================================================
# 1. GLOBAL CONSTANTS & PATHS
# ==============================================================================
VOXEL_SIZE = 0.015  # 1.5 cm per voxel

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLEND_PATH = os.path.join(SCRIPT_DIR, "skinny_zombie.blend")
PREVIEW_PATH = os.path.join(SCRIPT_DIR, "model_preview.png")

# ==============================================================================
# 2. SCENE INITIALIZATION
# ==============================================================================
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = "Scene_SkinnyZombie"

# ==============================================================================
# 3. SHADER & MATERIAL ARCHITECTURE (AgX Safe Principled BSDF)
# ==============================================================================
def create_voxel_material(name, base_color, roughness=0.6, metallic=0.0,
                          emission_color=None, emission_strength=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = base_color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        specular_input = bsdf.inputs.get("Specular IOR Level") or bsdf.inputs.get("Specular")
        if specular_input:
            specular_input.default_value = 0.5
        if emission_color:
            em_input = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
            if em_input:
                em_input.default_value = emission_color
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
        if alpha < 1.0:
            if "Alpha" in bsdf.inputs:
                bsdf.inputs["Alpha"].default_value = alpha
            mat.blend_method = 'BLEND'
    return mat

materials = {
    # Flesh & Necrosis
    "M_FleshGreen": create_voxel_material("M_FleshGreen", (0.075, 0.160, 0.068, 1.0), roughness=0.75),
    "M_FleshDark":  create_voxel_material("M_FleshDark",  (0.040, 0.088, 0.038, 1.0), roughness=0.85),
    
    # Bone & Ivory
    "M_DecayedBone":   create_voxel_material("M_DecayedBone",   (0.58, 0.54, 0.44, 1.0), roughness=0.60),
    "M_BoneHighlight": create_voxel_material("M_BoneHighlight", (0.78, 0.74, 0.62, 1.0), roughness=0.45),
    
    # Tattered Loincloth & Wraps
    "M_ClothTattered": create_voxel_material("M_ClothTattered", (0.16, 0.14, 0.13, 1.0), roughness=0.90),
    
    # Blood & Gore
    "M_BloodFresh": create_voxel_material("M_BloodFresh", (0.42, 0.015, 0.02, 1.0), roughness=0.18, metallic=0.10),
    "M_BloodDark":  create_voxel_material("M_BloodDark",  (0.12, 0.015, 0.015, 1.0), roughness=0.70),
    
    # Bloodlust Glowing Eye (AgX safe emission)
    "M_EyeGlow": create_voxel_material("M_EyeGlow", (0.95, 0.10, 0.02, 1.0),
                                       emission_color=(0.95, 0.10, 0.02, 1.0), emission_strength=2.4),
    
    # Claw Slash VFX Ribbons
    "M_SlashTrail": create_voxel_material("M_SlashTrail", (0.60, 0.02, 0.04, 0.85),
                                          emission_color=(0.55, 0.02, 0.03, 1.0), emission_strength=2.2, alpha=0.85),
    "M_SlashCore":  create_voxel_material("M_SlashCore",  (0.95, 0.25, 0.20, 1.0),
                                          emission_color=(0.95, 0.25, 0.20, 1.0), emission_strength=2.8),
}

# ==============================================================================
# 4. PROCEDURAL VOXEL GENERATION
# ==============================================================================
# Voxel database: (vx, vy, vz) -> {"mat": str, "bone": str}
voxels = {}

def set_v(vx, vy, vz, mat, bone):
    voxels[(vx, vy, vz)] = {"mat": mat, "bone": bone}

def fill_box(x_range, y_range, z_range, mat, bone):
    for x in range(x_range[0], x_range[1] + 1):
        for y in range(y_range[0], y_range[1] + 1):
            for z in range(z_range[0], z_range[1] + 1):
                set_v(x, y, z, mat, bone)

print("[1/5] Building procedural voxel geometry...")

# --- 4.1 PELVIS & TATTERED LOINCLOTH (Hips) ---
# Gaunt pelvic bone core (vz = 13..15)
fill_box((-1, 0), (0, 1), (13, 15), "M_DecayedBone", "Hips")  # Sacrum & spine base
# Iliac crests & gaunt hips
fill_box((-3, -2), (0, 1), (14, 15), "M_DecayedBone", "Hips")
fill_box((1, 2), (0, 1), (14, 15), "M_DecayedBone", "Hips")
fill_box((-2, 1), (1, 2), (13, 15), "M_FleshDark", "Hips")  # Gaunt rear flesh
# Tattered loincloth (vz = 11..15)
fill_box((-3, 2), (-2, -2), (15, 15), "M_ClothTattered", "Hips")  # Waist belt
fill_box((-2, 1), (-2, -2), (13, 14), "M_ClothTattered", "Hips")  # Front flap
fill_box((-1, 1), (-2, -2), (12, 12), "M_ClothTattered", "Hips")  # Ragged edge
set_v(0, -2, 11, "M_ClothTattered", "Hips")  # Shredded hanging strip
fill_box((-2, 1), (2, 2), (13, 14), "M_ClothTattered", "Hips")  # Back flap
# Blood stains on cloth
set_v(-1, -2, 13, "M_BloodDark", "Hips")
set_v(0, -2, 12, "M_BloodFresh", "Hips")

# --- 4.2 LUMBAR SPINE & SUNKEN ABDOMINAL CAVITY (Spine) ---
# Flanks (x < -1 and x > 0) are completely hollow!
fill_box((-1, 0), (0, 1), (16, 17), "M_DecayedBone", "Spine")  # Spine column
# Hunched vertebrae protruding backwards (+1 relief)
set_v(-1, 2, 16, "M_BoneHighlight", "Spine")
set_v(0, 2, 16, "M_BoneHighlight", "Spine")
set_v(-1, 2, 17, "M_BoneHighlight", "Spine")
set_v(0, 2, 17, "M_BoneHighlight", "Spine")
# Rotting dark visceral sinew on anterior spine
set_v(-1, -1, 16, "M_FleshDark", "Spine")
set_v(0, -1, 16, "M_BloodDark", "Spine")
set_v(-1, -1, 17, "M_FleshDark", "Spine")
set_v(0, -1, 17, "M_FleshDark", "Spine")

# --- 4.3 CHEST & PROTRUDING STEPPED RIBCAGE (Chest) ---
# Thoracic spine column (vz = 18..24)
fill_box((-1, 0), (1, 2), (18, 24), "M_DecayedBone", "Chest")
# Protruding hunched dorsal vertebrae down the back
for z in (19, 21, 23):
    set_v(-1, 3, z, "M_BoneHighlight", "Chest")
    set_v(0, 3, z, "M_BoneHighlight", "Chest")
# Sunken dark inner cavity core
fill_box((-2, 1), (0, 1), (18, 24), "M_BloodDark", "Chest")

# Ribcage Stepped Relief (+1 to +2 voxels stepped relief on front & flanks)
# Rib Level 1 (vz = 18):
fill_box((-3, -2), (0, 1), (18, 18), "M_DecayedBone", "Chest")  # Right flank
fill_box((1, 2), (0, 1), (18, 18), "M_FleshGreen", "Chest")    # Left flank
fill_box((-3, -1), (-2, -2), (18, 18), "M_DecayedBone", "Chest") # Right anterior
fill_box((0, 2), (-2, -2), (18, 18), "M_FleshGreen", "Chest")   # Left anterior

# Rib Level 2 (vz = 20) with BROKEN PROTRUDING RIB on Right:
fill_box((-4, -3), (0, 1), (20, 20), "M_DecayedBone", "Chest")  # Protruding right flank
fill_box((1, 3), (0, 1), (20, 20), "M_FleshDark", "Chest")     # Left flank
fill_box((-3, -1), (-2, -2), (20, 20), "M_DecayedBone", "Chest")
fill_box((0, 2), (-2, -2), (20, 20), "M_FleshGreen", "Chest")
# Protruding broken rib with blood droplet:
set_v(-3, -3, 20, "M_BoneHighlight", "Chest")
set_v(-3, -4, 20, "M_BoneHighlight", "Chest") # Broken needle tip!
set_v(-3, -4, 19, "M_BloodFresh", "Chest")    # Dripping blood droplet

# Rib Level 3 (vz = 22):
fill_box((-4, -3), (0, 1), (22, 22), "M_DecayedBone", "Chest")
fill_box((1, 3), (0, 1), (22, 22), "M_FleshGreen", "Chest")
fill_box((-3, 2), (-2, -2), (22, 22), "M_DecayedBone", "Chest")
# Stepped sternum plate forward (+1 relief)
fill_box((-2, 1), (-3, -3), (22, 22), "M_BoneHighlight", "Chest")

# Clavicle & Upper Shoulder Base (vz = 24):
fill_box((-3, -1), (-2, -2), (24, 24), "M_DecayedBone", "Chest")
fill_box((0, 2), (-2, -2), (24, 24), "M_FleshGreen", "Chest")
set_v(-4, -1, 24, "M_DecayedBone", "Chest")  # Right shoulder socket base
set_v(3, -1, 24, "M_FleshDark", "Chest")    # Left shoulder socket base

# --- 4.4 NECK (Neck) ---
# Thin hunched 2x2 strut (vz = 25..26)
set_v(-1, -1, 25, "M_DecayedBone", "Neck")
set_v(0, -1, 25, "M_FleshDark", "Neck")
set_v(-1, 0, 25, "M_DecayedBone", "Neck")
set_v(0, 0, 25, "M_FleshDark", "Neck")

set_v(-1, -1, 26, "M_DecayedBone", "Neck")
set_v(0, -1, 26, "M_FleshDark", "Neck")
set_v(-1, 0, 26, "M_DecayedBone", "Neck")
set_v(0, 0, 26, "M_FleshDark", "Neck")
set_v(-1, 1, 26, "M_BoneHighlight", "Neck") # Cervical vertebra
set_v(0, 1, 26, "M_BoneHighlight", "Neck")

# --- 4.5 HEAD & CRANIUM (Head) ---
# Base cranium volume (vz = 29..34)
fill_box((-4, 3), (-3, 3), (29, 33), "M_FleshDark", "Head")

# Sunken hollow cheeks (vz = 27..29)
fill_box((-2, 1), (-3, 1), (27, 28), "M_FleshDark", "Head")
fill_box((-3, -2), (-3, 0), (28, 29), "M_DecayedBone", "Head") # Right gaunt cheek
fill_box((1, 2), (-3, 0), (28, 29), "M_FleshGreen", "Head")   # Left gaunt cheek

# Heavy brow ridge (vz = 32..33, y = -4)
fill_box((-4, -1), (-4, -4), (32, 33), "M_DecayedBone", "Head")
fill_box((0, 3), (-4, -4), (32, 33), "M_FleshDark", "Head")

# Sunken Eye Sockets (vz = 30..31, y = -4):
# Right eye socket: Empty necrotic hollow void
fill_box((-3, -2), (-4, -3), (30, 31), "M_BloodDark", "Head")
# Left eye socket: BURNING NECROTIC BLOODLUST GLOWING EYE
set_v(1, -4, 31, "M_EyeGlow", "Head")
set_v(2, -4, 31, "M_EyeGlow", "Head")
set_v(1, -4, 30, "M_EyeGlow", "Head")
set_v(2, -4, 30, "M_BloodDark", "Head")

# Gaping Cranium Fracture (Top-Right broken open, vz = 34..36):
# Left scalp is intact rotting flesh:
fill_box((0, 3), (-2, 2), (34, 35), "M_FleshGreen", "Head")
fill_box((0, 2), (-1, 1), (36, 36), "M_FleshGreen", "Head")
# Right side skull is broken open:
set_v(-1, -2, 35, "M_BoneHighlight", "Head") # Sharp fracture edges
set_v(-1, 0, 35, "M_BoneHighlight", "Head")
set_v(-1, 2, 35, "M_BoneHighlight", "Head")
set_v(-3, 2, 34, "M_DecayedBone", "Head")
# Exposed dark coagulated brain cavity:
fill_box((-3, -2), (-1, 1), (34, 34), "M_BloodDark", "Head")

# Straggly rotting hair strands hanging down:
fill_box((4, 4), (0, 0), (28, 33), "M_ClothTattered", "Head")   # Left flank strand
fill_box((3, 3), (-4, -4), (28, 30), "M_ClothTattered", "Head") # Forehead strand
fill_box((1, 1), (4, 4), (27, 33), "M_ClothTattered", "Head")   # Back strand

# Dangling unhinged lower jaw & needle-like fangs (vz = 26..28):
fill_box((-3, 1), (-4, -1), (26, 27), "M_DecayedBone", "Head")  # Jaw bone
fill_box((-3, 1), (-5, -5), (27, 27), "M_DecayedBone", "Head")  # Extended chin (+1 relief)
# Needle-like fangs / teeth (+1 relief):
set_v(-3, -5, 28, "M_BoneHighlight", "Head")
set_v(-2, -5, 28, "M_BoneHighlight", "Head")
set_v(0, -5, 28, "M_BoneHighlight", "Head")
set_v(1, -5, 28, "M_BoneHighlight", "Head")
# Upper teeth pointing down:
set_v(-3, -5, 29, "M_BoneHighlight", "Head")
set_v(-1, -5, 29, "M_BoneHighlight", "Head")
set_v(1, -5, 29, "M_BoneHighlight", "Head")
# Dark oral cavity:
fill_box((-2, 0), (-4, -2), (27, 28), "M_BloodDark", "Head")

# --- 4.6 LEFT ARM (Desiccated Gangrene Flesh + Tattered Wraps) ---
# Shoulder.L (detached joint)
fill_box((3, 4), (-1, 0), (24, 24), "M_FleshDark", "Shoulder.L")

# UpperArm.L (vz = 19..23, 2x2 strut)
fill_box((4, 5), (-1, 0), (19, 23), "M_FleshGreen", "UpperArm.L")
set_v(4, -1, 21, "M_FleshDark", "UpperArm.L")
set_v(5, 0, 20, "M_FleshDark", "UpperArm.L")

# Forearm.L (vz = 14..18, 2x2 strut)
fill_box((4, 5), (-1, 0), (16, 18), "M_FleshGreen", "Forearm.L")
# Tattered wrist wraps (vz = 14..15)
fill_box((4, 5), (-1, 0), (14, 15), "M_ClothTattered", "Forearm.L")
set_v(6, 0, 14, "M_ClothTattered", "Forearm.L") # Wrap relief tab

# 1-voxel Detachment Gap at vz = 13 (Empty!)

# Hand.L (vz = 9..12, chunky 3x3 floating palm)
fill_box((4, 6), (-2, 0), (10, 12), "M_FleshDark", "Hand.L")
fill_box((4, 5), (-1, 0), (9, 9), "M_FleshGreen", "Hand.L")
# Long needle claws / talons (+2 voxels forward):
fill_box((4, 4), (-4, -3), (11, 11), "M_DecayedBone", "Hand.L")
set_v(4, -4, 11, "M_BloodFresh", "Hand.L")
fill_box((5, 5), (-5, -3), (10, 10), "M_DecayedBone", "Hand.L") # Longest claw
set_v(5, -5, 10, "M_BloodFresh", "Hand.L")
fill_box((6, 6), (-4, -3), (11, 11), "M_DecayedBone", "Hand.L")
set_v(6, -4, 11, "M_BloodFresh", "Hand.L")
set_v(4, -3, 9, "M_BoneHighlight", "Hand.L") # Thumb talon

# --- 4.7 RIGHT ARM (Bare Weathered Skeletal Bone) ---
# Shoulder.R (detached bone joint)
fill_box((-5, -4), (-1, 0), (24, 24), "M_DecayedBone", "Shoulder.R")

# UpperArm.R (vz = 19..23, 2x2 bare bone strut)
fill_box((-6, -5), (-1, 0), (19, 23), "M_DecayedBone", "UpperArm.R")
set_v(-5, -1, 21, "M_BloodDark", "UpperArm.R") # Blood drip on bone

# Forearm.R (vz = 14..18, skeletal strut with split notched radius/ulna)
fill_box((-6, -5), (-1, 0), (14, 18), "M_DecayedBone", "Forearm.R")
# Notched split between radius & ulna:
if (-5, -1, 16) in voxels: del voxels[(-5, -1, 16)]
set_v(-6, -1, 14, "M_BloodFresh", "Forearm.R")

# 1-voxel Detachment Gap at vz = 13 (Empty!)

# Hand.R (vz = 9..12, chunky skeletal carpal block)
fill_box((-7, -5), (-2, 0), (10, 12), "M_DecayedBone", "Hand.R")
fill_box((-6, -5), (-1, 0), (9, 9), "M_DecayedBone", "Hand.R")
# Splayed sharp needle bone talons:
fill_box((-7, -7), (-4, -3), (11, 11), "M_BoneHighlight", "Hand.R")
set_v(-7, -4, 11, "M_BloodFresh", "Hand.R")
fill_box((-6, -6), (-5, -3), (10, 10), "M_BoneHighlight", "Hand.R") # Longest talon
set_v(-6, -5, 10, "M_BloodFresh", "Hand.R")
fill_box((-5, -5), (-4, -3), (11, 11), "M_BoneHighlight", "Hand.R")
set_v(-5, -4, 11, "M_BloodFresh", "Hand.R")
set_v(-5, -3, 9, "M_BoneHighlight", "Hand.R") # Inner talon
# Dripping blood droplets falling from claws:
set_v(-6, -5, 8, "M_BloodFresh", "Hand.R")
set_v(-6, -5, 7, "M_BloodFresh", "Hand.R")

# --- 4.8 LEFT LEG (Gaunt Tattered Boot) ---
# UpperLeg.L (vz = 9..12, 2x2 thigh strut)
fill_box((1, 2), (-1, 0), (9, 12), "M_FleshGreen", "UpperLeg.L")
set_v(1, -1, 12, "M_ClothTattered", "UpperLeg.L") # Ragged thigh wrap

# LowerLeg.L (vz = 5..8, 2x2 calf strut)
fill_box((1, 2), (-1, 0), (5, 8), "M_FleshDark", "LowerLeg.L")

# 1-voxel Ankle Gap at vz = 4 (Empty!)

# Foot.L (vz = 0..3, gaunt tattered boot)
fill_box((1, 3), (-3, 1), (0, 3), "M_ClothTattered", "Foot.L")
set_v(2, -3, 1, "M_FleshDark", "Foot.L") # Exposed toe poking through tear!

# --- 4.9 RIGHT LEG (Bare Skeletal Leg & Bone Talons) ---
# UpperLeg.R (vz = 9..12, 2x2 bare bone thigh)
fill_box((-3, -2), (-1, 0), (9, 12), "M_DecayedBone", "UpperLeg.R")

# LowerLeg.R (vz = 5..8, 2x2 bare bone calf)
fill_box((-3, -2), (-1, 0), (5, 8), "M_DecayedBone", "LowerLeg.R")
set_v(-2, -1, 8, "M_BoneHighlight", "LowerLeg.R") # Patella bone cap

# 1-voxel Ankle Gap at vz = 4 (Empty!)

# Foot.R (vz = 0..2, bare skeletal foot with splayed talons)
fill_box((-3, -1), (-1, 1), (0, 2), "M_DecayedBone", "Foot.R") # Heel & tarsals
# Splayed sharp skeletal talons extending forward:
fill_box((-3, -3), (-3, -2), (0, 0), "M_BoneHighlight", "Foot.R")
fill_box((-2, -2), (-4, -2), (0, 0), "M_BoneHighlight", "Foot.R") # Long middle talon
fill_box((-1, -1), (-3, -2), (0, 0), "M_BoneHighlight", "Foot.R")
set_v(-2, -4, 0, "M_BloodDark", "Foot.R") # Blood crust on talon tip

# --- 4.10 CLAW SLASH VFX RIBBONS (Geometric curved voxel ribbons) ---
# Left Claw Slash Ribbon (ClawTrail.L)
left_slash = [
    ((4, -5, 10), "M_SlashCore"),
    ((5, -6, 9),  "M_SlashCore"),
    ((5, -7, 8),  "M_SlashCore"),
    ((4, -8, 6),  "M_SlashCore"),
    ((3, -8, 5),  "M_SlashCore"),
    ((2, -7, 4),  "M_SlashCore"),
    # Outer trail
    ((5, -5, 11), "M_SlashTrail"),
    ((6, -6, 10), "M_SlashTrail"),
    ((6, -7, 9),  "M_SlashTrail"),
    ((5, -8, 7),  "M_SlashTrail"),
    ((4, -9, 6),  "M_SlashTrail"),
    ((3, -9, 5),  "M_SlashTrail"),
    ((2, -8, 4),  "M_SlashTrail"),
]
for pt, mat in left_slash:
    set_v(pt[0], pt[1], pt[2], mat, "ClawTrail.L")

# Right Claw Slash Ribbon (ClawTrail.R)
right_slash = [
    ((-5, -5, 10), "M_SlashCore"),
    ((-6, -6, 9),  "M_SlashCore"),
    ((-6, -7, 8),  "M_SlashCore"),
    ((-5, -8, 6),  "M_SlashCore"),
    ((-4, -8, 5),  "M_SlashCore"),
    ((-3, -7, 4),  "M_SlashCore"),
    # Outer trail
    ((-6, -5, 11), "M_SlashTrail"),
    ((-7, -6, 10), "M_SlashTrail"),
    ((-7, -7, 9),  "M_SlashTrail"),
    ((-6, -8, 7),  "M_SlashTrail"),
    ((-5, -9, 6),  "M_SlashTrail"),
    ((-4, -9, 5),  "M_SlashTrail"),
    ((-3, -8, 4),  "M_SlashTrail"),
]
for pt, mat in right_slash:
    set_v(pt[0], pt[1], pt[2], mat, "ClawTrail.R")

print(f"Total active voxels populated: {len(voxels)}")

# ==============================================================================
# 5. RIGGING & ARMATURE (Zombie_Armature)
# ==============================================================================
print("[2/5] Constructing Zombie_Armature with standard equipment sockets...")

arm_data = bpy.data.armatures.new("Zombie_Armature_Data")
arm_obj = bpy.data.objects.new("Zombie_Armature", arm_data)
scene.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj

bpy.ops.object.mode_set(mode='EDIT')
edit_bones = arm_data.edit_bones

def add_ebone(name, head, tail, parent_name=None):
    b = edit_bones.new(name)
    b.head = Vector(head) * VOXEL_SIZE
    b.tail = Vector(tail) * VOXEL_SIZE
    if parent_name and parent_name in edit_bones:
        b.parent = edit_bones[parent_name]
    return b

# Core Spine Hierarchy
add_ebone("Root",  (0, 0, 0),  (0, 0, 4))
add_ebone("Hips",  (0, 0, 13), (0, 0, 16), "Root")
add_ebone("Spine", (0, 0, 16), (0, 0, 18), "Hips")
add_ebone("Chest", (0, 0, 18), (0, 0, 25), "Spine")
add_ebone("Neck",  (0, 0, 25), (0, 0, 27), "Chest")
add_ebone("Head",  (0, 0, 27), (0, 0, 37), "Neck")

# Left Arm Hierarchy (Facing -Y: Left is +X)
add_ebone("Shoulder.L", (3, 0, 24),        (4.5, 0, 23.5),   "Chest")
add_ebone("UpperArm.L", (4.5, -0.5, 23.5), (4.5, -0.5, 18.5), "Shoulder.L")
add_ebone("Forearm.L",  (4.5, -0.5, 18.5), (4.5, -0.5, 13.5), "UpperArm.L")
add_ebone("Hand.L",     (5, -1, 12.5),     (5, -1, 8),       "Forearm.L")

# Right Arm Hierarchy (Facing -Y: Right is -X)
add_ebone("Shoulder.R", (-3, 0, 24),        (-4.5, 0, 23.5),   "Chest")
add_ebone("UpperArm.R", (-4.5, -0.5, 23.5), (-4.5, -0.5, 18.5), "Shoulder.R")
add_ebone("Forearm.R",  (-4.5, -0.5, 18.5), (-4.5, -0.5, 13.5), "UpperArm.R")
add_ebone("Hand.R",     (-5.5, -1, 12.5),   (-5.5, -1, 8),       "Forearm.R")

# Legs Hierarchy
add_ebone("UpperLeg.L", (2, -0.5, 13),  (2, -0.5, 8.5),   "Hips")
add_ebone("LowerLeg.L", (2, -0.5, 8.5), (2, -0.5, 4.5),   "UpperLeg.L")
add_ebone("Foot.L",     (2, -0.5, 3.5), (2, -2.5, 0),     "LowerLeg.L")

add_ebone("UpperLeg.R", (-2, -0.5, 13),  (-2, -0.5, 8.5),   "Hips")
add_ebone("LowerLeg.R", (-2, -0.5, 8.5), (-2, -0.5, 4.5),   "UpperLeg.R")
add_ebone("Foot.R",     (-2, -0.5, 3.5), (-2, -2.5, 0),     "LowerLeg.R")

# Claw Slash VFX Bones
add_ebone("ClawTrail.L", (4, -6, 9), (3, -8, 6), "Hand.L")
add_ebone("ClawTrail.R", (-5, -6, 9), (-4, -8, 6), "Hand.R")

# Modular Equipment Sockets
add_ebone("Socket_Hand_R", (-5.5, -1, 10), (-5.5, -2, 10), "Hand.R")
add_ebone("Socket_Hand_L", (5, -1, 10),    (5, -2, 10),    "Hand.L")
add_ebone("Socket_Head",   (0, 0, 36.5),   (0, 0, 38),     "Head")
add_ebone("Socket_Back",   (0, 2.5, 22),   (0, 3.5, 22),   "Chest")

bpy.ops.object.mode_set(mode='OBJECT')

# ==============================================================================
# 6. WATERTIGHT BOUNDARY QUAD MESHING & PLANAR DISSOLVE
# ==============================================================================
print("[3/5] Generating boundary quads & planar dissolve optimization...")

mesh = bpy.data.meshes.new("SkinnyZombie_Mesh")
mesh_obj = bpy.data.objects.new("SkinnyZombie", mesh)
scene.collection.objects.link(mesh_obj)

# Link all materials to mesh
mat_index_map = {}
for i, (m_name, m_obj) in enumerate(materials.items()):
    mesh.materials.append(m_obj)
    mat_index_map[m_name] = i

# Create vertex groups for all bones on the mesh object
voxels_by_bone = {}
for coord, vdata in voxels.items():
    b_name = vdata["bone"]
    voxels_by_bone.setdefault(b_name, {})[coord] = vdata

vg_map = {}
for b_name in voxels_by_bone.keys():
    vg = mesh_obj.vertex_groups.new(name=b_name)
    vg_map[b_name] = vg.index

# Ensure socket groups also exist
for eb in arm_data.bones:
    if eb.name not in mesh_obj.vertex_groups:
        mesh_obj.vertex_groups.new(name=eb.name)

# Boundary Face Offsets & CCW Quad Vertex Indices
# 0:(-,-,-), 1:(+,-,-), 2:(+,+,-), 3:(-,+,-), 4:(-,-,+), 5:(+,-,+), 6:(+,+,+), 7:(-,+,+)
FACE_DEFS = [
    ((-1, 0, 0), (0, 4, 7, 3)), # -X
    ((1, 0, 0),  (1, 2, 6, 5)), # +X
    ((0, -1, 0), (0, 1, 5, 4)), # -Y (Front)
    ((0, 1, 0),  (3, 7, 6, 2)), # +Y (Back)
    ((0, 0, -1), (0, 3, 2, 1)), # -Z (Bottom)
    ((0, 0, 1),  (4, 5, 6, 7)), # +Z (Top)
]

CORNER_OFFSETS = [
    Vector((-0.5, -0.5, -0.5)),
    Vector((0.5, -0.5, -0.5)),
    Vector((0.5, 0.5, -0.5)),
    Vector((-0.5, 0.5, -0.5)),
    Vector((-0.5, -0.5, 0.5)),
    Vector((0.5, -0.5, 0.5)),
    Vector((0.5, 0.5, 0.5)),
    Vector((-0.5, 0.5, 0.5)),
]

bm = bmesh.new()
dvert_lay = bm.verts.layers.deform.verify()

for b_name, b_voxels in voxels_by_bone.items():
    bone_vg_idx = vg_map[b_name]
    # Dedicated vertex cache per bone to prevent cross-bone vertex welding
    v_cache = {}
    bone_verts = []
    
    for (vx, vy, vz), vdata in b_voxels.items():
        mat_name = vdata["mat"]
        mat_idx = mat_index_map.get(mat_name, 0)
        center = Vector((vx, vy, vz)) * VOXEL_SIZE
        
        for n_offset, c_indices in FACE_DEFS:
            nx = vx + n_offset[0]
            ny = vy + n_offset[1]
            nz = vz + n_offset[2]
            neighbor = (nx, ny, nz)
            
            # Boundary quad condition: neighbor is empty OR neighbor belongs to different bone
            if neighbor not in voxels or voxels[neighbor]["bone"] != b_name:
                face_verts = []
                for ci in c_indices:
                    pt_key = (vx + CORNER_OFFSETS[ci].x, vy + CORNER_OFFSETS[ci].y, vz + CORNER_OFFSETS[ci].z)
                    if pt_key not in v_cache:
                        pt_pos = center + CORNER_OFFSETS[ci] * VOXEL_SIZE
                        bm_vert = bm.verts.new(pt_pos)
                        bm_vert[dvert_lay][bone_vg_idx] = 1.0  # Strict 1.0 rigid weight
                        v_cache[pt_key] = bm_vert
                        bone_verts.append(bm_vert)
                    face_verts.append(v_cache[pt_key])
                
                try:
                    f = bm.faces.new(face_verts)
                    f.material_index = mat_idx
                    f.smooth = False
                except ValueError:
                    pass

    # Weld co-incident vertices strictly WITHIN this bone group
    bmesh.ops.remove_doubles(bm, verts=bone_verts, dist=0.0001)

bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
print(f"Pre-dissolve polycount: {len(bm.faces)} faces, {len(bm.verts)} vertices")

bm.to_mesh(mesh)
bm.free()

# Planar Dissolve Optimization with strict material boundary delimiter
bpy.context.view_layer.objects.active = mesh_obj
mesh_obj.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.dissolve_limited(angle_limit=0.0001, delimit={'MATERIAL'})
bpy.ops.mesh.tris_convert_to_quads()
bpy.ops.object.mode_set(mode='OBJECT')

print(f"Post-dissolve optimized: {len(mesh.polygons)} polygons, {len(mesh.vertices)} vertices")

# Ensure flat shading across all polygons
for p in mesh.polygons:
    p.use_smooth = False

# ==============================================================================
# 7. ARMATURE MODIFIER BINDING
# ==============================================================================
print("[4/5] Binding armature modifier...")

arm_mod = mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
arm_mod.object = arm_obj
mesh_obj.parent = arm_obj

# ==============================================================================
# 8. LIGHTING, CAMERA FRAMING & HIGH-FIDELITY CYCLES AGX PREVIEW
# ==============================================================================
print("[5/5] Setting up studio lighting & evaluated camera framing...")

# World Background: Dark Slate Void
scene.world = bpy.data.worlds.new("World_Void")
scene.world.use_nodes = True
bg_node = scene.world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs["Color"].default_value = (0.015, 0.020, 0.028, 1.0)
    bg_node.inputs["Strength"].default_value = 1.0

# 3-Point Studio Lighting + Rim Lights
def add_light(name, light_type, location, energy, color):
    ldata = bpy.data.lights.new(name=name, type=light_type)
    ldata.energy = energy
    ldata.color = color
    lobj = bpy.data.objects.new(name=name, object_data=ldata)
    lobj.location = location
    scene.collection.objects.link(lobj)
    return lobj

# Key Light (Warm sunlight from front-right)
add_light("Light_Key", 'POINT', (1.2, -1.8, 1.6), 25.0, (1.0, 0.95, 0.90))
# Fill Light (Cool shadow fill from front-left)
add_light("Light_Fill", 'POINT', (-1.4, -1.5, 1.2), 12.0, (0.45, 0.60, 0.75))
# Top/Back Rim Light (Catches spine vertebrae, skull fracture, hair)
add_light("Light_RimTop", 'POINT', (0.5, 1.8, 2.0), 30.0, (0.95, 0.95, 1.0))
# Crimson Gore Rim Light (Behind bare skeletal right arm & talons)
add_light("Light_RimBlood", 'POINT', (-1.5, 0.8, 0.8), 18.0, (0.95, 0.05, 0.05))

# Camera Auto-Framing via Evaluated Depsgraph
scene.render.engine = 'CYCLES'
scene.cycles.samples = 96
scene.cycles.use_denoising = True
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - High Contrast'

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
    center = Vector((0, 0, 0.25))
    span = 0.6

# Static Tracking Target
cam_target = bpy.data.objects.new("CamTarget", None)
scene.collection.objects.link(cam_target)
cam_target.location = center

# Static Camera Object
cam_data = bpy.data.cameras.new("HeroCamera")
cam_obj = bpy.data.objects.new("HeroCamera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Elevated 3/4 Front Isometric Perspective (Elevated 35 deg, viewing front -Y)
fov_rad = cam_data.angle
dist = (span * 0.5) / math.tan(fov_rad * 0.5) * 1.32
cam_obj.location = center + Vector((dist * 0.45, -dist * 0.82, dist * 0.52))

tt = cam_obj.constraints.new('TRACK_TO')
tt.target = cam_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

# Render Beauty Shot
scene.render.filepath = PREVIEW_PATH
print(f"Rendering preview shot to: {PREVIEW_PATH}")
bpy.ops.render.render(write_still=True)

# Save .blend Scene
print(f"Saving Blender source scene to: {BLEND_PATH}")
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)

print("[COMPLETE] Skinny Zombie procedural model authoring finished successfully!")
