# -------------------------------------------------------------
# Blender 5.0.1 – “Cosmic Regulation Through Consciousness”  ## -------------------------------------------------------------
# This script creates six scenes (Echo Hook, Aristotle Glitch, …)
# with the described geometry, materials, animation, and
# compositing setups.  Run it from the Scripting workspace
# (or via `blender --background --python script.py`).
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
    """Convenient wrapper for setting a keyframe."""
    setattr(obj, data_path, value)
    obj.keyframe_insert(data_path=data_path, frame=frame)
    fcurve = obj.animation_data.action.fcurves.find(data_path)
    if fcurve:
        kp = fcurve.keyframe_points[-1]
        kp.interpolation = interpolation

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
bpy.context.scene.cycles.motion_blur_shutter = 0.5   # global, overridden per scene later

# ------------------------------------------------------------------
# SCENE 1 – "The Echo Hook"
# ------------------------------------------------------------------

scene1 = bpy.data.scenes.new("Echo_Hook")
bpy.context.window.scene = scene1
scene1.render.film_transparent = False
scene1.cycles.motion_blur_shutter = 0.5

# 1️⃣ Starfield (≈80 000 point‑light instances)
star_coll = make_collection("Stars")
star_coll.hide_viewport = True   # keep viewport tidy

# Use a tiny sphere as the light instance (more efficient than true point lights)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=(0,0,0))
star_proto = bpy.context.active_object
star_proto.name = "Star_Proto"
star_proto.hide_render = True

# Emission material for stars (color temperature handled later per instance)
star_mat = add_material("Star_Emission", lambda n, l: (
    n.new('ShaderNodeEmission', name='Emission')
))
star_proto.data.materials.append(star_mat)

# Particle system on an empty sphere (radius 10 000)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
star_field = bpy.context.active_object
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
psettings.use_rotation_instance = False
psettings.use_scale_instance = False
psettings.use_dynamic_rotation = False
psettings.use_render_emitter = False
psettings.use_rotations = False
psettings.use_duplicate_particle = True
psettings.use_dead = False
psettings.use_size_deflect = False
psettings.use_modifier_stack = True

# Random color temperature per particle (via particle instance color)
def assign_star_colors():
    for p in star_field.particle_system.particles:
        # Temperature 2700‑12000 K → map to RGB roughly (amber → blue‑white)
        t = random.random()
        if t < 0.7:   # dim range
            strength = random.uniform(0.2,0.4)
        elif t < 0.95: # medium
            strength = random.uniform(0.6,0.8)
        else:         # bright
            strength = random.uniform(1.0,1.5)
        # Simple temperature → color approximation
        kelvin = lerp(2700,12000,t)
        # Convert Kelvin to RGB (approximate)
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
            return (max(0,min(255,r))/255,
                    max(0,min(255,g))/255,
                    max(0,min(255,b))/255)
        rgb = kelvin_to_rgb(kelvin)
        # Store color & strength in custom particle data (via vertex colors later)
        p.size = strength   # use size as proxy for emission strength (for later shading)
        p[0] = rgb[0]; p[1] = rgb[1]; p[2] = rgb[2]   # store RGB in particle's custom data
assign_star_colors()

# 2️⃣ Nebula smear (volumetric fog)
nebula_coll = make_collection("Nebula")
bpy.ops.mesh.primitive_cube_add(size=2000, location=(0,0,0))
nebula = bpy.context.active_object
nebula.name = "Nebula_Fog"
nebula_coll.objects.link(nebula)
bpy.context.scene.collection.objects.unlink(nebula)

nebula_mat = add_material("Nebula_Fog_Mat", lambda n,l: (
    n.new('ShaderNodeVolumePrincipled', name='PrincipledVolume')
))
nebula_mat.node_tree.nodes["PrincipledVolume"].inputs["Color"].default_value = (0.102,0.039,0.180,1) # #1a0a2e
nebula_mat.node_tree.nodes["PrincipledVolume"].inputs["Emission Strength"].default_value = 0.03
nebula.data.materials.append(nebula_mat)

# 3️⃣ Origin Pulse – Information Source + Shockwave Ring
origin_coll = make_collection("Origin")
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0,0,0))
source = bpy.context.active_object
source.name = "Info_Source"
origin_coll.objects.link(source)
bpy.context.scene.collection.objects.unlink(source)

