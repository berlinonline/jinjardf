<a id="jinjardf.rdf_filters"></a>

# jinjardf.rdf\_filters

This module defines a number of custom filters for Jinja2. Each filter is defined as a function.
When used as a filter in a Jinja template, some of the function's parameters are already set.

## Filter Parameters

If the `@pass_environment` decorator is used, the Jinja environment that called the template is
being passed to the filter function as the first parameter (usually called `environment`):

{% raw %}
```python
@pass_environment
def rdf_property(environment: RDFEnvironment, subject: IdentifiedNode, predicate: str, language: str=None, unique: bool=False) -> List[Identifier]:
...
```
{% endraw %}

The parameter after `environment` (or the first parameter, if the environment is not passed)
is the value that the filter is being applied to in the template. The remaining parameters of the filter
function are passed by the filter explicitly as parameters.

Lets consider the filter function `rdf_get(iri: str)`. This filter could be used in a template as follows:

{% raw %}
```jinja
{{ 'https://example.com/foo/bar' | rdf_get }}
```
{% endraw %}

In this case, '[https://example.com/foo/bar'](https://example.com/foo/bar') would be passed to `rdf_get()` as the `iri` parameter.

The `rdf_property()` function (see above) would be used as a filter like this:

{% raw %}
```jinja
{{ node | rdf_property(RDFS.label, 'en', true) }}
```
{% endraw %}

In this case, the function's `environment` parameter was passed by the `pass_environment` decorator, 
`node` from the template is passed as the `subject` parameter, and `RDFS.label`, `'en'` and `true` are
passed as the function's remaining three parameters `predicate`, `language` and `unique`.

## Examples

The documentation for the filter functions below includes examples of how to use them as filters
in a Jinja template.
For these examples, we assume that graph loaded by the `RDFEnvironment` contains the RDF from this
dataset: [https://berlinonline.github.io/jinja-rdf-demo/example/ducks/](https://berlinonline.github.io/jinja-rdf-demo/example/ducks/)

<a id="jinjardf.rdf_filters.DEFAULT_TITLE_PROPERTIES"></a>

### DEFAULT\_TITLE\_PROPERTIES

A list of properties that all mean something like 'title' and are used by
the `title()` and `title_any()` filters. The properties are:

* `rdfs:label`
* `dct:title`
* `foaf:name`
* `schema:name`
* `skos:prefLabel`

<a id="jinjardf.rdf_filters.DEFAULT_DESCRIPTION_PROPERTIES"></a>

### DEFAULT\_DESCRIPTION\_PROPERTIES

A list of properties that all mean something like 'description' and are used by
the `description()` and `description_any()` filters. The properties are:

* `rdfs:comment`
* `dct:description`
* `schema:description`

<a id="jinjardf.rdf_filters.RDFFilters"></a>

## RDFFilters Objects

{% raw %}
```python
class RDFFilters(Extension)
```
{% endraw %}

Implementation of a Jinja2 extension that provides various filters for
working with RDF data. The filters are based on the rdflib library.

See [https://rdflib.readthedocs.io/en/stable/](https://rdflib.readthedocs.io/en/stable/)

<a id="jinjardf.rdf_filters.RDFFilters.rdf_get"></a>

### rdf\_get

{% raw %}
```python
@staticmethod
def rdf_get(iri: str) -> URIRef
```
{% endraw %}

Return an rdflib `URIRef` with the IRI that was passed as the value.
When used as a Jinja filter, the value passed is the `iri`.
This is useful when we want to use use rdflib's API for URIRefs, or if we
want to compare the IRI with another URIRef.

**Usage in a template**:

The (somewhat contrieved) example is using `rdf_get` to turn a string into
a URIRef object, so what we can use the `n3()` function on it.
([https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#rdflib.term.URIRef.n3)](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#rdflib.term.URIRef.n3))


{% raw %}
```jinja
{% set iri_string = 'https://example.com/foo/bar' %}
{% set iri = iri_string | rdf_get %}
{{ iri.n3() }}
---
Output:
<https://example.com/foo/bar>
```
{% endraw %}

**Arguments**:

- `iri` _str_ - The IRI of the resource.
  

**Returns**:

- `URIRef` - The returned resource.

<a id="jinjardf.rdf_filters.RDFFilters.toPython"></a>

### toPython

{% raw %}
```python
@staticmethod
def toPython(node: Node)
```
{% endraw %}

Returns an appropriate python datatype for the rdflib type of `node`, or `None` if
`node` is `None`. This is useful if we want to compare the value of a literal
with a Jinja (Python) object, such as a String.

**Usage in a template**:

- node: [https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck](https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck)


{% raw %}
```jinja
{% set gender = node | rdf_property_any(SCHEMA.gender) | toPython %}
{% if gender == 'female' %}
    weiblich
{% elif gender == 'male' %}
    männlich
{% else %}
    sonstiges
{% endif %}
---
Output:
weiblich
```
{% endraw %}

**Arguments**:

- `node` _Node_ - the node to convert
  

**Returns**:

- `_type_` - an appropriate python representation of `node` (str, int, boolean etc.)

<a id="jinjardf.rdf_filters.RDFFilters.is_iri"></a>

### is\_iri

{% raw %}
```python
@staticmethod
def is_iri(node: Node) -> bool
```
{% endraw %}

Return `True` if `node` is an IRI (URI) resource, `False` if not.

**Usage in a template**:

- node: [https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck](https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck)


{% raw %}
```jinja
{% if node | is_iri %}
    {{ node }} is an IRI.
{% endif %}
------
Output:
https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck is an IRI.
```
{% endraw %}

**Arguments**:

- `node` _Node_ - the node to test
  

**Returns**:

- `bool` - `True` is `node` is an IRI, `False` if not.

<a id="jinjardf.rdf_filters.RDFFilters.is_bnode"></a>

### is\_bnode

{% raw %}
```python
@staticmethod
def is_bnode(node: Node) -> bool
```
{% endraw %}

Return `True` if `node` is a blank node resource, `False` if not.

**Usage in a template**:

- node: [https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck](https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck)


{% raw %}
```jinja
{% if node | is_bnode %}
    {{ node }} is a Bnode.
{% else %}
    {{ node }} is not a Bnode.
{% endif %}
------
Output:
https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck is not a Bnode.
```
{% endraw %}

**Arguments**:

- `node` _Node_ - the node to test
  

**Returns**:

- `bool` - `True` is `node` is a bnode, `False` if not.

<a id="jinjardf.rdf_filters.RDFFilters.is_resource"></a>

### is\_resource

{% raw %}
```python
@staticmethod
def is_resource(node: Node) -> bool
```
{% endraw %}

Return `True` if `node` is a resource (either IRI or bnode), `False` if not.

**Usage in a template**:

- node: [https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck](https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck)


{% raw %}
```jinja
{% if node | is_resource %}
    {{ node }} is a resource.
{% endif %}
------
Output: https://example.com/foo/bar is a resource.
```
{% endraw %}

**Arguments**:

- `node` _Node_ - the node to test
  

**Returns**:

- `bool` - `True` is `node` is a resource, `False` if not.

<a id="jinjardf.rdf_filters.RDFFilters.is_literal"></a>

### is\_literal

{% raw %}
```python
@staticmethod
def is_literal(node: Node) -> bool
```
{% endraw %}

Return `True` if `node` is a literal, `False` if not.

**Usage in a template**:

- node: [https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck](https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck)


{% raw %}
```jinja
{% set title = node | title_any(language=['en']) %}
{{ node }} is a literal: {% node | is_literal %}<br/>
'{{ title }}' is a literal: {% title | is_literal %}<br/>
------
Output:
https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck is a literal: False
'Della Duck' is a literal: True
```
{% endraw %}

**Arguments**:

- `node` _Node_ - the node to test
  

**Returns**:

- `bool` - `True` is `node` is a literal, `False` if not.

<a id="jinjardf.rdf_filters.RDFFilters.rdf_property"></a>

### rdf\_property

{% raw %}
```python
@staticmethod
@pass_environment
def rdf_property(environment: RDFEnvironment,
                 subject: IdentifiedNode,
                 predicate: str,
                 language: str = None,
                 unique: bool = False) -> List[Identifier]
```
{% endraw %}

Return the objects for the pattern (`subject`, `predicate`, `OBJ`).
If an optional language code is provided, the results will be filtered to only
contain literals with that language.
When used as a Jinja filter, the value passed is the `subject`.

**Usage in a template**:

- node: [https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck](https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck)


{% raw %}
```jinja
schema:names: {{ node | rdf_property(SCHEMA.name) }}<br/>
Japanese schema:names: {{ node | rdf_property(SCHEMA.name, 'ja') }}<br/>
rdfs:labels: {{ node | rdf_property(RDFS.label) }}<br/>
------
Output:
schema:names: [ 'Della And', 'Della Duck', 'Ντέλλα Ντακ', 'Della Duck', 'Bella Pato', 'デラ・ダック', … ]
Japanese schema:names: [ 'デラ・ダック' ]
rdfs:labels: []
```
{% endraw %}

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `subject` _IdentifiedNode_ - the subject resource
- `predicate` _str_ - URI of the property
- `language` _str, optional_ - language code like `en` or `fr`. Defaults to `None`.
- `unique` _bool, optional_ - Set to `True` if only unique results should be returned. Defaults to `False`.
  

**Returns**:

- `List[rdflib.term.Identifier]` - a list of nodes (`URIRef`, `Literal` or `BNode`)

<a id="jinjardf.rdf_filters.RDFFilters.rdf_property_any"></a>

### rdf\_property\_any

{% raw %}
```python
@staticmethod
@pass_environment
def rdf_property_any(environment: RDFEnvironment,
                     subject: IdentifiedNode,
                     predicate: str,
                     language: str = None) -> Identifier
```
{% endraw %}

Return one arbitrary object for the pattern (`subject`, `predicate`, `OBJ`).
If an optional language code is provided, only a literal with that language will
be returned.
When used as a Jinja filter, the value passed is the `subject`.

**Usage in a template**:

- node: [https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck](https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck)


{% raw %}
```jinja
any schema:name: {{ node | rdf_property_any(SCHEMA.name) }}<br/>
any Japanese schema:name: {{ node | rdf_property_any(SCHEMA.name, 'ja') }}<br/>
any rdfs:label: {{ node | rdf_property_any(RDFS.label) }}<br/>
------
Output:
any schema:name: 'Della And'
any Japanese schema:name: 'デラ・ダック'
any rdfs:label: None
```
{% endraw %}

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `subject` _IdentifiedNode_ - the subject resource
- `predicate` _str_ - URI of the property
- `language` _str, optional_ - language code like `en` or `fr`. Defaults to `None`.
  

**Returns**:

- `Identifier` - a `URIRef`, `Literal` or `BNode`

<a id="jinjardf.rdf_filters.RDFFilters.rdf_inverse_property"></a>

### rdf\_inverse\_property

{% raw %}
```python
@staticmethod
@pass_environment
def rdf_inverse_property(environment: RDFEnvironment,
                         object: IdentifiedNode,
                         predicate: str,
                         unique: bool = False) -> List[IdentifiedNode]
```
{% endraw %}

Return the subjects for the pattern (`SUBJ`, `predicate`, `object`).
When used as a Jinja filter, the value passed is the `object`.

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `object` _IdentifiedNode_ - The object resource.
- `predicate` _str_ - URI of the predicate
- `unique` _bool, optional_ - Set to `True` if only unique results should be returned. Defaults to `False`.
  

**Returns**:

- `List[rdflib.IdentifiedNode]` - a list of subject nodes (`URIRef` or `BNode`)

<a id="jinjardf.rdf_filters.RDFFilters.rdf_inverse_property_any"></a>

### rdf\_inverse\_property\_any

{% raw %}
```python
@staticmethod
@pass_environment
def rdf_inverse_property_any(environment: RDFEnvironment,
                             object: IdentifiedNode,
                             predicate: str) -> IdentifiedNode
```
{% endraw %}

Return one arbitrary subject for the pattern (`SUBJ`, `predicate`, `object`).
When used as a Jinja filter, the value passed is the `object`.

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `object` _IdentifiedNode_ - the object resource
- `predicate` _str_ - URI of the predicate
  

**Returns**:

- `IdentifiedNode` - one instance of `IdentifiedNode`, either a `URIRef` or a `BNode`.

<a id="jinjardf.rdf_filters.RDFFilters.sparql_query"></a>

### sparql\_query

{% raw %}
```python
@staticmethod
@pass_environment
def sparql_query(environment: RDFEnvironment, resourceURI: URIRef,
                 query: str) -> Result
```
{% endraw %}

Run a custom SPARQL query, where each occurrence of `?resourceUri`
is replaced with the `resourceURI` parameter. Returns an iterator over the
resultset, where each result contains the bindings for the selected variables
(in the case of a SELECT query).
See [https://rdflib.readthedocs.io/en/latest/apidocs/rdflib.html#rdflib.query.Result.](https://rdflib.readthedocs.io/en/latest/apidocs/rdflib.html#rdflib.query.Result.)

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `resourceURI` _URIRef_ - URIRef to drop into the query.
- `query` _str_ - the actual query.
  

**Returns**:

- `Result` - the iterable query result

<a id="jinjardf.rdf_filters.RDFFilters.statements_as_subject"></a>

### statements\_as\_subject

{% raw %}
```python
@staticmethod
@pass_environment
def statements_as_subject(environment: RDFEnvironment,
                          resource: IdentifiedNode,
                          as_list: bool = False) -> Generator
```
{% endraw %}

Return all statements/triples in the graph where the current resource as
passed to the filter is the subject.

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `resource` _IdentifiedNode_ - The resource as passed to the filter as the value.
  

**Yields**:

- `Generator` - The matching statements

<a id="jinjardf.rdf_filters.RDFFilters.statements_as_object"></a>

### statements\_as\_object

{% raw %}
```python
@staticmethod
@pass_environment
def statements_as_object(environment: RDFEnvironment,
                         resource: IdentifiedNode,
                         as_list: bool = False) -> Generator
```
{% endraw %}

Return all statements/triples in the graph where the current resource as
passed to the filter is the object.

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `resource` _IdentifiedNode_ - The resource as passed to the filter as the value.
  

**Yields**:

- `Generator` - The matching statements

<a id="jinjardf.rdf_filters.RDFFilters.get_text"></a>

### get\_text

{% raw %}
```python
@staticmethod
@pass_environment
def get_text(environment: RDFEnvironment,
             resource: IdentifiedNode,
             properties: list,
             languages: list = [],
             return_first: bool = False,
             default: str = None) -> List[Literal]
```
{% endraw %}

Find all literals connected to `resource` via any of the `properties`, for all `languages`
and return them as a list. This is e.g. used to get all titles, or all descriptions of a resource,
by passing a list of desired title-properties (`rdfs:label`, `dct:title`, `schema:name` etc.) or
description-properties (`rdfs:comment`, `dct:description`, `schema:description` etc.).

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `resource` _IdentifiedNode_ - the resource for which to find literals
- `properties` _list_ - the list of properties to use
- `languages` _list, optional_ - list of language codes. Defaults to `[]`.
- `return_first` _bool, optional_ - If `True`, only return the first literal found. Defaults to `False`.
- `default` _str, optional_ - If no matching literals are found, return this. Defaults to `None`.
  

**Returns**:

- `List[Literal]` - the list of literals found

<a id="jinjardf.rdf_filters.RDFFilters.title"></a>

### title

{% raw %}
```python
@staticmethod
@pass_environment
def title(environment: RDFEnvironment,
          resource: IdentifiedNode,
          languages: list = [],
          return_first: bool = False,
          default: str = None) -> List[Literal]
```
{% endraw %}

Find all titles (as defined by in the `environment`) for all languages specified and return them
as a list.

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `resource` _IdentifiedNode_ - the resource for which to find title
- `languages` _list_ - list of language codes
- `return_first` _bool, optional_ - If True, only return the first title found. Defaults to False.
- `default` _str_ - If no matching titles are found, return this.
  

**Returns**:

- `list` - the list of titles found

<a id="jinjardf.rdf_filters.RDFFilters.description"></a>

### description

{% raw %}
```python
@staticmethod
@pass_environment
def description(environment: RDFEnvironment,
                resource: IdentifiedNode,
                languages: list = [],
                return_first: bool = False,
                default: str = None) -> List[Literal]
```
{% endraw %}

Find all descriptions (as defined by in the `environment`) for all languages specified and return them
as a list.

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `resource` _IdentifiedNode_ - the resource for which to find title
- `languages` _list_ - list of language codes
- `return_first` _bool, optional_ - If True, only return the first title found. Defaults to False.
- `default` _str_ - If no matching titles are found, return this.
  

**Returns**:

- `list` - the list of titles found

<a id="jinjardf.rdf_filters.RDFFilters.relative_uri"></a>

### relative\_uri

{% raw %}
```python
@staticmethod
@pass_environment
def relative_uri(environment: RDFEnvironment, resource: IdentifiedNode) -> str
```
{% endraw %}

Returns the URI of this resource relative to the site URL.

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `resource` _IdentifiedNode_ - the resource for which we want to get the relative URI
  

**Returns**:

- `str` - the relative URI

