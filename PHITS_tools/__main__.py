import runpy
import sys
import importlib.util

spec = importlib.util.find_spec("PHITS_tools.PHITS_tools")
if spec and spec.origin:
    sys.argv[0] = spec.origin  # mimic running the module file directly; i.e., `python PHITS_tools/PHITS_tools.py`

sys.modules.pop("PHITS_tools.PHITS_tools", None)  # Ensure it isn't already imported to avoid RuntimeWarning
runpy.run_module("PHITS_tools.PHITS_tools", run_name="__main__")  # Execute as __main__