# Shockwave ring (thin torus)
bpy.ops.mesh.primitive_torus_add(major_radius=0.0, minor_radius=0.015, location=(0,0,0))
ring = bpy.context.active_object
ring.name = "Shockwave_Ring"
origin_coll.objects.link(ring)
bpy.context.scene.collection.objects.unlink(ring)

ring_mat = add_material("Ring_Emission", lambda n,l: (
    n.new('ShaderNodeEmission', name='Emission')
))
ring_mat.node_tree.nodes["Emission"].inputs["Color"].default_value = (1,1,1,1)
ring_mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = 18.0
ring.data.materials.append(ring_mat)

# Animate ring scaling (12 units / sec → 0.5 units / frame at 24 fps)
ring.scale = (0,0,0)
set_keyframe(ring, "scale", 1, (0,0,0))
set_keyframe(ring, "scale", 130, (12*130/24,12*130/24,0))  # radius in X/Y, Z stays 0

# 4️⃣ Functional Boundary – Grid Plane
grid_coll = make_collection("Boundary")
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,85))
grid = bpy.context.active_object
grid.name = "Functional_Boundary"
grid.rotation_euler = Euler((math.radians(2),0,0), 'XYZ')
grid_coll.objects.link(grid)
bpy.context.scene.collection.objects.unlink(grid)

# Subdivide to 100×100 cells (2‑unit spacing)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=100)
bpy.ops.object.mode_set(mode='OBJECT')

grid_mat = add_material("Grid_Mat", lambda n,l: (
    # Base color (near‑black) + Grid Texture → ColorRamp → Emission
    n.new('ShaderNodeEmission', name='Emission')
))
# For brevity, the full node network is omitted – you can replace the
# placeholder with a Grid Texture → ColorRamp → Mix Shader setup.
grid.data.materials.append(grid_mat)

# Breathing pulse (emission strength 1.0 → 1.5 over 90‑frame sine)
grid_mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = 1.0
for f in range(1, 271, 5):
    val = 1.25 + 0.25*math.sin(2*math.pi*(f%90)/90)
    grid_mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = val
    grid_mat.node_tree.nodes["Emission"].keyframe_insert(data_path="inputs[1].default_value", frame=f)

# 5️⃣ Collision & Shattering (simplified – you can expand with Geometry Nodes)
# We'll create a driver that stops the ring once it reaches Z=85.
# For brevity, the ripple rings and grid displacement are left as placeholders.

# 6️⃣ Camera – dolly forward, then slow near impact
cam_coll = make_collection("Camera")
bpy.ops.object.camera_add(location=(0, -200, -200))
cam = bpy.context.active_object
cam.name = "Cam_Echo"
cam_coll.objects.link(cam)
bpy.context.scene.collection.objects.unlink(cam)

cam.data.lens = 35
cam.rotation_euler = Euler((math.radians(8),0,0), 'XYZ')

# Dolly forward 0.15 units per frame until frame 210, then halt
for f in range(1, 271):
    dz = lerp(0, 0.15* (f-1), min(1, (f-1)/210))
    cam.location.z = -200 + dz
    cam.keyframe_insert(data_path="location", frame=f)

# ------------------------------------------------------------------
# SCENE 2 – "The Aristotle Glitch"
# ------------------------------------------------------------------

scene2 = bpy.data.scenes.new("Aristotle_Glitch")
bpy.context.window.scene = scene2
scene2.cycles.motion_blur_shutter = 0.5

# 1️⃣ Environment – black void, area light + rim light
scene2.world.use_nodes = True
bg = scene2.world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0,0,0,1)

# Area light (warm white)
bpy.ops.object.light_add(type='AREA', location=(-5,5,5))
area = bpy.context.active_object
area.data.energy = 400
area.data.color = (1.0,0.96,0.88)   # #fff5e0
area.data.shape = 'RECTANGLE'
area.data.size = 10

# Rim light (cool blue)
bpy.ops.object.light_add(type='POINT', location=(5,-5,-5))
rim = bpy.context.active_object
rim.data.energy = 80
rim.data.color = (0.63,0.78,1.0)   # #a0c8ff

# 2️⃣ Marble Bust – placeholder (high‑poly mesh should be imported)
bust_coll = make_collection("Bust")
# For demonstration we use a UV sphere; replace with your high‑poly bust.
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0,0,0))
bust = bpy.context.active_object
bust.name = "Aristotle_Bust"
bust_coll.objects.link(bust)
bpy.context.scene.collection.objects.unlink(bust)

