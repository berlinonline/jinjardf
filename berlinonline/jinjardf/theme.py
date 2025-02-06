from importlib.resources.abc import Traversable
import os
import sys
from abc import ABC
from importlib.resources import files
import logging
from posixpath import dirname
from pathlib import Path

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


class Theme(ABC):
    """A theme contains templates for use with the JinjaRDF site builder.
    `Theme` is an abstract base class and should be sub-classed for concrete
    themes.

    Attributes:
        name (str): A human-readable name of the theme. Default is the class name.
        module_path (str): The complete path to the theme in dot-notation.
        dir_path (importlib.resources.abc.Traversable): The location of this theme.
        template_path (str): The template path relative to the theme.
        Defaults to 'template'.
    """
    name: str
    module_path: str
    dir_path: Traversable
    template_path: str

    def __init__(self, name: str=None, template_path: str='templates'):
        """Initialize the theme

        Args:
            name (str, optional): Optional human-readable theme name. If none, then theme.name
            will be the name of the theme class. Defaults to None.
            template_path (str, optional): The template path relative to the theme class (this class).
            Defaults to 'templates'.
        """
        calling_class = type(self)
        modulename = calling_class.__module__
        classname = calling_class.__qualname__
        self.module_path = modulename + '.' + classname

        current_dir = dirname(sys.modules[modulename].__file__)
        template_folder_path = os.path.join(current_dir, template_path)
        self.template_path = template_folder_path

        if not name:
            name = classname
        self.name = name

        # where is the concrete subclass located?
        self.dir_path = files(modulename)

    def copy_templates(self, target_folder: str):
        """Copy the theme's templates to a subfolder in the site generator's
        template folder.

        Args:
            target_folder (str): the site generator's template folder
        """
        for file in self.dir_path.iterdir():
            if str(file) == str(self.template_path):
                theme_template_folder = os.path.join(target_folder, self.module_path)
                if not os.path.exists(theme_template_folder):
                    os.makedirs(theme_template_folder)
                for template in file.iterdir():
                    if template.is_file():
                        target_path = os.path.join(theme_template_folder, os.path.basename(str(template)))
                        destination = Path(target_path)
                        destination.write_text(template.read_text())
