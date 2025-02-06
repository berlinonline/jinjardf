import os

import pytest

from berlinonline.jinjardf.theme import Theme
from berlinonline.jinjardf.tests import temporary_template_folder

class ATheme(Theme):
    pass

class BTheme(Theme):
    pass


class TestTheme(object):

    @pytest.mark.parametrize("data", [
        {
            'name': 'foo',
            'class': ATheme,
            'expected': {
                'name': 'foo',
                'path': 'berlinonline.jinjardf.tests.test_theme.ATheme',
                'dir_path': os.path.dirname(__file__)
            }
        },
        {
            'name': None,
            'class': ATheme,
            'expected': {
                'name': ATheme.__qualname__,
                'path': 'berlinonline.jinjardf.tests.test_theme.ATheme',
                'dir_path': os.path.dirname(__file__)
            }
        },
        {
            'name': None,
            'class': BTheme,
            'expected': {
                'name': BTheme.__qualname__,
                'path': 'berlinonline.jinjardf.tests.test_theme.BTheme',
                'dir_path': os.path.dirname(__file__)
            }
        },
    ])
    def test_instantiation(self, data):
        """Test if all attributes have been set correctly upon instantiation.
        """
        ThemeClass = data['class']
        theme = ThemeClass(name=data['name'])
        assert theme.name == data['expected']['name']
        assert theme.module_path == data['expected']['path']
        assert str(theme.dir_path) == data['expected']['dir_path']

    def test_copy_templates(self, temporary_template_folder):
        """Test if the theme's templates have been copied to the correct
        target folder.
        """
        theme = ATheme()
        theme.copy_templates(temporary_template_folder)
        templates = [ 'animal', 'base', 'dataset', 'default', 'dog', 'event' ]
        for template in templates:
            template_file = os.path.join(temporary_template_folder, theme.module_path, f"{template}.html.jinja")
            assert os.path.exists(template_file)