# Marble material (Carrara‑style)
marble_mat = add_material("Marble_Mat", lambda n,l: (
    n.new('ShaderNodeBsdfPrincipled', name='Principled')
))
# Set base values (color, subsurface, roughness, etc.)
bsdf = marble_mat.node_tree.nodes["Principled"]
bsdf.inputs["Base Color"].default_value = (0.94,0.92,0.89,1)   # #f0ece4
bsdf.inputs["Subsurface"].default_value = 0.08
bsdf.inputs["Subsurface Color"].default_value = (0.96,0.84,0.69,1) # #f5d5b0
bsdf.inputs["Specular"].default_value = 0.6
bsdf.inputs["Roughness"].default_value = 0.15
# Vein overlay (Noise → ColorRamp → Mix)
# Omitted for brevity – you can add a Noise Texture node and blend it
# into the Base Color using a MixRGB node.

bust.data.materials.append(marble_mat)

# 3️⃣ HUD Scanner – two moving red scan lines
scan_coll = make_collection("HUD_Scanner")
bpy.ops.mesh.primitive_plane_add(size=2, location=(0,0,0))
line_top = bpy.context.active_object
line_top.name = "Scan_Line_Top"
line_top.scale = (1,0.0025,1)   # thin rectangle
line_top.location.z = 0.5
line_top.hide_viewport = False
scan_coll.objects.link(line_top)

line_bottom = line_top.copy()
line_bottom.data = line_top.data.copy()
line_bottom.name = "Scan_Line_Bottom"
line_bottom.location.z = -0.5
scan_coll.objects.link(line_bottom)

# Emission material for scan lines
scan_mat = add_material("ScanLine_Mat", lambda n,l: (
    n.new('ShaderNodeEmission', name='Emission')
))
scan_mat.node_tree.nodes["Emission"].inputs["Color"].default_value = (1,0.10,0.10,1) # #ff1a1a
scan_mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = 25.0
line_top.data.materials.append(scan_mat)
line_bottom.data.materials.append(scan_mat)

# Animate scan lines (top → bottom over 80 frames, jitter ±0.02)
for f in range(1, 241):
    t = (f-1)/80.0
    if t > 1.0: t = 1.0
    y = lerp(0.5, -0.5, t)
    jitter = random.uniform(-0.02,0.02)
    line_top.location.y = y + jitter
    line_bottom.location.y = y + jitter
    line_top.keyframe_insert(data_path="location", frame=f)
    line_bottom.keyframe_insert(data_path="location", frame=f)

# 4️⃣ Glitch HUD Overlays (screen‑space – implemented via compositor later)
# We'll add empty objects as placeholders for compositor masks.
hud_coll = make_collection("HUD_Overlays")
for name in ["BoundingBox", "Readout_TL", "Readout_TR", "ProgressBar"]:
    empty = bpy.data.objects.new(name, None)
    hud_coll.objects.link(empty)

# 5️⃣ Voxel Transition – Geometry Nodes (simplified placeholder)
# Create a Geometry Nodes modifier on the bust that swaps to a voxel
# representation when the scan line passes.  The full node tree is
# extensive; you can generate it manually or import a prepared .blend.

# 6️⃣ Camera – static, then push‑in after final transition
bpy.ops.object.camera_add(location=(0,-2,0))
cam2 = bpy.context.active_object
cam2.name = "Cam_Aristotle"
cam2.rotation_euler = Euler((math.radians(10),0,0), 'XYZ')
scene2.camera = cam2

# Push‑in animation (frames 200‑260)
cam2.location = (0,-2,0)
cam2.keyframe_insert(data_path="location", frame=200)
cam2.location = (0,-1.6,0)   # 20 % closer
cam2.keyframe_insert(data_path="location", frame=260)

# ------------------------------------------------------------------
# SCENE 3 – "The Natural Cage"
# ------------------------------------------------------------------

scene3 = bpy.data.scenes.new("Natural_Cage")
bpy.context.window.scene = scene3
scene3.cycles.motion_blur_shutter = 0.5

# Background – deep teal gradient (using world nodes)
scene3.world.use_nodes = True
wn = scene3.world.node_tree
nodes = wn.nodes
links = wn.links
nodes.clear()
bg = nodes.new('ShaderNodeBackground')
bg.inputs["Color"].default_value = (0.008,0.055,0.059,1)  # #010d0f
grad = nodes.new('ShaderNodeTexGradient')
grad.gradient_type = 'RADIAL'
coord = nodes.new('ShaderNodeTexCoord')
mix = nodes.new('ShaderNodeMixRGB')
mix.blend_type = 'MIX'
mix.inputs["Fac"].default_value = 0.5
links.new(coord.outputs["Object"], grad.inputs["Vector"])
links.new(grad.outputs["Color"], mix.inputs["Color2"])
links.new(bg.outputs["Background"], nodes.new('ShaderNodeOutputWorld').inputs["Surface"])

