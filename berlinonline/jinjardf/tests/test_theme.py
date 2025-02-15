import os
from pathlib import PosixPath

import pytest

import berlinonline
import berlinonline.jinjardf
from berlinonline.jinjardf.tests import (
    temporary_template_folder,
    temporary_asset_folder,
    temporary_config_folder,
)
from berlinonline.jinjardf.theme import Theme

class TestTheme(object):

    @pytest.mark.parametrize("data", [
        {
            "kwargs": {
                'package': 'foo.bar.baztheme',
            },  
            'expected': {
                'package': 'foo.bar.baztheme',
                'name': 'baztheme',
                'template_path': 'templates'
            }
        },
        {
            "kwargs": {
                'package': 'foo.bar.baztheme',
                'name': "Foo!"
            },  
            'expected': {
                'package': 'foo.bar.baztheme',
                'name': 'Foo!',
                'template_path': 'templates'
            }
        },
        {
            "kwargs": {
                'package': 'foo.bar.baztheme',
                'name': "Foo!",
                'template_path': 'tmplts'
            },  
            'expected': {
                'package': 'foo.bar.baztheme',
                'name': 'Foo!',
                'template_path': 'tmplts'
            }
        },
    ])
    def test_successful_instantiation(self, data):
        """Test if all attributes have been set correctly upon instantiation.
        """
        kwargs = data['kwargs']
        theme = Theme(**kwargs)
        assert theme.name == data['expected']['name']
        assert theme.package == data['expected']['package']
        assert theme.template_path == data['expected']['template_path']

    def test_unsuccessful_instantiation(self):
        """Test that in invalid package name raises a ValueError."""
        with pytest.raises(ValueError):
            theme = Theme(package='foo-bar/baz')

    def test_copy_templates(self, temporary_template_folder):
        """Test if the theme's templates have been copied to the correct
        target folder.
        """
        theme = Theme('berlinonline.jinjardf.tests.theme_a')
        copied_templates = theme.copy_templates(temporary_template_folder)
        assert len(copied_templates) == 2
        templates = [ 'base', 'default' ]
        for template in templates:
            template_file = os.path.join(temporary_template_folder, theme.package, f"{template}.html.jinja")
            assert os.path.exists(template_file)

    def test_no_templates_copied(self, temporary_template_folder):
        """Test that no templates were copied.
        """

        theme = Theme('berlinonline.jinjardf.tests.theme_b')
        copied_templates = theme.copy_templates(temporary_template_folder)
        assert len(copied_templates) == 0

    def test_copy_assets(self, temporary_asset_folder):
        """Test if the theme's assets have been copied to the correct
        target folder.
        """
        theme = Theme('berlinonline.jinjardf.tests.theme_a')
        copied_assets = theme.copy_assets(temporary_asset_folder)
        assert len(copied_assets) == 2
        assets = [ 'script.js', 'style.css' ]
        for asset in assets:
            asset_file = os.path.join(temporary_asset_folder, theme.package, asset)
            assert os.path.exists(asset_file)

    def test_copy_config(self, temporary_config_folder):
        """Test if the theme's assets have been copied to the correct
        target folder.
        """
        theme = Theme('berlinonline.jinjardf.tests.theme_a')
        copied_config = theme.copy_config(temporary_config_folder)
        assert len(copied_config) == 1
        config_files = [ 'config.yml' ]
        for config in config_files:
            config_file = os.path.join(temporary_config_folder, theme.package, config)
            assert os.path.exists(config_file)

    def test_only_certain_folders_allowed(self, temporary_asset_folder):
        """Test that the only allowed types for copy_files are 'assets', 
        'templates' and 'config'."""
        theme = Theme('berlinonline.jinjardf.tests.theme_a')
        with pytest.raises(ValueError):
            theme._copy_files('fonzos', temporary_asset_folder)

    def test_resolve_package_returns_multiplexpath(self):

        theme = Theme('berlinonline.jinjardf.tests.theme_a')
        path = theme.resolve_package()
        assert type(path) is PosixPath
        assert os.path.isdir(path)


    def test_resolve_package_handles_error(self, monkeypatch):
        """Test that when resolve_package() throws a NotADirectoryError (i.e. when
        the package was installed in editable mode), the error is handled correctly."""

        def mock_files(_):
            raise NotADirectoryError("Mocked error")

        monkeypatch.setattr(berlinonline.jinjardf.theme, "files", mock_files)
        theme = Theme('berlinonline.jinjardf.tests.theme_a')

        path = theme.resolve_package()
        assert type(path) is PosixPath
        assert os.path.isdir(path)
