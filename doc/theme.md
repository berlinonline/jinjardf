# Table of Contents

  * [Theme](#jinjardf.theme.Theme)
    * [\_\_init\_\_](#jinjardf.theme.Theme.__init__)
    * [resolve\_package](#jinjardf.theme.Theme.resolve_package)
    * [copy\_templates](#jinjardf.theme.Theme.copy_templates)
    * [copy\_assets](#jinjardf.theme.Theme.copy_assets)
    * [copy\_config](#jinjardf.theme.Theme.copy_config)

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
- `asset_path` _str_ - The asset path relative to the theme's package.
  Defaults to 'assets'.
- `config_path` _str_ - The config path relative to the theme's package.
  Defaults to 'config'.
- `file_paths` _dict_ - A dict to get `self.template_path` and `self.asset_path`
  by name (either `self.file_paths['templates']` or `self.file_paths['assets']`).

<a id="jinjardf.theme.Theme.__init__"></a>

### \_\_init\_\_

{% raw %}
```python
def __init__(package: str,
             name: str = None,
             template_path: str = 'templates',
             asset_path: str = 'assets',
             config_path: str = 'config')
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
- `asset_path` _str, optional_ - The asset path relative to the theme's package.
  Defaults to 'assets'.

<a id="jinjardf.theme.Theme.resolve_package"></a>

### resolve\_package

{% raw %}
```python
def resolve_package() -> Traversable
```
{% endraw %}

Take `self.package` and resolve to its location as a `Traversable`,
regardless of having been installed in editable mode or not.

**Returns**:

- `Traversable` - The location of the package, e.g. as a `Path` or
  a `MultiplexedPath`.

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

<a id="jinjardf.theme.Theme.copy_assets"></a>

### copy\_assets

{% raw %}
```python
def copy_assets(target_folder: str) -> list
```
{% endraw %}

Copy the theme's assets to a subfolder in the site generator's
asset folder.

**Arguments**:

- `target_folder` _str_ - the site generator's asset folder
  

**Returns**:

- `list` - the names of the copied assets

<a id="jinjardf.theme.Theme.copy_config"></a>

### copy\_config

{% raw %}
```python
def copy_config(target_folder: str) -> list
```
{% endraw %}

Copy the theme's config to a subfolder in the site generator's
config folder.

**Arguments**:

- `target_folder` _str_ - the site generator's config folder
  

**Returns**:

- `list` - the list of the copied config files