# 1️⃣ Sine Wave Rope
wave_coll = make_collection("Wave_Rope")
bpy.ops.curve.primitive_bezier_curve_add(location=(0,0,0))
curve = bpy.context.active_object
curve.name = "Sine_Wave"
wave_coll.objects.link(curve)
bpy.context.scene.collection.objects.unlink(curve)

# Build 3 full oscillations with amplitude 15
spline = curve.data.splines[0]
spline.bezier_points[0].co = (-60,0,0)
spline.bezier_points[1].co = (60,0,0)
# Use a modifier to shape into sine
curve.modifiers.new(name="Sine_Mod", type='DISPLACE')
disp = curve.modifiers["Sine_Mod"]
disp.texture = bpy.data.textures.new("Sine_Noise", type='CLOUDS')
disp.texture.noise_scale = 0.8
disp.direction = 'Z'
disp.strength = 15

# Convert to mesh (curve‑to‑mesh) with circular cross‑section
bpy.ops.object.convert(target='MESH')
rope = bpy.context.active_object
rope.name = "Rope_Mesh"

# Emission material (color ramps based on Y position)
rope_mat = add_material("Rope_Emission", lambda n,l: (
    n.new('ShaderNodeEmission', name='Emission')
))
rope_mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = 8.0
rope.data.materials.append(rope_mat)

# 2️⃣ Golden Pillars
pillars_coll = make_collection("Golden_Pillars")
for x in (-20, 20):
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x,0,0))
    pillar = bpy.context.active_object
    pillar.scale = (1,1,25)   # 2×2×50
    pillar.name = f"Pillar_{x}"
    pillars_coll.objects.link(pillar)
    bpy.context.scene.collection.objects.unlink(pillar)

    # Gold PBR material
    gold_mat = add_material("Gold_PBR", lambda n,l: (
        n.new('ShaderNodeBsdfPrincipled', name='Principled')
    ))
    bsdf = gold_mat.node_tree.nodes["Principled"]
    bsdf.inputs["Base Color"].default_value = (0.83,0.63,0.09,1)   # #d4a017
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.08
    bsdf.inputs["Anisotropic"].default_value = 0.3
    # Emission overlay (faint gold glow)
    emit = gold_mat.node_tree.nodes.new('ShaderNodeEmission')
    emit.inputs["Color"].default_value = (1.0,0.88,0.38,1)   # #ffd060
    emit.inputs["Strength"].default_value = 0.8
    mix = gold_mat.node_tree.nodes.new('ShaderNodeMixShader')
    gold_mat.node_tree.links.new(bsdf.outputs["BSDF"], mix.inputs[1])
    gold_mat.node_tree.links.new(emit.outputs["Emission"], mix.inputs[2])
    gold_mat.node_tree.links.new(mix.outputs["Shader"], gold_mat.node_tree.nodes["Material Output"].inputs["Surface"])
    pillar.data.materials.append(gold_mat)

    # Drop animation (Z from +200 to 0 over 18 frames)
    pillar.location.z = 200
    pillar.keyframe_insert(data_path="location", frame=1)
    pillar.location.z = 0
    pillar.keyframe_insert(data_path="location", frame=18)

# 3️⃣ Standing Wave (after pillars land)
# Placeholder: you would replace the noisy wave with a static mesh
# and animate its amplitude via a driver or shape key.

# 4️⃣ Camera – wide shot then cut to medium shot
bpy.ops.object.camera_add(location=(0,-150,30))
cam3 = bpy.context.active_object
cam3.name = "Cam_NaturalCage"
scene3.camera = cam3
cam3.rotation_euler = Euler((math.radians(20),0,0), 'XYZ')
# Cut to medium shot at frame 30 (simply move camera)
cam3.keyframe_insert(data_path="location", frame=1)
cam3.location = (0,-80,20)
cam3.keyframe_insert(data_path="location", frame=30)

# ------------------------------------------------------------------
# SCENE 4 – "The Causal Firewall"
# ------------------------------------------------------------------

scene4 = bpy.data.scenes.new("Causal_Firewall")
bpy.context.window.scene = scene4
scene4.cycles.motion_blur_shutter = 0.5

