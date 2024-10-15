import pygltflib
from pygltflib import GLTF2, Scene, Node, EXT_mesh_gpu_instancing, Accessor, BufferView, Buffer, Mesh
import sys

def identify_instancable_meshes(gltf: GLTF2):
    """
    Identify identical meshes that can be instanced. In this simplified case,
    we assume meshes with identical geometry (same buffer views, accessors, etc.)
    can be instanced.
    """
    mesh_to_nodes = {}
    
    # Iterate over nodes and group them by their mesh index
    for node_index, node in enumerate(gltf.nodes):
        if node.mesh is not None:
            if node.mesh not in mesh_to_nodes:
                mesh_to_nodes[node.mesh] = []
            mesh_to_nodes[node.mesh].append(node_index)
    
    # Find meshes with more than one node using them (i.e., possible candidates for instancing)
    instancable_meshes = {mesh: nodes for mesh, nodes in mesh_to_nodes.items() if len(nodes) > 1}
    
    return instancable_meshes

def add_instancing_to_gltf(gltf: GLTF2, instancable_meshes: dict):
    """
    Add EXT_mesh_gpu_instancing to the GLTF for identified instancable meshes.
    """
    if not instancable_meshes:
        print("No instancable meshes found.")
        return
    
    # Ensure extensionsUsed and extensionsRequired are lists
    if not gltf.extensionsUsed:
        gltf.extensionsUsed = []
    if not gltf.extensionsRequired:
        gltf.extensionsRequired = []
    
    # Add the EXT_mesh_gpu_instancing extension
    gltf.extensionsUsed.append("EXT_mesh_gpu_instancing")
    gltf.extensionsRequired.append("EXT_mesh_gpu_instancing")
    
    # Go through each instancable mesh and add instancing data
    for mesh, node_indices in instancable_meshes.items():
        # Create transformation matrices for each instance (position, rotation, scale)
        instance_transforms = []
        for node_index in node_indices:
            node = gltf.nodes[node_index]
            instance_transforms.append(node.matrix if node.matrix else node.translation + node.rotation + node.scale)
        
        # Add the extension with the instance transforms
        instancing_extension = EXT_mesh_gpu_instancing(count=len(instance_transforms), transformations=instance_transforms)
        gltf.meshes[mesh].extensions = {"EXT_mesh_gpu_instancing": instancing_extension}
        
        # Remove the individual nodes, they are now instanced
        for node_index in node_indices[1:]:  # Keep the first node
            gltf.nodes[node_index].mesh = None

def save_gltf(gltf: GLTF2, output_file: str):
    """Save the optimized GLTF file."""
    gltf.save(output_file)

def optimize_gltf_with_instancing(input_file: str, output_file: str):
    # Load the GLTF file
    gltf = GLTF2().load(input_file)
    
    # Identify meshes that can be instanced
    instancable_meshes = identify_instancable_meshes(gltf)
    
    # Apply instancing
    add_instancing_to_gltf(gltf, instancable_meshes)
    
    # Save the optimized GLTF file
    save_gltf(gltf, output_file)
    print(f"Optimized GLTF file saved to {output_file}")

if(len(sys.argv) < 2):
    print("Usage: python gltf_instancing.py input_model.gltf")
    sys.exit(1)

input_gltf_file = sys.argv[1]
output_gltf_file = input_gltf_file.split(".")[:1] + "optimized.gltf"


optimize_gltf_with_instancing(input_gltf_file, output_gltf_file)
