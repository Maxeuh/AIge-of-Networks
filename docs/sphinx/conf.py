import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
project = 'AIge of EmpAIres'
copyright = '2025 - INSA Centre Val de Loire'
author = 'KRILL Maxence, MUNT-BURON Killian, NGUYEN Dinh Huy, NGUYEN Nhat Lam, OUSEGGUA Mehdi, STOLL Nicolas'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme'
]

# -- Options for autodoc extension -------------------------------------------
with open('../../requirements.txt') as f:
    autodoc_mock_imports = f.read().splitlines()

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': True,
    'special-members': True,
    'inherited-members': True,
    'show-inheritance': True,
    'exclude-members': '__dict__, __firstlineno__, __module__, __static_attributes__, __weakref__, __annotations__, __abstractmethods__, __abc_impl'
}

# -- Options for napoleon extension ------------------------------------------

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'