# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = '技术记录'
copyright = '2023, zeroswan'
author = 'zeroswan'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser", 
    "sphinx_design", 
    "sphinx.ext.mathjax", 
    "sphinxcontrib.mermaid",
]
myst_enable_extensions = ["colon_fence", "dollarmath", "attrs_inline"]

templates_path = ['_templates']
exclude_patterns = ['_build', "_draft", 'Thumbs.db', '.DS_Store', '.venv']

language = 'zh_CN'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'sphinx_rtd_theme'
html_theme = 'furo'
html_static_path = ['_static']

source_suffix = ['.rst', '.md']

myst_dmath_allow_labels = True
myst_heading_anchors = 3

latex_engine = "xelatex"
latex_use_xindy = False
latex_elements = {
    "preamble": "\\usepackage[UTF8]{ctex}\n",
}
