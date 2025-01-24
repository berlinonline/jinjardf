<a id="jinjardf.site_generator"></a>

# jinjardf.site\_generator

`jinjardf.site_generator` generates a static HTML site based on an RDF graph. It does so by
iterating through the graph's resources and applying the appropriate Jinja template to it.
One page will be generated for each resource selected from the graph.

## Configuration

The site generator is configured using a YAML file like this:

{% raw %}
```python
generator = SiteGenerator('/path/to/config.yml')
```
{% endraw %}

The YAML file looks like this:

{% raw %}
```yaml
base_url: 'https://berlin.github.io' # the base hostname & protocol for your site, e.g. http://example.com
base_path: '/lod-budget' # the subpath of your site
dataset_path: 'data/temp/all.part.nt' # the path to the RDF file containing the graph (can be any format that
# rdflib can parse).
template_path: 'templates' # the path to the folder containing the Jinja templates
output_path: '_site/' # the output path where all generated HTML files will be placed
prefixes: # a list of prefixes that should be available throughout the site-generation process
  rdf: http://www.w3.org/1999/02/22-rdf-syntax-ns#
  rdfs: http://www.w3.org/2000/01/rdf-schema#
  schema: https://schema.org/
  void: http://rdfs.org/ns/void#
  xsd: http://www.w3.org/2001/XMLSchema#
include: # a list of files and folders that should be copied into the output_path
  - assets/
class_template_mappings: # mappings from classes to templates
  "void:Dataset": "dataset.html.jinja"
```
{% endraw %}

If you want to run the generator locally for test purposes, you can also pass a second parameter with
URL of the local test site (usually something like `[http://localhost:8000`).](http://localhost:8000`).)

## Template Variables

In the templates that have been loaded by the site generator, a number of variables are
available:

- `node`: The node from the input graph that is currently being processed. In other words, resource
for which the current page is being built. `node` is usually an instance of `rdflib.URIRef`, but can
for most purposes be use like a `str` (the URI of the node).
- `base_url`: The base URL of the site, e.g. `[https://berlin.github.io`](https://berlin.github.io`)
- `base_path`: The base path of the site, e.g. `/lod-budget`
- `resource_prefix`: BASE_URL + BASE_PATH – the URIs of all resources included in the site are in this namespace
- `prefixes`: A dictionary of prefixes that have been configured for the site generator.
- All prefixes in `prefixes` are also available directly in upper case in the template and are instances
of `rdflib.Namespace`. E.g., if `void: [http://rdfs.org/ns/void#`](http://rdfs.org/ns/void#`) is defined in the configuration, then
in the template we can do `{{ VOID.Dataset }}` to get `[http://rdfs.org/ns/void#Dataset`.](http://rdfs.org/ns/void#Dataset`.)

<a id="jinjardf.site_generator.DEFAULT_RESTRICTION"></a>

### DEFAULT\_RESTRICTION

The default SPARQL query for selection of resources from the input graph, if
`restriction_query` is not defined in the YAML config.
It selects all subject URIs which start with the site's resource prefix
(BASE_URL + BASE_PATH).

<a id="jinjardf.site_generator.DEFAULT_PREFIXES"></a>

### DEFAULT\_PREFIXES

A couple of default prefixes that are made available if `prefixes` is not set
in the YAML config.

<a id="jinjardf.site_generator.DEFAULT_DATASET_PATH"></a>

### DEFAULT\_DATASET\_PATH

The default path to the file containing the input RDF graph.

<a id="jinjardf.site_generator.DEFAULT_TEMPLATE_PATH"></a>

### DEFAULT\_TEMPLATE\_PATH

The default path to the template folder.

<a id="jinjardf.site_generator.DEFAULT_TEMPLATE"></a>

### DEFAULT\_TEMPLATE

The name of the default template that gets applied whenever no matching template could be
found in `class_template_mappings`.

<a id="jinjardf.site_generator.DEFAULT_OUTPUT_PATH"></a>

### DEFAULT\_OUTPUT\_PATH

The default path to the folder where all generated HTML files will be copied.

<a id="jinjardf.site_generator.SiteGenerator"></a>

## SiteGenerator Objects

{% raw %}
```python
class SiteGenerator(object)
```
{% endraw %}

<a id="jinjardf.site_generator.SiteGenerator.read_config"></a>

### read\_config

{% raw %}
```python
def read_config(config_key: str, default)
```
{% endraw %}

Read a value from the config and return it. If config_key is not included,
return the default instead. Write an appropriate log message for each case.

**Arguments**:

- `config_key` _str_ - the key for this setting in the config dictionary
- `default` __type__ - the default value for this setting
  

**Returns**:

- `_type_` - Either the value read from the config or the default.

<a id="jinjardf.site_generator.SiteGenerator.extract_resources"></a>

### extract\_resources

{% raw %}
```python
def extract_resources()
```
{% endraw %}

Run the restriction_query on the loaded RDF data to determine the set
of resources to include in the static site.

<a id="jinjardf.site_generator.SiteGenerator.compute_resource_class_index"></a>

### compute\_resource\_class\_index

{% raw %}
```python
def compute_resource_class_index(resources: list) -> Dict[URIRef, list]
```
{% endraw %}

Compute an index dict from resources to classes (rdf:type). The index is computed

based on the current RDF graph, and only resources are included in the index that are
contained in the list of resources passed to the function.

**Arguments**:

- `resources` (`list`): The list of resources to be considered.

**Returns**:

`dict`: A dict from resource URIs to class URIs, or None if no class is defined.

<a id="jinjardf.site_generator.SiteGenerator.compute_class_superclass_index"></a>

### compute\_class\_superclass\_index

{% raw %}
```python
def compute_class_superclass_index(
        resource_class_index: dict) -> Dict[URIRef, list]
```
{% endraw %}

Compute an index dict from class URIs to lists of class URIs which are their
superclasses, based on the current RDF graph. We consider all classes that are included
in the `resource_class_index`.
The list of superclasses is ordered from least to most specific. Also, every list of
superclasses that doesn't already begin with owl:Thing will have owl:Thing added as the
least specific superclass. This means that all resource keys in the index have at least
[ owl:Thing ] as their list of superclasses.

**Arguments**:

- `resource_class_index` _dict_ - An index dict from resource URIs to lists of class URIs.
  

**Returns**:

  Dict[URIRef, list]: An index dict from class URIs to lists of class URIs (the superclasses).

<a id="jinjardf.site_generator.SiteGenerator.compute_resource_template_index"></a>

### compute\_resource\_template\_index

{% raw %}
```python
def compute_resource_template_index(
        resources: list, resource_class_index: dict,
        class_superclass_index: dict) -> Dict[URIRef, str]
```
{% endraw %}

Compute an index dict from resource URIs to template names.

**Arguments**:

- `resources` _list_ - The list of resources to be considered
- `resource_class_index` _dict_ - The index of resources to classes
- `class_superclass_index` _dict_ - The index of classes to superclasses
  

**Returns**:

  Dict[URIRef, str]: The index from resource URIs to template names.

<a id="jinjardf.site_generator.CustomHandler"></a>

## CustomHandler Objects

{% raw %}
```python
class CustomHandler(SimpleHTTPRequestHandler)
```
{% endraw %}

A custom request handler that can serve *.html files without their file extension.
I.e., I can request `xxxxx` and get `xxxxx.html`.

