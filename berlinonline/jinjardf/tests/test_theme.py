import os

import pytest

from berlinonline.jinjardf.theme import Theme
from berlinonline.jinjardf.tests import temporary_template_folder

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