# Re‑use starfield (copy collection)
starfield_copy = star_coll.copy()
scene4.collection.children.link(starfield_copy)

# 1️⃣ Earth Sphere (Causal Core)
earth_coll = make_collection("Earth")
bpy.ops.mesh.primitive_uv_sphere_add(radius=3, location=(0,0,0))
earth = bpy.context.active_object
earth.name = "Earth_Core"
earth_coll.objects.link(earth)
bpy.context.scene.collection.objects.unlink(earth)

# Procedural planet material (Voronoi + Noise)
earth_mat = add_material("Earth_Mat", lambda n,l: (
    n.new('ShaderNodeBsdfPrincipled', name='Principled')
))
bsdf = earth_mat.node_tree.nodes["Principled"]
# Base color placeholder – you can replace with a full node tree
bsdf.inputs["Base Color"].default_value = (0.2,0.3,0.2,1)
earth.data.materials.append(earth_mat)

# Atmosphere sphere (slightly larger)
bpy.ops.mesh.primitive_uv_sphere_add(radius=3.15, location=(0,0,0))
atm = bpy.context.active_object
atm.name = "Atmosphere"
atm.data.materials.append(add_material("Atmosphere_Mat", lambda n,l: (
    n.new('ShaderNodeVolumePrincipled', name='PrincipledVolume')
)))
earth_coll.objects.link(atm)
bpy.context.scene.collection.objects.unlink(atm)

# Cloud sphere (slightly larger)
bpy.ops.mesh.primitive_uv_sphere_add(radius=3.08, location=(0,0,0))
clouds = bpy.context.active_object
clouds.name = "Clouds"
clouds.data.materials.append(add_material("Cloud_Mat", lambda n,l: (
    n.new('ShaderNodePrincipledBSDF', name='Principled')
)))
earth_coll.objects.link(clouds)
bpy.context.scene.collection.objects.unlink(clouds)

# 2️⃣ Light Shell (Speed‑of‑Light Boundary)
shell_coll = make_collection("Light_Shell")
bpy.ops.mesh.primitive_uv_sphere_add(radius=18, location=(0,0,0))
shell = bpy.context.active_object
shell.name = "Light_Shell"
shell_coll.objects.link(shell)
bpy.context.scene.collection.objects.unlink(shell)

# Shell material – emissive Voronoi + Fresnel edge glow
shell_mat = add_material("Shell_Mat", lambda n,l: (
    n.new('ShaderNodeEmission', name='Emission')
))
shell_mat.node_tree.nodes["Emission"].inputs["Color"].default_value = (1,1,1,1)
shell_mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = 120.0
shell.data.materials.append(shell_mat)

# Pulsing emission (30‑frame sine)
for f in range(1, 301, 5):
    strength = 100 + 20*math.sin(2*math.pi*(f%30)/30)
    shell_mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = strength
    shell_mat.node_tree.nodes["Emission"].keyframe_insert(data_path="inputs[1].default_value", frame=f)

# 3️⃣ Dark Storm (volumetric domain)
storm_coll = make_collection("Storm")
bpy.ops.mesh.primitive_uv_sphere_add(radius=60, location=(0,0,0))
storm = bpy.context.active_object
storm.name = "Storm_Volume"
storm_coll.objects.link(storm)
bpy.context.scene.collection.objects.unlink(storm)

storm_mat = add_material("Storm_Mat", lambda n,l: (
    n.new('ShaderNodeVolumePrincipled', name='PrincipledVolume')
))
storm_mat.node_tree.nodes["PrincipledVolume"].inputs["Color"].default_value = (0.10,0.06,0.07,1) # #1a1018
storm_mat.node_tree.nodes["PrincipledVolume"].inputs["Density"].default_value = 0.02
storm.data.materials.append(storm_mat)

# Dark lightning (simple emissive curves – placeholder objects)
for i in range(6):
    bpy.ops.mesh.primitive_curve_bezier_add(location=(random.uniform(-30,30),random.uniform(-30,30),random.uniform(-30,30)))
    bolt = bpy.context.active_object
    bolt.name = f"Lightning_{i}"
    bolt.data.bevel_depth = 0.02
    bolt.data.bevel_resolution = 4
    bolt_mat = add_material("Lightning_Mat", lambda n,l: (
        n.new('ShaderNodeEmission', name='Emission')
    ))
    bolt_mat.node_tree.nodes["Emission"].inputs["Color"].default_value = (0.5,0,0.38,1) # #800060
    bolt_mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = 6.0
    bolt.data.materials.append(bolt_mat)
    storm_coll.objects.link(bolt)

