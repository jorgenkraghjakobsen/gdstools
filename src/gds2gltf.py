#!/usr/bin/env python3
"""
This program converts a GDSII 2D layout file to a glTF 3D file

USAGE:
    - edit the "layerstack" variable in the "CONFIGURATION" section below
    - run "gdsiigtlf file.gds"
OUTPUT:
    - the files file.gds.gltf

The program takes one argument, a path to a GDSII file. It reads shapes from
each layer of the GDSII file, converts them to polygon boundaries, then makes
a triangle mesh for each GDSII layer by extruding the polygons to given sizes.

All units, including the units of the exported file, are the GDSII file's
user units (often microns).
"""

import sys # read command-line arguments
import gdspy # open gds file
import numpy as np # fast math on lots of points
import triangle # triangulate polygons
import time 

import pygltflib
from pygltflib import BufferFormat
from pygltflib.validator import validate, summary
from pygltflib.utils import gltf2glb

def read_layerstack_from_file(filename):
    """Reads a layerstack from a text file.

    The text file should contain lines in the following format:

    layer_name gds_number gds_datatype zmin zmax color_r color_g color_b color_a

    Example:

    substrate 245 0 -1 0 0.2 0.2 0.2 1.0
    nwell 21 0 0.1 0.4 0.4 0.4 1.0 
    ...

    Args:
        filename: The name of the text file containing the layerstack.

    Returns:
        A dictionary representing the layerstack.
    """

    layerstack = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip comments
                layer_name, gds_number, gds_datatype, zmin, zmax, color_r, color_g, color_b, color_a = line.split()
                layerstack[(int(gds_number), int(gds_datatype))] = {
                    'gds_number': int(gds_number),
                    'gds_datatype': int(gds_datatype), 
                    'name': layer_name,
                    'zmin': float(zmin),
                    'zmax': float(zmax),
                    'color': [float(color_r), float(color_g), float(color_b), float(color_a)]
                }
    
    return layerstack

def export_glb(gltf_filename):
    # glb_filename = gltf_filename.replace(".gltf", ".glb")
    gltf2glb(gltf_filename)
    print(f"GLB file saved as {gltf_filename.replace('.gltf', '.glb')}")

def remove_duplicates(polygon, edges, tol=1e-6):
    """
    Removes duplicate or nearly identical vertices from the polygon and updates the edges list.
    
    Args:
        polygon (list of lists): List of vertices (2D points).
        edges (list of lists): List of edges (pairs of vertex indices).
        tol (float): Tolerance for determining if two vertices are identical (default 1e-6).
        
    Returns:
        new_polygon (list of lists): Deduplicated list of vertices.
        new_edges (list of lists): Updated list of edges using new vertex indices.
    """
    # Convert the polygon list to a numpy array for efficient distance calculation
    polygon_np = np.array(polygon)
    
    # List to store unique vertices
    new_polygon = []
    # Dictionary to map old vertex index to new index after removing duplicates
    vertex_map = {}
    
    # Loop over the polygon vertices
    for i, vertex in enumerate(polygon_np):
        # Check if the vertex is close to any of the already added unique vertices
        found_duplicate = False
        for j, unique_vertex in enumerate(new_polygon):
            if np.linalg.norm(vertex - unique_vertex) < tol:  # Compare using tolerance
                vertex_map[i] = j  # Map the old index to the existing unique vertex index
                found_duplicate = True
                break
        
        # If no duplicate is found, add the vertex to the new polygon
        if not found_duplicate:
            vertex_map[i] = len(new_polygon)  # Map the old index to the new unique index
            new_polygon.append(vertex)
    
    # Convert the unique vertices list back to a regular list
    new_polygon = np.array(new_polygon).tolist()
    
    # Update the edges with the new vertex indices
    new_edges = []
    for edge in edges:
        new_edges.append([vertex_map[edge[0]], vertex_map[edge[1]]])
    
    return new_polygon, new_edges


# get the input file name
if len(sys.argv) < 3:
    print("Error: need exactly two files as command line arguments: GDSII file and layerstack file.")
    sys.exit(0)

gdsii_file_path = sys.argv[1]
layerstack_file_path = sys.argv[2]

########## INPUT ##############################################################

# First, the input file is read using the gdspy library, which interprets the
# GDSII file and formats the data Python-style.
# See https://gdspy.readthedocs.io/en/stable/index.html for documentation.
# Second, the boundaries of each shape (polygon or path) are extracted for
# further processing.

