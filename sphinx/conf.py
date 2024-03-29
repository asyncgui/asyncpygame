# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import importlib.metadata

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = 'asyncpygame'
copyright = '2023, Mitō Nattōsai'
author = 'Mitō Nattōsai'
release = importlib.metadata.version(project)

rst_epilog = """
.. |ja| replace:: 🇯🇵
"""

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    # 'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    # 'sphinx_tabs.tabs',

]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'en'
add_module_names = False
gettext_auto_build = False
gettext_location = False


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "furo"
html_static_path = ['_static']
# html_theme_options = {
#     "use_repository_button": True,
#     "repository_url": r"https://github.com/asyncgui/asyncpygame",
#     "use_download_button": False,
# }


# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration
todo_include_todos = True


# -- Options for intersphinx extension ---------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'kivy': ('https://kivy.org/doc/master', None),
    'trio': ('https://trio.readthedocs.io/en/stable/', None),
    'asyncgui': ('https://asyncgui.github.io/asyncgui/', None),
    'pygame': ('https://pyga.me/docs/', None),
}


# -- Options for autodoc extension ---------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration
# autodoc_mock_imports = ['pygame', ]
autodoc_default_options = {
#    'members': True,
#    'undoc-members': True,
   'show-inheritance': True,
}
# autodoc_type_aliases = {
#     'TimeUnit': 'TimeUnit',
#     'TimerCallback': 'TimerCallback',
# }

# -- Options for tabs extension ---------------------------------------
# https://sphinx-tabs.readthedocs.io/en/latest/
sphinx_tabs_disable_tab_closing = True


import re

def modify_signature(app, what: str, name: str, obj, options, signature, return_annotation: str,
                     prefix="asyncpygame.",
                     len_prefix=len("asyncpygame."),
                     int_pattern = re.compile(r"\bint\b"),
                     group1={'TimerEvent'},
                     # group2={'current_task', 'sleep_forever', 'open_nursery', },
                     # group3={"TaskState." + s for s in "CREATED STARTED CANCELLED FINISHED".split()},
                     # group4={'wait_all_cm', 'wait_any_cm', 'run_as_secondary', 'run_as_primary', 'run_as_daemon', },
                     # group5={'open_nursery', },
                     ):
    if not name.startswith(prefix):
        return (signature, return_annotation, )
    name = name[len_prefix:]
    # if return_annotation is not None:
    #     return_annotation = int_pattern.sub("TimeUnit", return_annotation)
    if name in group1:
        print(f"Hide the signature of {name!r}")
        return ('', None)
    # if name in group2:
    #     print(f"Modify the signature of {name!r}")
    #     return ('()', return_annotation)
    # if name in group4:
    #     print(f"add a return-annotation to {name!r}")
    #     return (signature, '~typing.AsyncContextManager[Task]')
    # if name in group5:
    #     print(f"Modify the return-annotation of {name!r}")
    #     return (signature, return_annotation.replace("AsyncIterator", "AsyncContextManager"))
    return (signature, return_annotation, )


def setup(app):
    app.connect('autodoc-process-signature', modify_signature)
