import json
import sys
import traceback

# Ensure we can import bpy
try:
    import bpy
    # bmesh and mathutils are commonly used in Blender scripts but seemingly unused here.
    # Keeping them commented out if needed later, or just removing to satisfy linter.
    # import bmesh
    # from mathutils import Vector
except ImportError:
    # This script must be run from within Blender
    sys.stderr.write("Error: This script must be run from within Blender.\n")
    sys.exit(1)

def log(message):
    """Log to stderr so it doesn't interfere with stdout JSON."""
    sys.stderr.write(f"[BlenderServer] {message}\n")
    sys.stderr.flush()

def handle_generate_scene(params):
    """
    Clear the scene and set up a basic environment.
    """
    log(f"Generating scene: {params}")

    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Add a floor plane
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
    plane = bpy.context.active_object
    plane.name = "Floor"

    # Add a light
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))

    # Add a camera
    bpy.ops.object.camera_add(location=(10, -10, 8), rotation=(0.8, 0, 0.8))
    bpy.context.scene.camera = bpy.context.active_object

    seed = params.get("seed")
    if seed is not None:
        import random
        random.seed(seed)

    # Process explicit object list if provided
    created_objects = []
    objects_data = params.get("objects", [])
    if objects_data:
        for obj_data in objects_data:
            # Re-use add_object logic or call it directly
            # We map the dictionary to what handle_add_object expects
            try:
                result = handle_add_object(obj_data)
                created_objects.append(result["object_name"])
            except Exception as e:
                log(f"Failed to add object {obj_data}: {e}")

    return {
        "message": f"Scene generated: {params.get('description')}",
        "objects_count": len(bpy.data.objects),
        "created_objects": created_objects
    }

def handle_add_object(params):
    """
    Add a primitive object.
    """
    log(f"Adding object: {params}")
    obj_type = params.get("object_type", "Cube").lower()
    location = params.get("location", {"x": 0, "y": 0, "z": 0})
    loc_vec = (location.get("x", 0), location.get("y", 0), location.get("z", 0))

    if "cube" in obj_type:
        bpy.ops.mesh.primitive_cube_add(location=loc_vec)
    elif "sphere" in obj_type:
        bpy.ops.mesh.primitive_uv_sphere_add(location=loc_vec)
    elif "plane" in obj_type:
        bpy.ops.mesh.primitive_plane_add(location=loc_vec)
    elif "cylinder" in obj_type:
        bpy.ops.mesh.primitive_cylinder_add(location=loc_vec)
    elif "cone" in obj_type:
        bpy.ops.mesh.primitive_cone_add(location=loc_vec)
    elif "monkey" in obj_type or "suzanne" in obj_type:
        bpy.ops.mesh.primitive_monkey_add(location=loc_vec)
    else:
        # Default to cube
        bpy.ops.mesh.primitive_cube_add(location=loc_vec)

    obj = bpy.context.active_object
    obj.name = f"{obj_type.capitalize()}_{len(bpy.data.objects)}"

    return {
        "message": f"Added object: {obj.name}",
        "object_name": obj.name,
        "location": loc_vec
    }

def handle_generate_texture(params):
    """
    Create a simple material and assign it.
    """
    log(f"Generating texture: {params}")
    object_name = params.get("object_name")
    texture_type = params.get("texture_type", "diffuse")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    if not obj.data.materials:
        mat = bpy.data.materials.new(name=f"{object_name}_Mat")
        obj.data.materials.append(mat)
    else:
        mat = obj.data.materials[0]

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")

    # Clear existing nodes connected to Base Color if any, or just add new ones
    # For simplicity, we just add.

    texture_path = params.get("texture_path")
    if texture_path:
        log(f"Loading texture from {texture_path}")
        try:
            tex_image_node = nodes.new('ShaderNodeTexImage')
            tex_image_node.location = (-300, 0)

            # Load image
            image = bpy.data.images.load(texture_path)
            tex_image_node.image = image

            if bsdf:
                links.new(tex_image_node.outputs['Color'], bsdf.inputs['Base Color'])

            return {
                "message": f"Applied texture from '{texture_path}' to '{object_name}'",
                "texture_path": texture_path
            }
        except Exception as e:
            log(f"Failed to load texture: {e}")
            # Fallback to random color

    import random
    seed = params.get("seed")
    if seed is not None:
        log(f"Seeding random with {seed}")
        random.seed(seed)

    color = (random.random(), random.random(), random.random(), 1)

    if bsdf:
        bsdf.inputs["Base Color"].default_value = color

    return {
        "message": f"Generated texture '{texture_type}' for '{object_name}'",
        "color": color
    }

def handle_export_asset(params):
    """
    Export the specified object or scene.
    """
    log(f"Exporting asset: {params}")
    filepath = params.get("filepath")
    fmt = params.get("format", "fbx").lower()
    object_name = params.get("object_name")

    if not filepath:
        raise ValueError("Filepath is required")

    # Select object if specified
    if object_name:
        bpy.ops.object.select_all(action='DESELECT')
        obj = bpy.data.objects.get(object_name)
        if obj:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
        else:
            log(f"Warning: Object '{object_name}' not found, exporting selection/scene")

    if fmt == "fbx":
        bpy.ops.export_scene.fbx(filepath=filepath, use_selection=bool(object_name))
    elif fmt == "obj":
        bpy.ops.export_scene.obj(filepath=filepath, use_selection=bool(object_name))
    elif fmt == "gltf":
        bpy.ops.export_scene.gltf(filepath=filepath, use_selection=bool(object_name))
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    return {
        "message": f"Exported to {filepath}",
        "format": fmt
    }

def main():
    log("Server started. Waiting for commands on stdin...")

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line)
            command = request.get("command")
            params = request.get("params", {})
            req_id = request.get("id")

            response = {"id": req_id, "status": "ok", "data": None}

            try:
                if command == "ping":
                    response["data"] = "pong"
                elif command == "generate_scene":
                    response["data"] = handle_generate_scene(params)
                elif command == "add_object":
                    response["data"] = handle_add_object(params)
                elif command == "generate_texture":
                    response["data"] = handle_generate_texture(params)
                elif command == "export_asset":
                    response["data"] = handle_export_asset(params)
                else:
                    raise ValueError(f"Unknown command: {command}")
            except Exception as e:
                log(f"Error handling command {command}: {e}")
                traceback.print_exc(file=sys.stderr)
                response["status"] = "error"
                response["error"] = str(e)

            # Write response
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except json.JSONDecodeError:
            log("Invalid JSON received")
        except Exception as e:
            log(f"Server loop error: {e}")
            break

if __name__ == "__main__":
    main()