# Read the layerstack from the text file
print('Reading layerstack file {}...'.format(layerstack_file_path))
layerstack = read_layerstack_from_file(layerstack_file_path)

print('Reading GDSII file {}...'.format(gdsii_file_path))
gdsii = gdspy.GdsLibrary()
gdsii.read_gds(gdsii_file_path, units='import')


gltf = pygltflib.GLTF2()
scene = pygltflib.Scene()
gltf.scenes.append(scene)
buffer = pygltflib.Buffer()
gltf.buffers.append(buffer)

for layer in layerstack:
    mainMaterial = pygltflib.Material()
    mainMaterial.doubleSided = True
    mainMaterial.name = layerstack[layer]['name']
    mainMaterial.pbrMetallicRoughness =  {
                    "baseColorFactor": layerstack[layer]['color'],
                    "metallicFactor": 0.5,
                    "roughnessFactor": 0.5
                }
    gltf.materials.append(mainMaterial)

binaryBlob = bytes()

print('Extracting polygons...')

meshes_lib = {}

for cell in gdsii.cells.values(): # loop through cells to read paths and polygons
    layers = {} # array to hold all geometry, sorted into layers
    
    start_time = time.time()
    print ("\nProcessing cell: ", cell.name)
    
    # $$$CONTEXT_INFO$$$ is a separate, non-standard compliant cell added
    # optionally by KLayout to store extra information not needed here.
    # see https://www.klayout.de/forum/discussion/1026/very-
    # important-gds-exported-from-k-layout-not-working-on-cadence-at-foundry
    if cell.name == '$$$CONTEXT_INFO$$$':
        continue # skip this cell

    print ("\tpaths loop. total paths:" , len(cell.paths))
    # loop through paths in cell
    for path in cell.paths:
        lnum = (path.layers[0],path.datatypes[0]) # GDSII layer number
        
        if not lnum in layerstack.keys():
            continue

        layers[lnum] = [] if not lnum in layers else layers[lnum]
        # add paths (converted to polygons) that layer
        for poly in path.get_polygons():
            layers[lnum].append((poly, None, False))

    print ("\tpolygons loop. total polygons:" , len(cell.polygons))

    for polygon in cell.polygons:
        # Get the first layer and datatype of the polygon
        layer_and_type = (polygon.layers[0], polygon.datatypes[0])

        # If the layer-datatype pair is not in the layerstack, skip to the next polygon
        if layer_and_type not in layerstack:
            continue

        # Ensure the 'layers' dictionary has an entry for the current layer-datatype pair
        if layer_and_type not in layers:
            layers[layer_and_type] = []

        # Loop through each individual polygon in the polygon object
        for sub_polygon in polygon.polygons:
            # Append the sub-polygon to the layers dictionary with placeholder values
            layers[layer_and_type].append((sub_polygon, None, False))

    """
    At this point, "layers" is a Python dictionary structured as follows:

    layers = {
    0 : [ ([[x1, y1], [x2, y2], ...], None, False), ... ]
    1 : [ ... ]
    2 : [ ... ]
    ...
    }

    Each dictionary key is a GDSII layer number (0-255), and the value of the
    dictionary at that key (if it exists; keys were only created for layers with
    geometry) is a list of polygons in that GDSII layer. Each polygon is a 3-tuple
    whose first element is a list of points (2-element lists with x and y
    coordinates), second element is None (for the moment; this will be used later),
    and third element is False (whether the polygon is clockwise; will be updated).
    """

    ########## TRIANGULATION ######################################################

    # An STL file is a list of triangles, so the polygons need to be filled with
    # triangles. This is a surprisingly hard algorithmic problem, especially since
    # there are few limits on what shapes GDSII file polygons can be. So we use the
    # Python triangle library (documentation is at https://rufat.be/triangle/),
    # which is a Python interface to a fast and well-written C library also called
    # triangle (with documentation at https://www.cs.cmu.edu/~quake/triangle.html).

    print('\tTriangulating polygons...')

    
    num_triangles = {} # will store the number of triangles for each layer
    print(f"\t{len(layers)} layers found")
    # loop through all layers
    for layer_number, polygons in layers.items():
        print(f"\tLayer {layer_number} has {len(polygons)} polygons, name: {layerstack[layer_number]['name']}")
        # print(f"\tLayer name: {layerstack[layer_number]['name']}")
        # print(f"\tLayer {layer_number} has {len(polygons)} polygons")
        # but skip layer if it won't be exported
        if not layer_number in layerstack.keys():
            continue

        num_triangles[layer_number] = 0

        # loop through polygons in layer
        for index, (polygon, _, _) in enumerate(polygons):
            num_polygon_points = len(polygon)

            # determine whether polygon points are CW or CCW
            area = 0
            for i, v1 in enumerate(polygon): # loop through vertices
                v2 = polygon[(i+1) % num_polygon_points]
                area += (v2[0]-v1[0])*(v2[1]+v1[1]) # integrate area
            clockwise = area > 0

            # GDSII implements holes in polygons by making the polygon edge
            # wrap into the hole and back out along the same line. However,
            # this confuses the triangulation library, which fills the holes
            # with extra triangles. Avoid this by moving each edge back a
            # very small amount so that no two edges of the same polygon overlap.
            # Define a small threshold to avoid division by very small numbers (to prevent NaNs or infinities)

            epsilon = 1e-8  
            delta = 0.00001  # Amount to inset each vertex by (smaller values have caused issues in the past)

            # Step 1: Extract polygon points
            points_i = polygon  # Get the list of points representing the polygon vertices

            # Step 2: Shift points to get neighbors
            points_j = np.roll(points_i, -1, axis=0)  # Shift points forward by 1 (next point)
            points_k = np.roll(points_i, 1, axis=0)   # Shift points backward by 1 (previous point)

            # Step 3: Calculate normals for edges (between consecutive vertices)
            # Normal between current and next vertex (i -> j)
            normal_ij = np.stack((points_j[:, 1] - points_i[:, 1],  # y-component difference
                                points_i[:, 0] - points_j[:, 0]), axis=1)  # x-component difference (perpendicular)

            # Normal between current and previous vertex (i -> k)
            normal_ik = np.stack((points_i[:, 1] - points_k[:, 1],  # y-component difference
                                points_k[:, 0] - points_i[:, 0]), axis=1)  # x-component difference (perpendicular)

            # Step 4: Compute the lengths of these normal vectors
            length_ij = np.linalg.norm(normal_ij, axis=1)
            length_ik = np.linalg.norm(normal_ik, axis=1)

            # Step 5: Handle small lengths to avoid division by near-zero values
            length_ij[length_ij < epsilon] = 1  # Set very small lengths to 1 to avoid division issues
            length_ik[length_ik < epsilon] = 1  # Set very small lengths to 1

            # Step 6: Normalize the normals (unit vectors)
            normal_ij /= np.stack((length_ij, length_ij), axis=1)  # Normalize by dividing by length
            normal_ik /= np.stack((length_ik, length_ik), axis=1)  # Normalize by dividing by length

            # Step 7: Adjust direction of normals if polygon is oriented clockwise
            if clockwise:
                normal_ij = -normal_ij  # Reverse direction for clockwise orientation
                normal_ik = -normal_ik

            # Step 8: Move each vertex inward by 'delta' along its two edge normals
            # Each vertex is moved inward along both the normal to its adjacent edges
            polygon = points_i - delta * normal_ij - delta * normal_ik

            # In an extreme case of the above, the polygon edge doubles back on
            # itself on the same line, resulting in a zero-width segment. I've
            # seen this happen, e.g., with a capital "N"-shaped hole, where
            # the hole split line cuts out the "N" shape but splits apart to
            # form the triangle cutout in one side of the shape. In any case,
            # simply moving the polygon edges isn't enough to deal with this;
            # we'll additionally mark points just outside of each edge, between
            # the original edge and the delta-shifted edge, as outside the polygon.
            # These parts will be removed from the triangulation, and this solves
            # just this case with no adverse affects elsewhere.
            hole_delta = 0.00001 # small fraction of delta
            holes = 0.5*(points_j+points_i) - hole_delta*delta*normal_ij
            # HOWEVER: sometimes this causes a segmentation fault in the triangle
            # library. I've observed this as a result of certain various polygons.
            # Frustratingly, the fault can be bypassed by *rotating the polygons*
            # by like 30 degrees (exact angle seems to depend on delta values) or
            # moving one specific edge outward a bit. I have absolutely no idea
            # what is wrong. In the interest of stability over full functionality,
            # this is disabled. TODO: figure out why this happens and fix it.
            use_holes = False


            # triangulate: compute triangles to fill polygon
            point_array = np.arange(num_polygon_points)

            edges = np.transpose(np.stack((point_array, np.roll(point_array, 1))))
            polygon, edges = remove_duplicates(polygon, edges)
            
            if use_holes:
                triangles = triangle.triangulate(dict(vertices=polygon,
                                                    segments=edges,
                                                    holes=holes), opts='p')
            else:
                triangles = triangle.triangulate(dict(vertices=polygon,
                                                    segments=edges), opts='p')

            if not 'triangles' in triangles.keys():
                triangles['triangles'] = []

            # each line segment will make two triangles (for a rectangle), and the polygon
            # triangulation will be copied on the top and bottom of the layer.
            num_triangles[layer_number] += num_polygon_points*2 + \
                                        len(triangles['triangles'])*2
            polygons[index] = (polygon, triangles, clockwise)

        # glTF Mesh creation

        zmin = layerstack[layer_number]['zmin']
        zmax = layerstack[layer_number]['zmax']
        layername = layerstack[layer_number]['name']
        node_name = cell.name + "_" + layername

        gltf_positions = []
        gltf_indices = []        
        indices_offset = 0
        for i,(_, poly_data, clockwise) in enumerate(polygons):         

            
            p_positions_top = np.insert(poly_data['vertices'], 2, zmax, axis=1)
            p_positions_bottom = np.insert( poly_data['vertices'] , 2, zmin, axis=1)
            
            p_positions = np.concatenate( (p_positions_top, p_positions_bottom) )
            p_indices_top = poly_data['triangles']
            p_indices_bottom = np.flip ((p_indices_top+len(p_positions_top)), axis=1 )
            
            ind_list_top = np.arange(len(p_positions_top))
            ind_list_bottom = np.arange(len(p_positions_top)) + len(p_positions_top)

            if(clockwise):
                ind_list_top = np.flip(ind_list_top, axis=0)
                ind_list_bottom = np.flip(ind_list_bottom, axis=0)

            p_indices_right = np.stack( (ind_list_bottom, np.roll(ind_list_bottom, -1, axis=0) , np.roll(ind_list_top, -1, axis=0)), axis=1 )
            p_indices_left = np.stack( ( np.roll(ind_list_top, -1, axis=0), ind_list_top , ind_list_bottom ) , axis=1)
                 
            p_indices = np.concatenate( (p_indices_top, p_indices_bottom, p_indices_right, p_indices_left) )

            if(len(gltf_positions)==0):
                gltf_positions = p_positions
            else:
                gltf_positions = np.append(gltf_positions , p_positions, axis=0)
            if(len(gltf_indices)==0):
                gltf_indices = p_indices
            else:    
                gltf_indices = np.append(gltf_indices, p_indices + indices_offset, axis=0)            
            indices_offset += len(p_positions)
      
        
        indices_binary_blob = gltf_indices.astype(np.uint32).flatten().tobytes() #triangles.flatten().tobytes()
        positions_binary_blob = gltf_positions.astype(np.float32).tobytes() #points.tobytes()

        bufferView1 = pygltflib.BufferView()
        bufferView1.buffer = 0
        bufferView1.byteOffset = len(binaryBlob)
        bufferView1.byteLength = len(indices_binary_blob)
        bufferView1.target = pygltflib.ELEMENT_ARRAY_BUFFER
        gltf.bufferViews.append(bufferView1)

        accessor1 = pygltflib.Accessor()
        accessor1.bufferView = len(gltf.bufferViews)-1
        accessor1.byteOffset = 0
        accessor1.componentType = pygltflib.UNSIGNED_INT
        accessor1.type = pygltflib.SCALAR
        accessor1.count = gltf_indices.size
        accessor1.max = [int(gltf_indices.max())]
        accessor1.min = [int(gltf_indices.min())]
        gltf.accessors.append(accessor1)

        binaryBlob = binaryBlob + indices_binary_blob

        bufferView2 = pygltflib.BufferView()
        bufferView2.buffer = 0
        bufferView2.byteOffset = len(binaryBlob)
        bufferView2.byteLength = len(positions_binary_blob)
        bufferView2.target = pygltflib.ARRAY_BUFFER
        gltf.bufferViews.append(bufferView2)

        positions_count = len(gltf_positions)
        accessor2 = pygltflib.Accessor()
        accessor2.bufferView =  len(gltf.bufferViews)-1
        accessor2.byteOffset = 0
        accessor2.componentType = pygltflib.FLOAT
        accessor2.count = positions_count
        accessor2.type = pygltflib.VEC3
        accessor2.max = gltf_positions.max(axis=0).tolist()
        accessor2.min = gltf_positions.min(axis=0).tolist()

        gltf.accessors.append(accessor2)
        # print("BBLOB: " + positions_binary_blob)
        binaryBlob = binaryBlob + positions_binary_blob

        mesh = pygltflib.Mesh()
        mesh_primitive = pygltflib.Primitive()
        mesh_primitive.indices = len(gltf.accessors)-2
        mesh_primitive.attributes.POSITION = len(gltf.accessors)-1

        mesh_primitive.material = list(layerstack).index(layer_number)

        mesh.primitives.append(mesh_primitive)


        gltf.meshes.append(mesh)
        meshes_lib[node_name] = len(gltf.meshes)-1

    end_time = time.time()
    elapsed_time = end_time - start_time
    poly = len(cell.polygons)

    if poly != 0 :
        print(f"Function took {elapsed_time:.5f} seconds {poly} polygons ({(elapsed_time/poly*1000):.3f}) ")   
    else:
        Warning("No polygons found in cell: " + cell.name)

    len(cell.polygons)

