# ------------------------------------------------------------
# Blender 5.0.1 – Chapter 1 “The Echo Hook”
# ------------------------------------------------------------
# Generates the first visual chapter and renders it to MP4
# in C:/tmp/chapter1.mp4
# ------------------------------------------------------------

import bpy
import math
import random
from mathutils import Vector

# ----------------------------------------------------------------------
# USER SETTINGS ---------------------------------------------------------
# ----------------------------------------------------------------------
OUTPUT_DIR   = "C:/tmp"
OUTPUT_FILE  = "chapter1.mp4"
FPS          = 24
RES_X        = 1920
RES_Y        = 1080
FRAME_START  = 1
FRAME_END    = 300          # a little beyond the final hold
STAR_COUNT   = 80000
STAR_RADIUS  = 10000
GRID_SIZE    = 200
GRID_SUBDIV  = 100            # creates 100×100 cells (2‑unit spacing)
RING_SPEED   = 12.0            # units / sec → 0.5 units / frame
RING_THRU   = 85.0            # distance where impact occurs
RING_MAX_FR  = int(RING_THRU / (RING_SPEED / FPS))  # ≈170
RIPPLE_COUNT = 6
RIPPLE_DELAY = 10            # frames between successive ripple spawns
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# CLEAN SCENE -----------------------------------------------------------
# ----------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start = FRAME_START
scene.frame_end   = FRAME_END
scene.render.fps   = FPS
scene.render.resolution_x = RES_X
scene.render.resolution_y = RES_Y
# Video output is set via ffmpeg settings only
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.filepath = f"{OUTPUT_DIR}/{OUTPUT_FILE}"


