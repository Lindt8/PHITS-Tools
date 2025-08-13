# conftest.py
import os
import sys
from pathlib import Path

# Determine if you want to use the example outputs located in your PHITS distribution for testing
# If True, your PATH variable will be searched for the phits/ directory
# If False, the path specified by path_to_base_phits_test_dir will be used instead (it will also be used if phits is not found in your PATH)
use_default_phits_dist_files_for_testing = True
path_to_base_phits_test_dir = Path(r'C:\phits')

phits_base_path = None
for p in os.get_exec_path():
    if "phits" in p.lower():
        path = Path(p).resolve()
        if path.name == "bin" and path.parent.name.lower() == "phits":
            phits_base_path = path.parent
            break
        elif path.name.lower() == "phits":
            phits_base_path = path
            break

if phits_base_path:
    path_to_base_phits_test_dir = phits_base_path
    sys.stderr.write("Found phits in PATH, using it for testing: {:}\n".format(phits_base_path))
else:
    sys.stderr.write("phits not found in PATH, falling back to path specified in 'path_to_base_phits_test_dir': {:}\n".format(path_to_base_phits_test_dir))
sys.stderr.flush()
