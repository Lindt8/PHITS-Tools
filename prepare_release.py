'''
This script serves to automate production of HTML documentation using [pdoc](https://github.com/pdoc3/pdoc) 
and organizing of files for builing of a release of PHITS Tools.

'''

import pdoc
import shutil
import re
import sys
import subprocess

# PHITS Tools version number for PyPI release and appearing in the documentation.
# https://packaging.python.org/en/latest/specifications/version-specifiers/#pre-releases
VERSION_NUMBER = '1.6.0b3'

build_release = True  # If True, execute "py -m build" at the end of this script

# Build documentation following pdoc instructions: https://pdoc3.github.io/pdoc/doc/pdoc/#programmatic-usage
modules = ['PHITS_tools']
modules += [pdoc.import_module('MC_materials/manage_mc_materials.py')]
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
        html = html.replace('width:70%;max-width:100ch;','width:70%;max-width:120ch;',1) # make page contents wider
        if module_name == 'manage_mc_materials':
            html = html.replace('<h1 class="title">Module <code>manage_mc_materials</code></h1>','<h1 class="title">Submodule <code>manage_mc_materials</code></h1>',1)
            # Replace text where pdoc evaluated function arguments prematurely
            html = re.sub('=WindowsPath?(.*?)b/PHITS-Tools/', "=(Path.cwd()/'", html, flags=re.DOTALL)
        # add version number
        html = html.replace('</code></h1>','</code> <i><small>(v'+VERSION_NUMBER+')</small></i></h1>', 1)
        with open('docs/'+html_file_name, 'w') as f:
            f.write(html)


# Copy all .py files to src/PHITS_tools/ directory for dist building
destination_dir = 'src/PHITS_tools/'
shutil.copy2('PHITS_tools.py', destination_dir)
shutil.copy2('DCHAIN-Tools/dchain_tools.py', destination_dir)
shutil.copy2('MC_materials/manage_mc_materials.py', destination_dir)

# Update version number in pyproject.toml
with open('pyproject.toml','r') as file:
    lines = file.readlines()
    for li, line in enumerate(lines):
        if line[:9] == 'version =':
            lines[li] = 'version = "' + VERSION_NUMBER + '"\n'
with open('pyproject.toml', 'w') as file:
    file.writelines(lines)
    
# Build the release
if build_release:
    subprocess.run([sys.executable, "-m", "build"])