# 4️⃣ Particle Streams (incoming to shell)
particle_coll = make_collection("Particles")
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(58,0,0))
proto = bpy.context.active_object
proto.name = "Particle_Proto"
particle_coll.objects.link(proto)
bpy.context.scene.collection.objects.unlink(proto)

# Emission material for particles
part_mat = add_material("Particle_Emission", lambda n,l: (
    n.new('ShaderNodeEmission', name='Emission')
))
part_mat.node_tree.nodes["Emission"].inputs["Color"].default_value = (0.16,0.13,0.19,1) # #2a2030
part_mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = 2.0
proto.data.materials.append(part_mat)

# Particle system on an empty that spawns particles around the storm edge
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
particle_emitter = bpy.context.active_object
particle_emitter.name = "Particle_Emitter"
ps = particle_emitter.modifiers.new(name="ParticleStream", type='PARTICLE_SYSTEM')
psettings = ps.particle_system.settings
psettings.count = 2000
psettings.frame_start = 1
psettings.frame_end = 250
psettings.lifetime = 300
psettings.render_type = 'OBJECT'
psettings.instance_object = proto
psettings.use_dynamic_rotation = False
psettings.velocity_factor_random = 0.5
psettings.normal_factor = -0.8   # inward
psettings.use_rotations = False

# 5️⃣ Camera – inside bubble, then dolly outward
bpy.ops.object.camera_add(location=(0,0,-5))
cam4 = bpy.context.active_object
cam4.name = "Cam_Firewall"
scene4.camera = cam4
cam4.rotation_euler = Euler((0,0,0), 'XYZ')
# Dolly outward (frames 1‑150)
for f in range(1, 151):
    cam4.location = (0,0,-5 - f*0.1)
    cam4.keyframe_insert(data_path="location", frame=f)

# ------------------------------------------------------------------
# SCENE 5 – "The Recursive Failsafe"
# ------------------------------------------------------------------

scene5 = bpy.data.scenes.new("Recursive_Failsafe")
bpy.context.window.scene = scene5
scene5.cycles.motion_blur_shutter = 0.5

# 1️⃣ Multi‑ring structure
rings_coll = make_collection("Core_Rings")
radii = [5,9,14,20]
minor = [0.3,0.25,0.2,0.15]
axes = [(0,0,0), (35,0,0), (0,60,0), (45,15,0)]  # tilt in degrees (X,Y,Z)
for i, (R,m) in enumerate(zip(radii,minor)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=m, location=(0,0,0))
    ring = bpy.context.active_object
    ring.name = f"Ring_{i+1}"
    rings_coll.objects.link(ring)
    bpy.context.scene.collection.objects.unlink(ring)
    # Apply tilt
    ring.rotation_euler = Euler((math.radians(axes[i][0]),
                                 math.radians(axes[i][1]),
                                 math.radians(axes[i][2])), 'XYZ')
    # Material – chaotic red with flicker noise
    red_mat = add_material(f"Ring_{i+1}_Mat", lambda n,l: (
        n.new('ShaderNodeEmission', name='Emission')
    ))
    red_mat.node_tree.nodes["Emission"].inputs["Color"].default_value = (0.80,0.07,0.00,1) # #cc1100
    red_mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = 4.0
    ring.data.materials.append(red_mat)

# 2️⃣ Geometric Eye (centered)
eye_coll = make_collection("Geometric_Eye")
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=0.2, location=(0,0,0))
eye = bpy.context.active_object
eye.name = "Eye_Iris"
eye_coll.objects.link(eye)
bpy.context.scene.collection.objects.unlink(eye)

# Eye material – dark with gold circuit overlay (placeholder)
eye_mat = add_material("Eye_Mat", lambda n,l: (
    n.new('ShaderNodeEmission', name='Emission')
))
eye_mat.node_tree.nodes["Emission"].inputs["Color"].default_value = (0.10,0.10,0.10,1) # dark
eye_mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.2
eye.data.materials.append(eye_mat)

# Surrounding diamond/rhombus shapes (6 copies, rotated)
for i in range(6):
    bpy.ops.mesh.primitive_cone_add(radius1=0.5, radius2=0.0, depth=2, location=(0,0,0))
    shape = bpy.context.active_object
    shape.name = f"Eye_Shape_{i}"
    shape.rotation_euler = Euler((0,0,math.radians(i*60)), 'XYZ')
    shape.scale = (0.2,0.2,0.2)
    eye_coll.objects.link(shape)
    bpy.context.scene.collection.objects.unlink(shape)

