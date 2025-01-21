<a id="jinjardf.rdf_filters"></a>

# jinjardf.rdf\_filters

This module defines a number of custom filters for Jinja2. Each filter is defined as a function.
When used as a filter in a Jinja template, some of the function's parameters are already set.

## Filter Parameters

If the `@pass_environment` decorator is used, the Jinja environment that called the template is
being passed to the filter function as the first parameter (usually called `environment`):

```python
@pass_environment
def rdf_property(environment: RDFEnvironment, subject: IdentifiedNode, predicate: str, language: str=None, unique: bool=False) -> List[Identifier]:
...
```

The parameter after `environment` (or the first parameter, if the environment is not passed)
is the value that the filter is being applied to in the template. The remaining parameters of the filter
function are passed by the filter explicitly as parameters.

Lets consider the filter function `rdf_get(iri: str)`. This filter could be used in a template as follows:

{% raw %}
```jinja
{{ 'https://example.com/foo/bar' | rdf_get }}
```

In this case, 'https://example.com/foo/bar' would be passed to `rdf_get()` as the `iri` parameter.

The `rdf_property()` function (see above) would be used as a filter like this:

```jinja
{% endraw %}
{{ node | rdf_property(RDFS.label, 'en', true) }}
```

In this case, the function's `environment` parameter was passed by the `@pass_environment` decorator, 
`node` from the template is passed as the `subject` parameter, and `RDFS.label`, `'en'` and `true` are
passed as the function's remaining three parameters `predicate`, `language` and `unique`.

<a id="jinjardf.rdf_filters.DEFAULT_TITLE_PROPERTIES"></a>

#### DEFAULT\_TITLE\_PROPERTIES

A list of properties that all mean something like 'title' and are used by
the `title()` and `title_any()` filters. The properties are:

* `rdfs:label`
* `dct:title`
* `foaf:name`
* `schema:name`
* `skos:prefLabel`

<a id="jinjardf.rdf_filters.DEFAULT_DESCRIPTION_PROPERTIES"></a>

#### DEFAULT\_DESCRIPTION\_PROPERTIES

A list of properties that all mean something like 'description' and are used by
the `description()` and `description_any()` filters. The properties are:

* `rdfs:comment`
* `dct:description`
* `schema:description`

<a id="jinjardf.rdf_filters.RDFFilters"></a>

## RDFFilters Objects

```python
class RDFFilters(Extension)
```

Implementation of a Jinja2 extension that provides various filters for
working with RDF data. The filters are based on the rdflib library.

See https://rdflib.readthedocs.io/en/stable/

<a id="jinjardf.rdf_filters.RDFFilters.rdf_get"></a>

#### rdf\_get

```python
@staticmethod
def rdf_get(iri: str) -> URIRef
```

Return an rdflib URIRef with the IRI that was passed as the value.
When used as a Jinja filter, the value passed is the `iri`.

**Usage in a template**:


{% raw %}
```jinja
{% set iri = 'https://example.com/foo/bar' %}
{{ iri | rdf_get }}
```

**Arguments**:

- `iri` _str_ - The IRI of the resource.
  

**Returns**:

- `URIRef` - The returned resource.

<a id="jinjardf.rdf_filters.RDFFilters.toPython"></a>

#### toPython

```python
@staticmethod
def toPython(node: Node)
```

