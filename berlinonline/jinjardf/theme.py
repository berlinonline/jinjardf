import logging
import os
from importlib.resources import files
from pathlib import Path

from berlinonline.jinjardf.helper import is_valid_package_path

LOG = logging.getLogger(__name__)
ALLOWED_FILE_TYPES = [ 'templates', 'assets' ]

class Theme(object):
    """A theme contains templates for use with the JinjaRDF site builder.

    Attributes:
        package (str): the full dotted path of the theme's package, e.g. 'foo.bar.basetheme'
        name (str): A human-readable name of the theme. Default is the theme's subpackage,
        e.g. 'basetheme'.
        template_path (str): The template path relative to the theme's package.
        Defaults to 'templates'.
        asset_path (str): The asset path relative to the theme's package.
        Defaults to 'assets'.
        file_paths (dict): A dict to get `self.template_path` and `self.asset_path`
        by name (either `self.file_paths['templates']` or `self.file_paths['assets']`).
    """
    package: str
    name: str
    template_path: str
    asset_path: str
    file_paths: dict

    def __init__(self, package: str, name: str=None, template_path: str='templates', asset_path: str='assets'):
        """Initialize the theme

        Args:
            package (str): the full dotted path of the theme's package, e.g. 'foo.bar.basetheme'
            name (str): Optional human-readable theme name. If None, then `theme.name`
            will be the name of the theme's subpackage (e.g. 'basetheme').
            Defaults to None.
            template_path (str, optional): The template path relative to the theme's package.
            Defaults to 'templates'.
            asset_path (str, optional): The asset path relative to the theme's package.
            Defaults to 'assets'.
        """

        if is_valid_package_path(package):
            self.package = package
        else:
            raise ValueError(f"'{package}' is not a valid package name")
        
        if not name:
            name = package.split('.').pop()
        self.name = name

        self.template_path = template_path
        self.asset_path = asset_path
        self.file_paths = {
            'templates': self.template_path ,
            'assets': self.asset_path ,
        }

    def _copy_files(self, type: str, target_folder: str) -> list:
        """Generic method to copy either the templates or the assets
        of a theme from their installed location in the python site packages
        to the correct folder of the JinjaRDF site generator project.

        Args:
            type (str): either `templates` or `assets`
            target_folder (str): the site generator's template or asset folder

        Returns:
            list: the names of the copied files
        """
        if type not in ALLOWED_FILE_TYPES:
            raise ValueError(f"'type' must be one of ({' | '.join(ALLOWED_FILE_TYPES)}).")
        copied_files = []
        files_path = files(self.package) / self.file_paths[type]
        for file in files(self.package).iterdir():
            if file == files_path:
                LOG.debug(f" copying {type} from {files_path}")
                theme_files_folder = os.path.join(target_folder, self.package)
                if not os.path.exists(theme_files_folder):
                    os.makedirs(theme_files_folder)
                for _file in file.iterdir():
                    if _file.is_file():
                        file_name = os.path.basename(str(_file))
                        copied_files.append(file_name)
                        target_path = os.path.join(theme_files_folder, file_name)
                        destination = Path(target_path)
                        destination.write_text(_file.read_text())
                        LOG.debug(f" copied {file_name} to {theme_files_folder}")
        if not copied_files:
            LOG.debug(f" No {type} found in {self.file_paths[type]}")
        return copied_files


    def copy_templates(self, target_folder: str) -> list:
        """Copy the theme's templates to a subfolder in the site generator's
        template folder.

        Args:
            target_folder (str): the site generator's template folder

        Returns:
            list: the names of the copied templates
        """
        return self._copy_files('templates', target_folder)

    def copy_assets(self, target_folder: str) -> list:
        """Copy the theme's assets to a subfolder in the site generator's
        asset folder.

        Args:
            target_folder (str): the site generator's asset folder

        Returns:
            list: the names of the copied assets
        """
        return self._copy_files('assets', target_folder)