# Table of Contents

  * [Theme](#jinjardf.theme.Theme)
    * [\_\_init\_\_](#jinjardf.theme.Theme.__init__)
    * [copy\_templates](#jinjardf.theme.Theme.copy_templates)

<a id="jinjardf.theme"></a>

# jinjardf.theme

<a id="jinjardf.theme.Theme"></a>

## Theme Objects

{% raw %}
```python
class Theme(ABC)
```
{% endraw %}

A theme contains templates for use with the JinjaRDF site builder.
`Theme` is an abstract base class and should be sub-classed for concrete
themes.

**Attributes**:

- `name` _str_ - A human-readable name of the theme. Default is the class name.
- `module_path` _str_ - The complete path to the theme in dot-notation.
- `dir_path` _importlib.resources.abc.Traversable_ - The location of this theme.
- `template_path` _str_ - The template path relative to the theme.
  Defaults to 'template'.

<a id="jinjardf.theme.Theme.__init__"></a>

### \_\_init\_\_

{% raw %}
```python
def __init__(name: str = None, template_path: str = 'templates')
```
{% endraw %}

Initialize the theme

**Arguments**:

- `name` _str, optional_ - Optional human-readable theme name. If none, then theme.name
  will be the name of the theme class. Defaults to None.
- `template_path` _str, optional_ - The template path relative to the theme class (this class).
  Defaults to 'templates'.

<a id="jinjardf.theme.Theme.copy_templates"></a>

### copy\_templates

{% raw %}
```python
def copy_templates(target_folder: str)
```
{% endraw %}

Copy the theme's templates to a subfolder in the site generator's
template folder.

**Arguments**:

- `target_folder` _str_ - the site generator's template folder