Returns an appropriate python datatype for the rdflib type of `node`, or `None``
if `node` is `None`.

**Arguments**:

- `node` _Node_ - the node to convert
  

**Returns**:

- `_type_` - an appropriate python representation of `node` (str, int, boolean etc.)

<a id="jinjardf.rdf_filters.RDFFilters.is_iri"></a>

#### is\_iri

```python
@staticmethod
def is_iri(node: Node) -> bool
```

Return `True` if `node` is an IRI (URI) resource, `False` if not.

**Usage in a template**:


```jinja
{% endraw %}
{% set node = 'https://example.com/foo/bar' | rdf_get %}
{% if node | is_iri %}
    {{ node }} is an IRI.
{% endif %}
------
https://example.com/foo/bar is an IRI.
```

**Arguments**:

- `node` _Node_ - the node to test
  

**Returns**:

- `bool` - `True` is `node` is an IRI, `False` if not.

<a id="jinjardf.rdf_filters.RDFFilters.is_bnode"></a>

#### is\_bnode

```python
@staticmethod
def is_bnode(node: Node) -> bool
```

Return `True` if `node` is a blank node resource, `False` if not.

**Usage in a template**:


{% raw %}
```jinja
{% set node = 'https://example.com/foo/bar' | rdf_get %}
{% if node | is_bnode %}
    {{ node }} is a Bnode.
{% else %}
    {{ node }} is not a Bnode.
{% endif %}
------
https://example.com/foo/bar is not a Bnode.
```

**Arguments**:

- `node` _Node_ - the node to test
  

**Returns**:

- `bool` - `True` is `node` is a bnode, `False` if not.

<a id="jinjardf.rdf_filters.RDFFilters.is_resource"></a>

#### is\_resource

```python
@staticmethod
def is_resource(node: Node) -> bool
```

Return `True` if `node` is a resource (either IRI or bnode), `False` if not.

**Usage in a template**:


```jinja
{% endraw %}
{% set node = 'https://example.com/foo/bar' | rdf_get %}
{% if node | is_resource %}
    {{ node }} is a resource.
{% endif %}
------
https://example.com/foo/bar is a resource.
```

**Arguments**:

- `node` _Node_ - the node to test
  

**Returns**:

- `bool` - `True` is `node` is a resource, `False` if not.

<a id="jinjardf.rdf_filters.RDFFilters.is_literal"></a>

#### is\_literal

```python
@staticmethod
def is_literal(node: Node) -> bool
```

Return `True` if `node` is a literal, `False` if not.

**Usage in a template**:


{% raw %}
```jinja
{% set title = node | title_any %}
{% if title | is_literal %}
    '{{ title }}' is a literal.
{% endif %}
------
'Hello World' is a literal.
```

**Arguments**:

- `node` _Node_ - the node to test
  

**Returns**:

- `bool` - `True` is `node` is a literal, `False` if not.

<a id="jinjardf.rdf_filters.RDFFilters.rdf_property"></a>

#### rdf\_property

```python
@staticmethod
@pass_environment
def rdf_property(environment: RDFEnvironment,
                 subject: IdentifiedNode,
                 predicate: str,
                 language: str = None,
                 unique: bool = False) -> List[Identifier]
```

Return the objects for the pattern (`subject`, `predicate`, `OBJ`).
If an optional language code is provided, the results will be filtered to only
contain literals with that language.
When used as a Jinja filter, the value passed is the `subject`.

**Usage in a template**:


```jinja
{% endraw %}
{{ node | rdf_property(RDFS.label, 'en', true) }}
```

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `subject` _IdentifiedNode_ - the subject resource
- `predicate` _str_ - URI of the property
- `language` _str, optional_ - language code like `en` or `fr`. Defaults to `None`.
- `unique` _bool, optional_ - Set to `True` if only unique results should be returned. Defaults to `False`.
  

**Returns**:

- `List[rdflib.term.Identifier]` - a list of nodes (`URIRef`, `Literal` or `BNode`)

<a id="jinjardf.rdf_filters.RDFFilters.rdf_property_any"></a>

#### rdf\_property\_any

```python
@staticmethod
@pass_environment
def rdf_property_any(environment: RDFEnvironment,
                     subject: IdentifiedNode,
                     predicate: str,
                     language: str = None) -> Identifier
