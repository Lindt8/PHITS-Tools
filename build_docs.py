'''
This script serves to automate production of HTML documentation for PHITS Tools using [pdoc](https://github.com/pdoc3/pdoc) 
'''

import pdoc
import os
import re

# PHITS Tools version number appearing in the documentation.
# https://packaging.python.org/en/latest/specifications/version-specifiers/#pre-releases
def get_version_from_module(path):
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith("__version__ ="):
                return line.split("=", 1)[1].strip().strip("\"'")
    raise RuntimeError("Version string not found.")
VERSION_NUMBER = get_version_from_module('PHITS_tools/PHITS_tools.py')

output_dir = "build/docs"
os.makedirs(output_dir, exist_ok=True)

# Build documentation following pdoc instructions: https://pdoc3.github.io/pdoc/doc/pdoc/#programmatic-usage
modules = ['PHITS_tools/PHITS_tools.py'] 
modules += ['MC_materials/manage_mc_materials.py']
context = pdoc.Context()
modules = [pdoc.Module(mod, context=context) for mod in modules]
pdoc.link_inheritance(context)

def recursive_htmls(mod):
    yield mod.name, mod.html(sort_identifiers=False)
    for submod in mod.submodules():
        yield from recursive_htmls(submod)

for mod in modules:
    for module_name, html in recursive_htmls(mod):
        if module_name == 'PHITS_tools':
            html_file_name = 'index.html'
        else:
            html_file_name = module_name + '.html'
        html = html.replace('width:70%;max-width:100ch;', 'width:70%;max-width:120ch;',1)  # make page contents wider
        if module_name == 'manage_mc_materials':
            html = html.replace('<h1 class="title">Module <code>manage_mc_materials</code></h1>','<h1 class="title">Submodule <code>manage_mc_materials</code></h1>',1)
            # Replace text where pdoc evaluated function arguments prematurely
            html = re.sub('=WindowsPath?(.*?)b/PHITS-Tools/', "=(Path.cwd()/'", html, flags=re.DOTALL)
            html = re.sub('=PosixPath?(.*?)/PHITS-Tools/', "=(Path.cwd()/'", html, flags=re.DOTALL)
        # add version number
        html = html.replace('</code></h1>','</code> <i><small>(v'+VERSION_NUMBER+')</small></i></h1>', 1)
        with open(os.path.join(output_dir, html_file_name), 'w') as f:
            f.write(html)

# Make CNAME file for use with custom domain name
with open(os.path.join(output_dir, "CNAME"), "w") as f:
    f.write("hratliff.com\n")