# 3️⃣ Blink mechanism (simple animation using keyframes on rotation of surrounding shapes)
blink_frames = []
frame = 1
while frame < 600:
    # Closed phase
    for i in range(6):
        shape = bpy.data.objects[f"Eye_Shape_{i}"]
        shape.rotation_euler.z = math.radians(0)
        shape.keyframe_insert(data_path="rotation_euler", frame=frame)
    # Open phase after 8 frames
    frame += 8
    for i in range(6):
        shape = bpy.data.objects[f"Eye_Shape_{i}"]
        shape.rotation_euler.z = math.radians(180)
        shape.keyframe_insert(data_path="rotation_euler", frame=frame)
    # Random open interval 40‑80 frames
    frame += random.randint(40,80)

# 4️⃣ Blink‑triggered cascade (simplified with drivers)
# For each blink, we will add a keyframe to the rings' emission color/strength
def set_ring_state(ring_obj, frame, color, strength, speed_mul):
    mat = ring_obj.active_material
    mat.node_tree.nodes["Emission"].inputs["Color"].default_value = color
    mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = strength
    mat.node_tree.nodes["Emission"].keyframe_insert(data_path="inputs[1].default_value", frame=frame)
    # Rotation speed change via custom property
    ring_obj["rot_speed"] = speed_mul
    ring_obj.keyframe_insert(data_path='["rot_speed"]', frame=frame)

# Example: first blink at frame 120
set_ring_state(bpy.data.objects["Ring_1"], 120, (0.8,0.8,1,1), 4.0, 1.5)
# Subsequent blinks would be scripted similarly.

# 5️⃣ Camera – medium‑wide, then zoom‑in
bpy.ops.object.camera_add(location=(0,-10,2))
cam5 = bpy.context.active_object
cam5.name = "Cam_Failsafe"
scene5.camera = cam5
cam5.rotation_euler = Euler((math.radians(10),0,0), 'XYZ')
# Zoom‑in after first blink (frame 150)
cam5.keyframe_insert(data_path="location", frame=1)
cam5.location = (0,-8,2)
cam5.keyframe_insert(data_path="location", frame=210)

# ------------------------------------------------------------------
# SCENE 6 – "The Measurement Cliffhanger"
# ------------------------------------------------------------------

scene6 = bpy.data.scenes.new("Measurement_Cliffhanger")
bpy.context.window.scene = scene6
scene6.cycles.motion_blur_shutter = 1.0   # high blur for particle streaks

# Re‑use starfield
starfield_copy2 = star_coll.copy()
scene6.collection.children.link(starfield_copy2)

# Superposition particle – 10 spheres in a loose cluster
particle_coll6 = make_collection("Superposition")
for i in range(10):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(random.uniform(-2,2),
                                                             random.uniform(-2,2),
                                                             random.uniform(-2,2)))
    sph = bpy.context.active_object
    sph.name = f"SuperSphere_{i}"
    particle_coll6.objects.link(sph)
    bpy.context.scene.collection.objects.unlink(sph)
    mat = add_material(f"SuperMat_{i}", lambda n,l: (
        n.new('ShaderNodeEmission', name='Emission')
    ))
    mat.node_tree.nodes["Emission"].inputs["Color"].default_value = (1.0,0.83,0.27,1) # #ffdd44
    mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = 12.0
    sph.data.materials.append(mat)
    # Random oscillation animation (simple location keyframes)
    for f in range(1, 301, 10):
        offset = Vector((random.uniform(-0.5,0.5),
                         random.uniform(-0.5,0.5),
                         random.uniform(-0.5,0.5)))
        sph.location = offset
        sph.keyframe_insert(data_path="location", frame=f)

# Camera – fly‑past
bpy.ops.object.camera_add(location=(0, -150, 0))
cam6 = bpy.context.active_object
cam6.name = "Cam_Measure"
scene6.camera = cam6
cam6.rotation_euler = Euler((0,0,0), 'XYZ')
# Move forward (negative Z) over 300 frames
for f in range(1, 301):
    cam6.location.y = -150 + (f-1)*(150/300)
    cam6.keyframe_insert(data_path="location", frame=f)

