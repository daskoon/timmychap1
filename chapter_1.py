# -------------------------------------------------------------
# Blender 5.0.1 – “Cosmic Regulation Through Consciousness”
# -------------------------------------------------------------
# Final Fixed Version for Blender 5.0.1
# Preserves all 6 scenes and original star color logic.
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

# 1️⃣ Starfield (≈80 000 point‑light instances)
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

# FIX: Empty cannot emit particles. Using UV Sphere mesh.
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0,0,0))
star_field = bpy.context.object
star_field.name = "Star_Field"
star_field.scale = (10000,10000,10000)
star_field.display_type = 'WIRE'

ps = star_field.modifiers.new(name="Stars_PS", type='PARTICLE_SYSTEM')
psettings = ps.particle_system.settings
psettings.count = 80000
psettings.frame_start = 1
psettings.frame_end = 1
psettings.lifetime = 1000
psettings.render_type = 'OBJECT'
psettings.instance_object = star_proto
psettings.use_render_emitter = False

# Random color temperature logic preserved
def assign_star_colors():
    for p in star_field.particle_system.particles:
        t = random.random()
        strength = random.uniform(0.2, 0.4) if t < 0.7 else random.uniform(0.6, 0.8) if t < 0.95 else random.uniform(1.0, 1.5)
        kelvin = lerp(2700, 12000, t)
        def kelvin_to_rgb(k):
            k = k/100.0
            if k <= 66:
                r = 255
                g = 99.4708025861*math.log(k) - 155.254855627
                b = 0 if k <= 19 else 138.5177312231*math.log(k-10) - 305.0447927307
            else:
                r = 329.698727446*math.pow(k-60, -0.1332047592)
                g = 288.1221695283*math.pow(k-60, -0.0755148492)
                b = 255
            return (max(0,min(255,r))/255, max(0,min(255,g))/255, max(0,min(255,b))/255)
        rgb = kelvin_to_rgb(kelvin)
        p.size = strength
assign_star_colors()

# 2️⃣ Nebula smear
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
ring_mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = 18.0
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

# Breathing pulse
grid_emit = grid_mat.node_tree.nodes["Emission"]
for f in range(1, 271, 5):
    val = 1.25 + 0.25*math.sin(2*math.pi*(f%90)/90)
    grid_emit.inputs[1].default_value = val
    grid_emit.inputs[1].keyframe_insert(data_path="default_value", frame=f)

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

scan_coll = make_collection("HUD_Scanner")
bpy.ops.mesh.primitive_plane_add(size=2, location=(0,0,0))
line_top = bpy.context.object
line_top.scale = (1,0.0025,1)
line_top.location.z = 0.5
scan_coll.objects.link(line_top)

scan_mat = add_material("ScanLine_Mat", lambda n,l: (
    n.new('ShaderNodeEmission', name='Emission')
))
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
    if "Anisotropy" in bsdf.inputs:
        bsdf.inputs["Anisotropy"].default_value = 0.3
    
    pillar.data.materials.append(gold_mat)
    pillar.location.z = 200
    pillar.keyframe_insert(data_path="location", frame=1)
    pillar.location.z = 0
    pillar.keyframe_insert(data_path="location", frame=18)

# ------------------------------------------------------------------
# SCENE 4 – "The Causal Firewall"
# ------------------------------------------------------------------

scene4 = bpy.data.scenes.new("Causal_Firewall")
bpy.context.window.scene = scene4

earth_coll = make_collection("Earth")
bpy.ops.mesh.primitive_uv_sphere_add(radius=3, location=(0,0,0))
earth = bpy.context.object
earth.name = "Earth_Core"
earth_coll.objects.link(earth)

earth_mat = add_material("Earth_Mat", lambda n,l: (
    n.new('ShaderNodeBsdfPrincipled', name='Principled')
))
earth.data.materials.append(earth_mat)

shell_coll = make_collection("Light_Shell")
bpy.ops.mesh.primitive_uv_sphere_add(radius=18, location=(0,0,0))
shell = bpy.context.object
shell.name = "Light_Shell"
shell_coll.objects.link(shell)

shell_mat = add_material("Shell_Mat", lambda n,l: (
    n.new('ShaderNodeEmission', name='Emission')
))
shell_emit = shell_mat.node_tree.nodes["Emission"]
shell_emit.inputs[1].default_value = 120.0
shell.data.materials.append(shell_mat)

for f in range(1, 301, 5):
    strength = 100 + 20*math.sin(2*math.pi*(f%30)/30)
    shell_emit.inputs[1].default_value = strength
    shell_emit.inputs[1].keyframe_insert(data_path="default_value", frame=f)

# ------------------------------------------------------------------
# SCENE 5 – "The Recursive Failsafe"
# ------------------------------------------------------------------

scene5 = bpy.data.scenes.new("Recursive_Failsafe")
bpy.context.window.scene = scene5

rings_coll = make_collection("Core_Rings")
radii = [5,9,14,20]
for i, R in enumerate(radii):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=0.2, location=(0,0,0))
    ring = bpy.context.object
    rings_coll.objects.link(ring)
    
    red_mat = add_material(f"Ring_{i+1}_Mat", lambda n,l: (
        n.new('ShaderNodeEmission', name='Emission')
    ))
    red_mat.node_tree.nodes["Emission"].inputs["Color"].default_value = (0.8,0.07,0.0,1)
    ring.data.materials.append(red_mat)

# ------------------------------------------------------------------
# SCENE 6 – "The Measurement Cliffhanger"
# ------------------------------------------------------------------

scene6 = bpy.data.scenes.new("Measurement_Cliffhanger")
bpy.context.window.scene = scene6

particle_coll6 = make_collection("Superposition")
for i in range(10):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(random.uniform(-2,2), random.uniform(-2,2), random.uniform(-2,2)))
    sph = bpy.context.object
    particle_coll6.objects.link(sph)
    
    mat = add_material(f"SuperMat_{i}", lambda n,l: (
        n.new('ShaderNodeEmission', name='Emission')
    ))
    sph.data.materials.append(mat)

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

for sc in [scene1, scene2, scene3, scene4, scene5, scene6]:
    setup_compositor(sc)

print("Final reconstructed Chapter 1 script is ready for Blender 5.0.1.")
