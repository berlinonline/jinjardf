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
class Theme(object)
```
{% endraw %}

A theme contains templates for use with the JinjaRDF site builder.

**Attributes**:

- `package` _str_ - the full dotted path of the theme's package, e.g. 'foo.bar.basetheme'
- `name` _str_ - A human-readable name of the theme. Default is the theme's subpackage,
  e.g. 'basetheme'.
- `template_path` _str_ - The template path relative to the theme's package.
  Defaults to 'templates'.

<a id="jinjardf.theme.Theme.__init__"></a>

### \_\_init\_\_

{% raw %}
```python
def __init__(package: str, name: str = None, template_path: str = 'templates')
```
{% endraw %}

Initialize the theme

**Arguments**:

- `package` _str_ - the full dotted path of the theme's package, e.g. 'foo.bar.basetheme'
- `name` _str_ - Optional human-readable theme name. If None, then `theme.name`
  will be the name of the theme's subpackage (e.g. 'basetheme').
  Defaults to None.
- `template_path` _str, optional_ - The template path relative to the theme's package.
  Defaults to 'templates'.

<a id="jinjardf.theme.Theme.copy_templates"></a>

### copy\_templates

{% raw %}
```python
def copy_templates(target_folder: str) -> list
```
{% endraw %}

Copy the theme's templates to a subfolder in the site generator's
template folder.

**Arguments**:

- `target_folder` _str_ - the site generator's template folder
  

**Returns**:

- `list` - the names of the copied templates