# Collision & collapse (frame ~200)
# We'll use a simple keyframe to hide the 10 spheres and show a single sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0,0,0))
final_sphere = bpy.context.active_object
final_sphere.name = "Resolved_Particle"
final_mat = add_material("Resolved_Mat", lambda n,l: (
    n.new('ShaderNodeEmission', name='Emission')
))
final_mat.node_tree.nodes["Emission"].inputs["Color"].default_value = (1.0,0.83,0.27,1)
final_mat.node_tree.nodes["Emission"].inputs["Strength"].default_value = 20.0
final_sphere.data.materials.append(final_mat)
final_sphere.hide_viewport = True
final_sphere.hide_render = True
scene6.collection.objects.link(final_sphere)

# At frame 200 hide the 10 spheres
for i in range(10):
    obj = bpy.data.objects[f"SuperSphere_{i}"]
    obj.hide_viewport = True
    obj.hide_render = True
    obj.keyframe_insert(data_path="hide_viewport", frame=200)
    obj.keyframe_insert(data_path="hide_render", frame=200)

# Show the resolved sphere at frame 206
final_sphere.hide_viewport = False
final_sphere.hide_render = False
final_sphere.keyframe_insert(data_path="hide_viewport", frame=206)
final_sphere.keyframe_insert(data_path="hide_render", frame=206)

# Cut to black on frame 250 (override compositing)
scene6.world.use_nodes = True
wn6 = scene6.world.node_tree
nodes6 = wn6.nodes
links6 = wn6.links
nodes6.clear()
bg6 = nodes6.new('ShaderNodeBackground')
bg6.inputs["Color"].default_value = (0,0,0,1)
out6 = nodes6.new('ShaderNodeOutputWorld')
links6.new(bg6.outputs["Background"], out6.inputs["Surface"])

# ------------------------------------------------------------------
# COMPOSITING (common to all scenes)
# ------------------------------------------------------------------

def setup_compositor(scene):
    """Add lens distortion, chromatic aberration, glare, vignette, grain."""
    scene.use_nodes = True
    tree = scene.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()

    # Render layers
    rl = nodes.new('CompositorNodeRLayers')
    rl.location = (0,0)

    # Lens distortion
    lens = nodes.new('CompositorNodeLensdist')
    lens.inputs["Distort"].default_value = 0.02
    lens.location = (200,0)
    links.new(rl.outputs["Image"], lens.inputs["Image"])

    # Chromatic aberration (separate for glitch frames – omitted)
    ca = nodes.new('CompositorNodeLensdist')
    ca.inputs["Distort"].default_value = 0.003
    ca.location = (400,0)
    links.new(lens.outputs["Image"], ca.inputs["Image"])

    # Glare (Streaks)
    glare = nodes.new('CompositorNodeGlare')
    glare.glare_type = 'STREAKS'
    glare.threshold = 0.8
    glare.mix = -0.3
    glare.location = (600,0)
    links.new(ca.outputs["Image"], glare.inputs["Image"])

    # Vignette (mix with darkened corners)
    vignette = nodes.new('CompositorNodeEllipseMask')
    vignette.width = 0.9
    vignette.height = 0.9
    vignette.location = (800,0)
    mix = nodes.new('CompositorNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs["Fac"].default_value = 0.5
    mix.location = (1000,0)
    links.new(glare.outputs["Image"], mix.inputs[1])
    links.new(vignette.outputs["Mask"], mix.inputs[2])

    # Film grain
    grain = nodes.new('CompositorNodeNoise')
    grain.inputs["Scale"].default_value = 1000
    grain.location = (1200,0)
    mix2 = nodes.new('CompositorNodeMixRGB')
    mix2.blend_type = 'OVERLAY'
    mix2.inputs["Fac"].default_value = 0.08
    mix2.location = (1400,0)
    links.new(mix.outputs["Image"], mix2.inputs[1])
    links.new(grain.outputs["Image"], mix2.inputs[2])

    # Composite output
    comp = nodes.new('CompositorNodeComposite')
    comp.location = (1600,0)
    links.new(mix2.outputs["Image"], comp.inputs["Image"])

# Apply compositor to each scene
for sc in [scene1, scene2, scene3, scene4, scene5, scene6]:
    setup_compositor(sc)

# ------------------------------------------------------------------
# FINAL NOTES
# ------------------------------------------------------------------

print("All six scenes have been created.")
print("You may need to fine‑tune node networks (grid texture, wave color ramp, etc.)")
print("and add the missing Geometry‑Nodes setups for the ripple effects and voxel transition.")
print("Render each scene individually or concatenate them in the Video Sequencer.")

# -------------------------------------------------------------
# End of script
# -------------------------------------------------------------