# ----------------------------------------------------------------------
# STARFIELD -------------------------------------------------------------
# ----------------------------------------------------------------------
def create_starfield():
    """Create a point‑cloud starfield with per‑vertex colour & intensity."""
    mesh = bpy.data.meshes.new("StarfieldMesh")
    obj  = bpy.data.objects.new("Starfield", mesh)
    bpy.context.collection.objects.link(obj)

    verts = []
    for _ in range(STAR_COUNT):
        theta = random.random() * 2 * math.pi
        phi   = math.acos(2 * random.random() - 1)
        r = STAR_RADIUS
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        verts.append((x, y, z))

    mesh.from_pydata(verts, [], [])
    mesh.update()

    # ---- Vertex colour layer (RGB = colour, A = intensity) ----
    col_layer = mesh.vertex_colors.new(name="Col")
    for i, loop in enumerate(mesh.loops):
        rand = random.random()
        amber = (1.0, 0.6, 0.3)          # warm amber
        blue  = (0.6, 0.8, 1.0)          # blue‑white
        rgb = tuple(amber[j] * (1 - rand) + blue[j] * rand for j in range(3))
        intensity = 0.2 + 1.3 * random.random()   # 0.2‑1.5 → alpha 0‑1
        col_layer.data[i].color = rgb + (intensity,)
    # --------------------------------------------------------------

    # ---- Material – emission that reads vertex colour (including alpha) ----
    mat = bpy.data.materials.new(name="StarMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node   = nodes.new(type='ShaderNodeOutputMaterial')
    emit_node  = nodes.new(type='ShaderNodeEmission')
    vcol_node  = nodes.new(type='ShaderNodeVertexColor')
    vcol_node.layer_name = "Col"

    # Multiply colour by its alpha (intensity)
    mul_node   = nodes.new(type='ShaderNodeMath')
    mul_node.operation = 'MULTIPLY'

    # Connections
    links.new(vcol_node.outputs['Color'], emit_node.inputs['Color'])
    links.new(vcol_node.outputs['Alpha'], mul_node.inputs[0])
    links.new(mul_node.outputs['Value'], emit_node.inputs['Strength'])
    links.new(emit_node.outputs['Emission'], out_node.inputs['Surface'])

    obj.data.materials.append(mat)
    return obj


# ----------------------------------------------------------------------
# NEBULA ---------------------------------------------------------------
# ----------------------------------------------------------------------
def create_nebula():
    """Add a large low‑density volumetric cube that acts as a faint nebula."""
    bpy.ops.mesh.primitive_cube_add(size=4000, location=(0, 0, 0))
    vol = bpy.context.active_object
    vol.name = "Nebula"

    mat = bpy.data.materials.new(name="NebulaMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    vol_node = nodes.new(type='ShaderNodeVolumePrincipled')
    vol_node.inputs['Density'].default_value = 0.03
    vol_node.inputs['Color'].default_value = (0.10, 0.05, 0.18, 1)   # #1a0a2e

    links.new(vol_node.outputs['Volume'], out_node.inputs['Volume'])
    vol.data.materials.append(mat)
    return vol


# ----------------------------------------------------------------------
# INFORMATION SOURCE ----------------------------------------------------
# ----------------------------------------------------------------------
def create_info_source():
    """Tiny sphere at the origin – the “information source”."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0, 0, 0))
    src = bpy.context.active_object
    src.name = "InfoSource"
    return src


# ----------------------------------------------------------------------
# SHOCKWAVE RING --------------------------------------------------------
# ----------------------------------------------------------------------
def create_shockwave_ring():
    """Razor‑thin torus that expands outward as the echo."""
    bpy.ops.mesh.primitive_torus_add(major_radius=0.0, minor_radius=0.015,
                                     location=(0, 0, 0))
    ring = bpy.context.active_object
    ring.name = "ShockwaveRing"
    ring.scale = (0, 0, 0)   # start invisible

    mat = bpy.data.materials.new(name="RingMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    emit_node = nodes.new(type='ShaderNodeEmission')
    emit_node.inputs['Color'].default_value = (1, 1, 1, 1)
    emit_node.inputs['Strength'].default_value = 18.0

    # Simple halo – low‑strength Volume Scatter mixed in
    vol_node = nodes.new(type='ShaderNodeVolumeScatter')
    vol_node.inputs['Density'].default_value = 0.1
    mix_node = nodes.new(type='ShaderNodeMixShader')
    links.new(emit_node.outputs['Emission'], mix_node.inputs[1])
    links.new(vol_node.outputs['Volume'], mix_node.inputs[2])
    links.new(mix_node.outputs['Shader'], out_node.inputs['Surface'])

    ring.data.materials.append(mat)
    return ring


def animate_shockwave(ring):
    """Scale the ring from 0 → 85 units, then hold."""
    ring.scale = (0, 0, 0)
    ring.keyframe_insert(data_path="scale", frame=1)

    impact = RING_MAX_FR
    ring.scale = (RING_THRU, RING_THRU, 0)
    ring.keyframe_insert(data_path="scale", frame=impact)

    # Hold after impact
    ring.scale = (RING_THRU, RING_THRU, 0)
    ring.keyframe_insert(data_path="scale", frame=impact + 1)


# ----------------------------------------------------------------------
# FUNCTIONAL BOUNDARY GRID ---------------------------------------------
# ----------------------------------------------------------------------
def create_grid():
    """Translucent blue grid that “breathes” (emission 1.0 ↔ 1.5)."""
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=GRID_SUBDIV,
                                     y_subdivisions=GRID_SUBDIV,
                                     size=GRID_SIZE/2,
                                     location=(0, 0, RING_THRU))
    grid = bpy.context.active_object
    grid.name = "FunctionalBoundary"
    grid.rotation_euler = (math.radians(2.5), 0, 0)

    mat = bpy.data.materials.new(name="GridMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = (0.04, 0.10, 1.0, 1)   # #0a1aff
    principled.inputs['Emission Color'].default_value = (0.04, 0.10, 1.0, 1)
    principled.inputs['Emission Strength'].default_value = 1.2
    principled.inputs['Transmission Weight'].default_value = 0.65
    principled.inputs['Roughness'].default_value = 0.0

    # Grid‑line mask (checker + ramp)
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    mapping   = nodes.new(type='ShaderNodeMapping')
    checker   = nodes.new(type='ShaderNodeTexChecker')
    ramp      = nodes.new(type='ShaderNodeValToRGB')
    mix_rgb   = nodes.new(type='ShaderNodeMixRGB')
    mix_rgb.blend_type = 'MULTIPLY'

    checker.inputs['Scale'].default_value = 50
    ramp.color_ramp.elements[0].position = 0.48
    ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp.color_ramp.elements[1].position = 0.52
    ramp.color_ramp.elements[1].color = (0.04, 0.10, 1.0, 1)

    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], checker.inputs['Vector'])
    links.new(checker.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], mix_rgb.inputs['Color2'])
    mix_rgb.inputs['Color1'].default_value = (0, 0, 0, 1)

    links.new(mix_rgb.outputs['Color'], principled.inputs['Base Color'])
    links.new(mix_rgb.outputs['Color'], principled.inputs['Emission Color'])
    links.new(principled.outputs['BSDF'], out_node.inputs['Surface'])

    grid.data.materials.append(mat)

    # Breathing emission (SINE‑like)
    principled.inputs['Emission Strength'].default_value = 1.0
    principled.inputs['Emission Strength'].keyframe_insert(data_path="default_value", frame=1)
    principled.inputs['Emission Strength'].default_value = 1.5
    principled.inputs['Emission Strength'].keyframe_insert(data_path="default_value", frame=46)
    principled.inputs['Emission Strength'].default_value = 1.0
    principled.inputs['Emission Strength'].keyframe_insert(data_path="default_value", frame=91)

    if mat.node_tree.animation_data and mat.node_tree.animation_data.action:
        print(f"Action attributes: {dir(mat.node_tree.animation_data.action)}")
        for f in mat.node_tree.animation_data.action.fcurves:
            f.modifiers.new(type='CYCLES')
            for kp in f.keyframe_points:
                kp.interpolation = 'SINE'

    return grid


# ----------------------------------------------------------------------
# GRID DISPLACEMENT RIPPLE -----------------------------------------------
# ----------------------------------------------------------------------
def add_grid_ripple(grid):
    """Radial displacement on the grid at impact."""
    disp = grid.modifiers.new(name="RippleDisp", type='DISPLACE')
    tex = bpy.data.textures.new(name="RippleTex", type='CLOUDS')
    tex.noise_scale = 0.5
    disp.texture = tex
    disp.strength = 0.0
    impact = RING_MAX_FR
    disp.keyframe_insert(data_path="strength", frame=impact)
    disp.strength = 1.5
    disp.keyframe_insert(data_path="strength", frame=impact + 10)
    disp.strength = 0.0
    disp.keyframe_insert(data_path="strength", frame=impact + 58)
    return disp


# ----------------------------------------------------------------------
# RIPPLE RINGS (back‑toward‑camera) --------------------------------------
# ----------------------------------------------------------------------
def create_ripple_ring(offset_radius, start_frame):
    """Concentric rings that travel toward the camera after impact."""
    bpy.ops.mesh.primitive_torus_add(major_radius=offset_radius,
                                     minor_radius=0.015,
                                     location=(0, 0, RING_THRU))
    ring = bpy.context.active_object
    ring.name = f"Ripple_{offset_radius:.1f}"

    mat = bpy.data.materials.new(name=f"RippleMat_{offset_radius:.1f}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    emit_node = nodes.new(type='ShaderNodeEmission')
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.location = (-200, 0)

    # Gradient: white → ice blue → pale blue‑white
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (1, 1, 1, 1)          # #FFFFFF
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = (0.53, 0.80, 1.0, 1)       # #88ccff
    ramp.color_ramp.elements[2].position = 1.0
    ramp.color_ramp.elements[2].color = (0.87, 0.94, 1.0, 1)       # #ddeeff

    emit_node.inputs['Strength'].default_value = 0.3

    links.new(ramp.outputs['Color'], emit_node.inputs['Color'])
    links.new(emit_node.outputs['Emission'], out_node.inputs['Surface'])
    ring.data.materials.append(mat)

    # Move toward camera (negative Z)
    ring.location = (0, 0, RING_THRU)
    ring.keyframe_insert(data_path="location", frame=start_frame)
    ring.location = (0, 0, -200)
    ring.keyframe_insert(data_path="location", frame=start_frame + 120)

    # Fade emission
    emit_node.inputs['Strength'].default_value = 0.3
    emit_node.inputs['Strength'].keyframe_insert(data_path="default_value", frame=start_frame)
    emit_node.inputs['Strength'].default_value = 0.1
    emit_node.inputs['Strength'].keyframe_insert(data_path="default_value", frame=start_frame + 120)

    # Scale growth
    ring.scale = (1, 1, 1)
    ring.keyframe_insert(data_path="scale", frame=start_frame)
    ring.scale = (3, 3, 3)
    ring.keyframe_insert(data_path="scale", frame=start_frame + 120)

    return ring


# ----------------------------------------------------------------------
# CAMERA ---------------------------------------------------------------
# ----------------------------------------------------------------------
def create_camera():
    """Camera starts far back, dolly‑forward until impact, then holds."""
    bpy.ops.object.camera_add(location=(0, 0, -200))
    cam = bpy.context.active_object
    cam.name = "Camera"

    # Point at origin
    direction = Vector((0, 0, 0)) - cam.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    # Downward tilt ~8°
    cam.rotation_euler.x += math.radians(8)

    # Dolly forward (0.15 units / frame) until impact frame
    cam.location = (0, 0, -200)
    cam.keyframe_insert(data_path="location", frame=1)
    cam.location = (0, 0, -200 + 0.15 * RING_MAX_FR)
    cam.keyframe_insert(data_path="location", frame=RING_MAX_FR)

    # Hold after impact
    cam.keyframe_insert(data_path="location", frame=RING_MAX_FR + 40)

    return cam


# ----------------------------------------------------------------------
# RENDER SETTINGS --------------------------------------------------------
# ----------------------------------------------------------------------
def set_render_settings():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 512
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.motion_blur_position = 'CENTER'
    scene.cycles.motion_blur_shutter = 0.5
    scene.cycles.use_denoising = True
    scene.render.film_transparent = False
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'


# ----------------------------------------------------------------------
# MAIN -------------------------------------------------------------------
# ----------------------------------------------------------------------
def main():
    create_starfield()
    create_nebula()
    create_info_source()
    ring = create_shockwave_ring()
    animate_shockwave(ring)

    grid = create_grid()
    add_grid_ripple(grid)

    for i in range(RIPPLE_COUNT):
        radius_offset = 3.0 * (i + 1)
        start_f = RING_MAX_FR + i * RIPPLE_DELAY
        create_ripple_ring(radius_offset, start_f)

    create_camera()
    set_render_settings()
    print(f"Setup complete – rendering to {OUTPUT_DIR}/{OUTPUT_FILE}")

    # Uncomment the line below to start rendering automatically:
    # bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()