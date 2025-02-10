import logging
import os
from importlib.resources import files
from pathlib import Path

from berlinonline.jinjardf.helper import is_valid_package_path

LOG = logging.getLogger(__name__)


class Theme(object):
    """A theme contains templates for use with the JinjaRDF site builder.

    Attributes:
        package (str): the full dotted path of the theme's package, e.g. 'foo.bar.basetheme'
        name (str): A human-readable name of the theme. Default is the theme's subpackage,
        e.g. 'basetheme'.
        template_path (str): The template path relative to the theme's package.
        Defaults to 'templates'.
    """
    package: str
    name: str
    template_path: str

    def __init__(self, package: str, name: str=None, template_path: str='templates'):
        """Initialize the theme

        Args:
            package (str): the full dotted path of the theme's package, e.g. 'foo.bar.basetheme'
            name (str): Optional human-readable theme name. If None, then `theme.name`
            will be the name of the theme's subpackage (e.g. 'basetheme').
            Defaults to None.
            template_path (str, optional): The template path relative to the theme's package.
            Defaults to 'templates'.
        """

        if is_valid_package_path(package):
            self.package = package
        else:
            raise ValueError(f"'{package}' is not a valid package name")
        
        if not name:
            name = package.split('.').pop()
        self.name = name

        self.template_path = template_path

    def copy_templates(self, target_folder: str) -> list:
        """Copy the theme's templates to a subfolder in the site generator's
        template folder.

        Args:
            target_folder (str): the site generator's template folder

        Returns:
            list: the names of the copied templates
        """
        copied_templates = []
        templates_path = files(self.package) / self.template_path
        for file in files(self.package).iterdir():
            if file == templates_path:
                LOG.debug(f" copying templates from {templates_path}")
                theme_template_folder = os.path.join(target_folder, self.package)
                if not os.path.exists(theme_template_folder):
                    os.makedirs(theme_template_folder)
                for template in file.iterdir():
                    if template.is_file():
                        template_name = os.path.basename(str(template))
                        copied_templates.append(template_name)
                        target_path = os.path.join(theme_template_folder, template_name)
                        destination = Path(target_path)
                        destination.write_text(template.read_text())
                        LOG.debug(f" copied template {template_name} to {theme_template_folder}")
        if not copied_templates:
            LOG.debug(f" No templates found in {self.template_path}")
        return copied_templates
