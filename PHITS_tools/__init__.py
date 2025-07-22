from .PHITS_tools import *

import importlib.util
import os, sys

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if not os.path.exists(os.path.join(base_dir, "DCHAIN-Tools")):
    base_dir = os.path.join(base_dir, "..")

submodules = {
    "PHITS_tools.manage_mc_materials": os.path.join(base_dir, "MC_materials", "manage_mc_materials.py"),
    "PHITS_tools.dchain_tools": os.path.join(base_dir, "DCHAIN-Tools", "dchain_tools.py"),
}

for module_name, filepath in submodules.items():
    if module_name not in sys.modules and os.path.exists(filepath):
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

from PHITS_tools import manage_mc_materials, dchain_tools