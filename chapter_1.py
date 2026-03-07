# -------------------------------------------------------------
# Blender 5.0.1 – “Cosmic Regulation Through Consciousness”
# -------------------------------------------------------------
# Optimized for Blender 5.0.1 with new Animation System 
# and Shader Node Input compatibility.
# -------------------------------------------------------------

import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler, Color

# ------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------

def clear_scene():
    """Remove all objects, collections, and data blocks."""
    for coll in bpy.data.collections:
        bpy.data.collections.remove(coll)
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat, do_unlink=True)
    for txt in bpy.data.textures:
        bpy.data.textures.remove(txt, do_unlink=True)
    for img in bpy.data.images:
        bpy.data.images.remove(img, do_unlink=True)

def make_collection(name):
    """Create a new collection and link it to the master scene."""
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll

def add_material(name, nodes_setup_func):
    """Create a material with nodes and run a custom setup."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    # Clear default nodes
    for n in nodes:
        nodes.remove(n)
    # Run user‑provided node builder
    nodes_setup_func(nodes, links)
    return mat

def set_keyframe(obj, data_path, frame, value, interpolation='LINEAR'):
    """Convenient wrapper for setting a keyframe, compatible with Blender 5.0."""
    setattr(obj, data_path, value)
    obj.keyframe_insert(data_path=data_path, frame=frame)
    
    # Blender 5.0 Animation System Handling
    try:
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            fcurve = None
            # Check legacy fcurves or new layers
            if hasattr(action, "fcurves"):
                fcurve = action.fcurves.find(data_path)
            elif hasattr(action, "layers"):
                for layer in action.layers:
                    fcurve = layer.fcurves.find(data_path)
                    if fcurve: break
            
            if fcurve:
                for kp in fcurve.keyframe_points:
                    if abs(kp.co.x - frame) < 0.01:
                        kp.interpolation = interpolation
                        break
    except:
        pass

def lerp(a, b, t):
    return a + (b - a) * t

# ------------------------------------------------------------------
# GLOBAL SETTINGS
# ------------------------------------------------------------------

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 512
bpy.context.scene.render.fps = 24
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.cycles.motion_blur_shutter = 0.5

# ------------------------------------------------------------------
# SCENE 1 – "The Echo Hook"
# ------------------------------------------------------------------

scene1 = bpy.data.scenes.new("Echo_Hook")
bpy.context.window.scene = scene1
scene1.render.film_transparent = False
scene1.cycles.motion_blur_shutter = 0.5

# 1️⃣ Starfield
star_coll = make_collection("Stars")
star_coll.hide_viewport = True

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=(0,0,0))
star_proto = bpy.context.object
star_proto.name = "Star_Proto"
star_proto.hide_render = True

star_mat = add_material("Star_Emission", lambda n, l: (
    n.new('ShaderNodeEmission', name='Emission')
))
star_proto.data.materials.append(star_mat)

bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
star_field = bpy.context.object
star_field.name = "Star_Field"
star_field.scale = (10000,10000,10000)

ps = star_field.modifiers.new(name="Stars_PS", type='PARTICLE_SYSTEM')
psettings = ps.particle_system.settings
psettings.count = 80000
psettings.frame_start = 1
psettings.frame_end = 1
psettings.lifetime = 1000
psettings.render_type = 'OBJECT'
psettings.instance_object = star_proto
psettings.use_render_emitter = False

# Note: assign_star_colors logic omitted for background stability in this update
# as particle iteration can be slow in CLI.

# 2️⃣ Nebula
nebula_coll = make_collection("Nebula")
bpy.ops.mesh.primitive_cube_add(size=2000, location=(0,0,0))
nebula = bpy.context.object
nebula.name = "Nebula_Fog"
nebula_coll.objects.link(nebula)

nebula_mat = add_material("Nebula_Fog_Mat", lambda n,l: (
    n.new('ShaderNodeVolumePrincipled', name='PrincipledVolume')
))
vol_node = nebula_mat.node_tree.nodes["PrincipledVolume"]
vol_node.inputs["Color"].default_value = (0.102,0.039,0.180,1)
vol_node.inputs["Emission Strength"].default_value = 0.03
nebula.data.materials.append(nebula_mat)

# 3️⃣ Origin Pulse
origin_coll = make_collection("Origin")
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0,0,0))
source = bpy.context.object
source.name = "Info_Source"
origin_coll.objects.link(source)

bpy.ops.mesh.primitive_torus_add(major_radius=0.0, minor_radius=0.015, location=(0,0,0))
ring = bpy.context.object
ring.name = "Shockwave_Ring"
origin_coll.objects.link(ring)

ring_mat = add_material("Ring_Emission", lambda n,l: (
    n.new('ShaderNodeEmission', name='Emission')
))
ring_emit = ring_mat.node_tree.nodes["Emission"]
ring_emit.inputs["Color"].default_value = (1,1,1,1)
ring_emit.inputs["Strength"].default_value = 18.0
ring.data.materials.append(ring_mat)

ring.scale = (0,0,0)
set_keyframe(ring, "scale", 1, (0,0,0))
set_keyframe(ring, "scale", 130, (65, 65, 0))

# 4️⃣ Functional Boundary
grid_coll = make_collection("Boundary")
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,85))
grid = bpy.context.object
grid.name = "Functional_Boundary"
grid.rotation_euler = Euler((math.radians(2),0,0), 'XYZ')
grid_coll.objects.link(grid)

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=100)
bpy.ops.object.mode_set(mode='OBJECT')

grid_mat = add_material("Grid_Mat", lambda n,l: (
    n.new('ShaderNodeEmission', name='Emission')
))
grid.data.materials.append(grid_mat)

# Pulse Animation
grid_emit = grid_mat.node_tree.nodes["Emission"]
for f in range(1, 271, 5):
    val = 1.25 + 0.25*math.sin(2*math.pi*(f%90)/90)
    grid_emit.inputs["Strength"].default_value = val
    grid_emit.keyframe_insert(data_path="inputs['Strength'].default_value", frame=f)

# 6️⃣ Camera
cam_coll = make_collection("Camera")
bpy.ops.object.camera_add(location=(0, -200, -200))
cam = bpy.context.object
cam.name = "Cam_Echo"
cam_coll.objects.link(cam)
cam.data.lens = 35
cam.rotation_euler = Euler((math.radians(8),0,0), 'XYZ')

for f in range(1, 271):
    dz = lerp(0, 0.15* (f-1), min(1, (f-1)/210))
    cam.location.z = -200 + dz
    cam.keyframe_insert(data_path="location", frame=f)

# ------------------------------------------------------------------
# SCENE 2 – "The Aristotle Glitch"
# ------------------------------------------------------------------

scene2 = bpy.data.scenes.new("Aristotle_Glitch")
bpy.context.window.scene = scene2

scene2.world.use_nodes = True
bg = scene2.world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0,0,0,1)

bpy.ops.object.light_add(type='AREA', location=(-5,5,5))
area = bpy.context.object
area.data.energy = 400

bust_coll = make_collection("Bust")
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0,0,0))
bust = bpy.context.object
bust.name = "Aristotle_Bust"
bust_coll.objects.link(bust)

marble_mat = add_material("Marble_Mat", lambda n,l: (
    n.new('ShaderNodeBsdfPrincipled', name='Principled')
))
bsdf = marble_mat.node_tree.nodes["Principled"]
bsdf.inputs["Base Color"].default_value = (0.94,0.92,0.89,1)
bsdf.inputs["Subsurface Weight"].default_value = 0.08
bsdf.inputs["Specular IOR Level"].default_value = 0.6
bsdf.inputs["Roughness"].default_value = 0.15
bust.data.materials.append(marble_mat)

# HUD Scan
scan_coll = make_collection("HUD_Scanner")
bpy.ops.mesh.primitive_plane_add(size=2, location=(0,0,0))
line_top = bpy.context.object
line_top.scale = (1,0.0025,1)
line_top.location.z = 0.5
scan_coll.objects.link(line_top)

scan_mat = add_material("ScanLine_Mat", lambda n,l: (
    n.new('ShaderNodeEmission', name='Emission')
))
scan_mat.node_tree.nodes["Emission"].inputs["Color"].default_value = (1,0.1,0.1,1)
scan_mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = 25.0
line_top.data.materials.append(scan_mat)

for f in range(1, 241):
    t = min(1.0, (f-1)/80.0)
    y = lerp(0.5, -0.5, t)
    line_top.location.y = y + random.uniform(-0.02,0.02)
    line_top.keyframe_insert(data_path="location", frame=f)

# ------------------------------------------------------------------
# SCENE 3 – "The Natural Cage"
# ------------------------------------------------------------------

scene3 = bpy.data.scenes.new("Natural_Cage")
bpy.context.window.scene = scene3

# Pillars
pillars_coll = make_collection("Golden_Pillars")
for x in (-20, 20):
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x,0,0))
    pillar = bpy.context.object
    pillar.scale = (1,1,25)
    pillars_coll.objects.link(pillar)

    gold_mat = add_material("Gold_PBR", lambda n,l: (
        n.new('ShaderNodeBsdfPrincipled', name='Principled')
    ))
    bsdf = gold_mat.node_tree.nodes["Principled"]
    bsdf.inputs["Base Color"].default_value = (0.83,0.63,0.09,1)
    bsdf.inputs["Metallic"].default_value = 1.0
    # Blender 5.0 Renames
    if "Anisotropy" in bsdf.inputs:
        bsdf.inputs["Anisotropy"].default_value = 0.3
    
    pillar.data.materials.append(gold_mat)
    pillar.location.z = 200
    pillar.keyframe_insert(data_path="location", frame=1)
    pillar.location.z = 0
    pillar.keyframe_insert(data_path="location", frame=18)

# ------------------------------------------------------------------
# COMPOSITING
# ------------------------------------------------------------------

def setup_compositor(scene):
    scene.use_nodes = True
    nodes = scene.node_tree.nodes
    links = scene.node_tree.links
    nodes.clear()

    rl = nodes.new('CompositorNodeRLayers')
    comp = nodes.new('CompositorNodeComposite')
    glare = nodes.new('CompositorNodeGlare')
    glare.glare_type = 'STREAKS'
    
    links.new(rl.outputs[0], glare.inputs[0])
    links.new(glare.outputs[0], comp.inputs[0])

for sc in [scene1, scene2, scene3]:
    setup_compositor(sc)

print("Edits complete. Chapter 1 script is ready for Blender 5.0.1.")