```

Return one arbitrary object for the pattern (`subject`, `predicate`, `OBJ`).
If an optional language code is provided, only a literal with that language will
be returned.
When used as a Jinja filter, the value passed is the `subject`.

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `subject` _IdentifiedNode_ - the subject resource
- `predicate` _str_ - URI of the property
- `language` _str, optional_ - language code like `en` or `fr`. Defaults to `None`.
  

**Returns**:

- `Identifier` - a `URIRef`, `Literal` or `BNode`

<a id="jinjardf.rdf_filters.RDFFilters.rdf_inverse_property"></a>

#### rdf\_inverse\_property

```python
@staticmethod
@pass_environment
def rdf_inverse_property(environment: RDFEnvironment,
                         object: IdentifiedNode,
                         predicate: str,
                         unique: bool = False) -> List[IdentifiedNode]
```

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

#### rdf\_inverse\_property\_any

```python
@staticmethod
@pass_environment
def rdf_inverse_property_any(environment: RDFEnvironment,
                             object: IdentifiedNode,
                             predicate: str) -> IdentifiedNode
```

Return one arbitrary subject for the pattern (`SUBJ`, `predicate`, `object`).
When used as a Jinja filter, the value passed is the `object`.

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `object` _IdentifiedNode_ - the object resource
- `predicate` _str_ - URI of the predicate
  

**Returns**:

- `IdentifiedNode` - one instance of `IdentifiedNode`, either a `URIRef` or a `BNode`.

<a id="jinjardf.rdf_filters.RDFFilters.sparql_query"></a>

#### sparql\_query

```python
@staticmethod
@pass_environment
def sparql_query(environment: RDFEnvironment, resourceURI: URIRef,
                 query: str) -> Result
```

Run a custom SPARQL query, where each occurrence of `?resourceUri`
is replaced with the `resourceURI` parameter. Returns an iterator over the
resultset, where each result contains the bindings for the selected variables
(in the case of a SELECT query).
See https://rdflib.readthedocs.io/en/latest/apidocs/rdflib.html#rdflib.query.Result.

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `resourceURI` _URIRef_ - URIRef to drop into the query.
- `query` _str_ - the actual query.
  

**Returns**:

- `Result` - the iterable query result

<a id="jinjardf.rdf_filters.RDFFilters.statements_as_subject"></a>

#### statements\_as\_subject

```python
@staticmethod
@pass_environment
def statements_as_subject(environment: RDFEnvironment,
                          resource: IdentifiedNode,
                          as_list: bool = False) -> Generator
```

Return all statements/triples in the graph where the current resource as
passed to the filter is the subject.

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `resource` _IdentifiedNode_ - The resource as passed to the filter as the value.
  

**Yields**:

- `Generator` - The matching statements

<a id="jinjardf.rdf_filters.RDFFilters.statements_as_object"></a>

#### statements\_as\_object

```python
@staticmethod
@pass_environment
def statements_as_object(environment: RDFEnvironment,
                         resource: IdentifiedNode,
                         as_list: bool = False) -> Generator
```

Return all statements/triples in the graph where the current resource as
passed to the filter is the object.

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `resource` _IdentifiedNode_ - The resource as passed to the filter as the value.
  

**Yields**:

- `Generator` - The matching statements

<a id="jinjardf.rdf_filters.RDFFilters.get_text"></a>

#### get\_text

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

#### title

```python
@staticmethod
@pass_environment
def title(environment: RDFEnvironment,
          resource: IdentifiedNode,
          languages: list = [],
          return_first: bool = False,
          default: str = None) -> List[Literal]
```

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

#### description

```python
@staticmethod
@pass_environment
def description(environment: RDFEnvironment,
                resource: IdentifiedNode,
                languages: list = [],
                return_first: bool = False,
                default: str = None) -> List[Literal]
```

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

#### relative\_uri

```python
@staticmethod
@pass_environment
def relative_uri(environment: RDFEnvironment, resource: IdentifiedNode) -> str
```

Returns the URI of this resource relative to the site URL.

**Arguments**:

- `environment` _RDFEnvironment_ - the RDFEnvironment
- `resource` _IdentifiedNode_ - the resource for which we want to get the relative URI
  

**Returns**:

- `str` - the relative URI