gltf.set_binary_blob(binaryBlob)
print(f"Binary blob size: {len(binaryBlob)} bytes")

buffer.byteLength = len(binaryBlob)
gltf.convert_buffers(BufferFormat.DATAURI)

done_time = time.time()
done_elapsed_time = done_time - end_time
print(f"store took: {done_elapsed_time:.5f} seconds")

def add_cell_node(c, parent_node, prefix):
    for ref in c.references:
        instance_node = pygltflib.Node()
        instance_node.extras = {}
        instance_node.extras["type"] = ref.ref_cell.name;
        if(ref.properties.get(61)==None):
            # ref.ref_cell.name
            instance_node.name = "???"; 
        else:
            instance_node.name = ref.properties[61]
            
        #print(prefix, instance_node.name, "(", ref.ref_cell.name + ")")
        instance_node.translation = [ref.origin[0], ref.origin[1], 0]
        if(ref.rotation!=None):
            if(ref.rotation==90):
                instance_node.rotation = [ 0, 0, 0.7071068, 0.7071068 ]
            elif(ref.rotation==180):
                instance_node.rotation = [ 0, 0, 1, 0 ]
            elif(ref.rotation==270):
                instance_node.rotation = [ 0, 0, 0.7071068, -0.7071068 ]
        if(ref.x_reflection):
            instance_node.scale = [1,-1,1]

        for layer in layerstack.values():
            lib_name = ref.ref_cell.name + "_" + layer['name']
            if(meshes_lib.get(lib_name)!=None):
                layer_node = pygltflib.Node()
                layer_node.name = lib_name
                layer_node.mesh = meshes_lib[lib_name]
                gltf.nodes.append(layer_node)
                instance_node.children.append(len(gltf.nodes)-1)
        
        if(len(ref.ref_cell.references)>0):
            add_cell_node(ref.ref_cell, instance_node, prefix + "\t")

        gltf.nodes.append(instance_node)
        parent_node.children.append(len(gltf.nodes)-1)


main_cell = gdsii.top_level()[0]

root_node = pygltflib.Node()
root_node.name = main_cell.name #"ROOT"
gltf.nodes.append(root_node)

print ("\nBuilding Scenegraph:")
print(root_node.name)

add_cell_node(main_cell, root_node, "\t")
    

for layer in layerstack.values():
    lib_name = main_cell.name + "_" + layer['name']
    if(meshes_lib.get(lib_name)!=None):
        layer_node = pygltflib.Node()
        layer_node.name =lib_name
        layer_node.mesh = meshes_lib[lib_name]
        gltf.nodes.append(layer_node)
        root_node.children.append(len(gltf.nodes)-1)




scene.nodes.append(0)
gltf.scene = 0

##validate(gltf)  # will throw an error depending on the problem
#summary(gltf) 


print ("\nWriting glTF file:")
gltf.save(gdsii_file_path + ".gltf")
# gltf.save("output.gltf")
#export_glb(gdsii_file_path + ".glb")

print('Done.')