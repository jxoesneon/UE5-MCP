import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock Blender modules before importing the server script
sys.modules["bpy"] = MagicMock()
sys.modules["bmesh"] = MagicMock()
sys.modules["mathutils"] = MagicMock()

# Load the blender_server script as a module
SERVER_PATH = Path("modules/mcp_target_blender/scripts/blender_server.py").resolve()

def load_blender_server():
    spec = importlib.util.spec_from_file_location("blender_server", SERVER_PATH)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules["blender_server"] = module
        spec.loader.exec_module(module)
        return module
    raise ImportError("Could not load blender_server.py")

blender_server = load_blender_server()

def test_generate_scene_determinism():
    """Verify generate_scene respects seed."""
    params = {
        "description": "Test Scene",
        "seed": 42
    }
    
    # We want to verify that random.seed is called with 42
    with patch("random.seed") as mock_seed:
        blender_server.handle_generate_scene(params)
        mock_seed.assert_called_with(42)

def test_generate_texture_determinism():
    """Verify generate_texture respects seed."""
    params = {
        "object_name": "Cube",
        "texture_type": "diffuse",
        "seed": 12345
    }
    
    # Mock bpy.data.objects.get to return a mock object
    mock_obj = MagicMock()
    mock_obj.data.materials = []
    
    # Setup mock node tree
    mock_mat = MagicMock()
    mock_bsdf = MagicMock()
    mock_mat.node_tree.nodes.get.return_value = mock_bsdf
    
    # When creating new material
    sys.modules["bpy"].data.materials.new.return_value = mock_mat
    sys.modules["bpy"].data.objects.get.return_value = mock_obj

    # Verify random.seed is called
    # Note: currently handle_generate_texture might NOT invoke random.seed, 
    # so this test might fail, which is expected for TDD/Regression.
    with patch("random.seed") as mock_seed:
        # We also need to patch random.random inside the module if it was imported via from
        # but the script uses 'import random' inside the function in handle_generate_scene
        # check handle_generate_texture
        
        # handle_generate_texture does:
        # import random
        # color = ...
        
        # Since 'import random' happens inside the function, we can patch 'random' globally?
        # Or since we patch 'random.seed', it should work if it uses the standard random module.
        
        blender_server.handle_generate_texture(params)
        mock_seed.assert_called_with(12345)
