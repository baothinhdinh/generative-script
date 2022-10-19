import random
import time
import math

import bpy
import bmesh

def purge_orphans():
    """
    Remove all orphan data blocks

    see this from more info:
    https://youtu.be/3rNqVPtbhzc?t=149
    """
    if bpy.app.version >= (3, 0, 0):
        # run this only for Blender versions 3.0 and higher
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    else:
        # run this only for Blender versions lower than 3.0
        # call purge_orphans() recursively until there are no more orphan data blocks to purge
        result = bpy.ops.outliner.orphans_purge()
        if result.pop() != "CANCELLED":
            purge_orphans()


def clean_scene():
    """
    Removing all of the objects, collection, materials, particles,
    textures, images, curves, meshes, actions, nodes, and worlds from the scene

    Checkout this video explanation with example

    "How to clean the scene with Python in Blender (with examples)"
    https://youtu.be/3rNqVPtbhzc
    """
    # make sure the active object is not in Edit Mode
    if bpy.context.active_object and bpy.context.active_object.mode == "EDIT":
        bpy.ops.object.editmode_toggle()

    # make sure non of the objects are hidden from the viewport, selection, or disabled
    for obj in bpy.data.objects:
        obj.hide_set(False)
        obj.hide_select = False
        obj.hide_viewport = False

    # select all the object and delete them (just like pressing A + X + D in the viewport)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    # find all the collections and remove them
    collection_names = [col.name for col in bpy.data.collections]
    for name in collection_names:
        bpy.data.collections.remove(bpy.data.collections[name])

    # in the case when you modify the world shader
    # delete and recreate the world object
    world_names = [world.name for world in bpy.data.worlds]
    for name in world_names:
        bpy.data.worlds.remove(bpy.data.worlds[name])
    # create a new world data block
    bpy.ops.world.new()
    bpy.context.scene.world = bpy.data.worlds["World"]

    purge_orphans()

def convert_srgb_to_linear_rgb(srgb_color_component):
    """
    Converting from sRGB to Linear RGB
    based on https://en.wikipedia.org/wiki/SRGB#From_sRGB_to_CIE_XYZ

    Video Tutorial: https://www.youtube.com/watch?v=knc1CGBhJeU
    """
    if srgb_color_component <= 0.04045:
        linear_color_component = srgb_color_component / 12.92
    else:
        linear_color_component = math.pow((srgb_color_component + 0.055) / 1.055, 2.4)

    return linear_color_component

def hex_color_to_rgb(hex_color):
    """
    Converting from a color in the form of a hex triplet string (en.wikipedia.org/wiki/Web_colors#Hex_triplet)
    to a Linear RGB

    Supports: "#RRGGBB" or "RRGGBB"

    Note: We are converting into Linear RGB since Blender uses a Linear Color Space internally
    https://docs.blender.org/manual/en/latest/render/color_management.html

    Video Tutorial: https://www.youtube.com/watch?v=knc1CGBhJeU
    """
    # remove the leading '#' symbol if present
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]

    assert len(hex_color) == 6, f"RRGGBB is the supported hex color format: {hex_color}"

    # extracting the Red color component - RRxxxx
    red = int(hex_color[:2], 16)
    # dividing by 255 to get a number between 0.0 and 1.0
    srgb_red = red / 255
    linear_red = convert_srgb_to_linear_rgb(srgb_red)

    # extracting the Green color component - xxGGxx
    green = int(hex_color[2:4], 16)
    # dividing by 255 to get a number between 0.0 and 1.0
    srgb_green = green / 255
    linear_green = convert_srgb_to_linear_rgb(srgb_green)

    # extracting the Blue color component - xxxxBB
    blue = int(hex_color[4:6], 16)
    # dividing by 255 to get a number between 0.0 and 1.0
    srgb_blue = blue / 255
    linear_blue = convert_srgb_to_linear_rgb(srgb_blue)

    return tuple([linear_red, linear_green, linear_blue])

def hex_color_to_rgba(hex_color, alpha=1.0):
    """
    Converting from a color in the form of a hex triplet string (en.wikipedia.org/wiki/Web_colors#Hex_triplet)
    to a Linear RGB with an Alpha passed as a parameter

    Supports: "#RRGGBB" or "RRGGBB"

    Video Tutorial: https://www.youtube.com/watch?v=knc1CGBhJeU
    """
    linear_red, linear_green, linear_blue = hex_color_to_rgb(hex_color)
    return tuple([linear_red, linear_green, linear_blue, alpha])

def create_reflective_material(color, name=None, roughness=0.1, specular=0.5, return_nodes=False):
    if name is None:
        name = ""

    material = bpy.data.materials.new(name=f"material.reflective.{name}")
    material.use_nodes = True

    material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = color
    material.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = roughness
    material.node_tree.nodes["Principled BSDF"].inputs["Specular"].default_value = specular

    if return_nodes:
        return material, material.node_tree.nodes
    else:
        return material

#--------------------------------------

clean_scene()

color_list = [
            "#E7434F",
            "#E7434F",
            "#E7973D",
            "#E7DC4E",
            "#5CE75D",
            "#2981E7",
            "#5D21E7",
            "#E777E4",
            "#E7E7E7",
            "#131313",
        ]
        
shape = 2   # shape 1, shape 2

color1 = random.choice(color_list)
color2 = random.choice(color_list)
color3 = random.choice(color_list)
color4 = random.choice(color_list)

#create shape 1
if shape == 1:
    #create cone without bottom
    bpy.ops.mesh.primitive_plane_add(size=0.2, enter_editmode=True, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0.1), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable_only":False, "use_snap_to_same_target":False, "snap_face_nearest_steps":1, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
    bpy.ops.mesh.merge(type='CENTER')
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.shade_smooth()



#create shape 2 - part 1
if shape == 2:
    # create cube without top and bottom
    bpy.ops.mesh.primitive_plane_add(size=0.1, enter_editmode=True, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0.2), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable_only":False, "use_snap_to_same_target":False, "snap_face_nearest_steps":1, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.shade_smooth()

    
    

# create and apply material 1
candy = bpy.context.active_object
material = create_reflective_material(hex_color_to_rgba(color1, alpha=1.0), name="mat 1", roughness=0.1, specular=0.5, return_nodes=False)
candy.data.materials.append(material)


# create material 2    
material = create_reflective_material(hex_color_to_rgba(color2, alpha=1.0), name="mat 2", roughness=0.1, specular=0.5, return_nodes=False)
candy.data.materials.append(material)
    
#Set active material
candy.active_material_index = 1

#Set active face
bpy.ops.object.editmode_toggle()

bpy.ops.mesh.select_all(action='DESELECT')

candy_bmesh = bmesh.from_edit_mesh(candy.data)
candy_bmesh.faces.ensure_lookup_table()
candy_bmesh.faces[0].select = True
bmesh.update_edit_mesh(candy.data)

# Assign material to active face
bpy.ops.object.material_slot_assign()

# create material 3    
material = create_reflective_material(hex_color_to_rgba(color3, alpha=1.0), name="mat 3", roughness=0.1, specular=0.5, return_nodes=False)
candy.data.materials.append(material)
    
#Set active material
candy.active_material_index = 2
# Set active face and Assign material 
bpy.ops.mesh.select_all(action='DESELECT')
candy_bmesh.faces[1].select = True
bmesh.update_edit_mesh(candy.data)
bpy.ops.object.material_slot_assign()

# create material 4    
material = create_reflective_material(hex_color_to_rgba(color4, alpha=1.0), name="mat 4", roughness=0.1, specular=0.5, return_nodes=False)
candy.data.materials.append(material)
    
#Set active material
candy.active_material_index = 3
# Set active face and Assign material    
bpy.ops.mesh.select_all(action='DESELECT')
candy_bmesh.faces[2].select = True
bmesh.update_edit_mesh(candy.data)
bpy.ops.object.material_slot_assign()

bpy.ops.object.editmode_toggle()
    
    
# create shape 2 - part 2
if shape == 2:
    # Select top vertex

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')
    candy_bmesh = bmesh.from_edit_mesh(candy.data)
   
    for vert in candy_bmesh.verts:
        if vert.co[2] >= 0.1: #if Z position >= 0.1
            candy_bmesh.verts.ensure_lookup_table() 
            candy_bmesh.verts[vert.index].select = True
            bmesh.update_edit_mesh(candy.data)

    # Convert selected vertex to selected edge        
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()        
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
    # Extrude edges and merge at center
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0.02), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable_only":False, "use_snap_to_same_target":False, "snap_face_nearest_steps":1, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
    bpy.ops.mesh.merge(type='CENTER')
    bpy.ops.object.editmode_toggle()

# mirror shape
bpy.ops.object.modifier_add(type='MIRROR')
bpy.context.object.modifiers["Mirror"].use_axis[0] = False
bpy.context.object.modifiers["Mirror"].use_axis[1] = False
bpy.context.object.modifiers["Mirror"].use_axis[2] = True

# candy shape making
bpy.ops.object.modifier_add(type='SUBSURF')
bpy.context.object.modifiers["Subdivision"].levels = 2

bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
bpy.context.object.modifiers["SimpleDeform"].deform_axis = 'Z'
if shape == 1:
    bpy.context.object.modifiers["SimpleDeform"].angle = 6.28319
if shape == 2:
    bpy.context.object.modifiers["SimpleDeform"].angle = 6.28319*2

bpy.ops.object.modifier_add(type='SUBSURF')
bpy.context.object.modifiers["Subdivision.001"].levels = 2





