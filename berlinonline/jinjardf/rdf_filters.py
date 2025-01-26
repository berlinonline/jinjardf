"""
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

```jinja
{{ 'https://example.com/foo/bar' | rdf_get }}
```

In this case, 'https://example.com/foo/bar' would be passed to `rdf_get()` as the `iri` parameter.

The `rdf_property()` function (see above) would be used as a filter like this:

```jinja
{{ node | rdf_property(RDFS.label, 'en', true) }}
```

In this case, the function's `environment` parameter was passed by the `pass_environment` decorator, 
`node` from the template is passed as the `subject` parameter, and `RDFS.label`, `'en'` and `true` are
passed as the function's remaining three parameters `predicate`, `language` and `unique`.

## Examples

The documentation for the filter functions below includes examples of how to use them as filters
in a Jinja template.
For these examples, we assume the graph loaded by the `RDFEnvironment` contains the RDF from this
dataset: https://berlinonline.github.io/jinja-rdf-demo/example/ducks/

"""

import logging
from typing import Generator, List
from urllib.parse import urlparse

from jinja2.ext import Extension
from jinja2 import pass_environment
from rdflib import BNode, IdentifiedNode, Literal, URIRef, RDFS, Namespace
from rdflib.term import Identifier, Node
from rdflib.query import Result

from berlinonline.jinjardf.rdf_environment import RDFEnvironment

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)
DCT = Namespace('http://purl.org/dc/terms/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
SCHEMA = Namespace('https://schema.org/')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
UNTAGGED = 'untagged'

DEFAULT_TITLE_PROPERTIES = [
    RDFS.label,
    DCT.title,
    FOAF.name,
    SCHEMA.name,
    SKOS.prefLabel,
]
"""A list of properties that all mean something like 'title' and are used by
the `title()` and `title_any()` filters.
"""

DEFAULT_DESCRIPTION_PROPERTIES = [
    RDFS.comment,
    DCT.description,
    SCHEMA.description,
]
"""A list of properties that all mean something like 'description' and are used by
the `description()` and `description_any()` filters.
"""

class RDFFilters(Extension):
    """Implementation of a Jinja2 extension that provides various filters for
    working with RDF data. The filters are based on the rdflib library.

    See https://rdflib.readthedocs.io/en/stable/
    """
    
    def __init__(self, environment):
        super().__init__(environment)

        environment.filters['rdf_get'] = self.rdf_property
        environment.filters['toPython'] = self.toPython
        environment.filters['is_iri'] = self.is_iri
        environment.filters['is_bnode'] = self.is_bnode
        environment.filters['is_resource'] = self.is_resource
        environment.filters['is_literal'] = self.is_literal
        environment.filters['rdf_property'] = self.rdf_property
        environment.filters['rdf_property_any'] = self.rdf_property_any
        environment.filters['rdf_inverse_property'] = self.rdf_inverse_property
        environment.filters['sparql_query'] = self.sparql_query
        environment.filters['statements_as_subject'] = self.statements_as_subject
        environment.filters['statements_as_object'] = self.statements_as_object
        environment.filters['title'] = self.title
        environment.filters['title_any'] = self.title_any
        environment.filters['description'] = self.description
        environment.filters['description_any'] = self.description_any
        environment.filters['relative_uri'] = self.relative_uri

    @staticmethod
    def rdf_get(iri: str) -> URIRef:
        """Return an rdflib `URIRef` with the IRI that was passed as the value.
        When used as a Jinja filter, the value passed is the `iri`.
        This is useful when we want to use use rdflib's API for URIRefs, or if we
        want to compare the IRI with another URIRef.

        **Usage in a template**:

        The (somewhat contrieved) example is using `rdf_get` to turn a string into
        a URIRef object, so what we can use the `n3()` function on it.
        (https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#rdflib.term.URIRef.n3)

        ```jinja
        {% set iri_string = 'https://example.com/foo/bar' %}
        {% set iri = iri_string | rdf_get %}
        {{ iri.n3() }}
        ```

        ```html
        <https://example.com/foo/bar>
        ```

        Args:
            iri (str): The IRI of the resource.

        Returns:
            URIRef: The returned resource.
        """

        return URIRef(iri)

    @staticmethod
    def toPython(node: Node):
        """Returns an appropriate python datatype for the rdflib type of `node`, or `None` if
        `node` is `None`. This is useful if we want to compare the value of a literal
        with a Jinja (Python) object, such as a String.

        **Usage in a template**:

        - `node`: https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck

        ```jinja
        {% set gender = node | rdf_property_any(SCHEMA.gender) | toPython %}
        {% if gender == 'female' %}
            weiblich
        {% elif gender == 'male' %}
            männlich
        {% else %}
            sonstiges
        {% endif %}
        ```

        ```html
        weiblich
        ```

        Args:
            node (Node): the node to convert

        Returns:
            _type_: an appropriate python representation of `node` (str, int, boolean etc.)
        """
        value = None
        if node:
            value = node.toPython()
        return value

    @staticmethod
    def is_iri(node: Node) -> bool:
        """Return `True` if `node` is an IRI (URI) resource, `False` if not.

        **Usage in a template**:

        - `node`: https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck
        
        ```jinja
        {% if node | is_iri %}
            {{ node }} is an IRI.
        {% endif %}
        ```

        ```html
        https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck is an IRI.
        ```

        Args:
            node (Node): the node to test

        Returns:
            bool: `True` is `node` is an IRI, `False` if not.
        """
        return isinstance(node, URIRef)

    @staticmethod
    def is_bnode(node: Node) -> bool:
        """Return `True` if `node` is a blank node resource, `False` if not.

        **Usage in a template**:

        - `node`: https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck
        
        ```jinja
        {% if node | is_bnode %}
            {{ node }} is a Bnode.
        {% else %}
            {{ node }} is not a Bnode.
        {% endif %}
        ```

        ```html
        https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck is not a Bnode.
        ```

        Args:
            node (Node): the node to test

        Returns:
            bool: `True` is `node` is a bnode, `False` if not.
        """
        return isinstance(node, BNode)

    @staticmethod
    def is_resource(node: Node) -> bool:
        """Return `True` if `node` is a resource (either IRI or bnode), `False` if not.

        **Usage in a template**:

        - `node`: https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck
        
        ```jinja
        {% if node | is_resource %}
            {{ node }} is a resource.
        {% endif %}
        ```

        ```html
        https://example.com/foo/bar is a resource.
        ```

        Args:
            node (Node): the node to test

        Returns:
            bool: `True` is `node` is a resource, `False` if not.
        """
        return isinstance(node, IdentifiedNode)

    @staticmethod
    def is_literal(node: Node) -> bool:
        """Return `True` if `node` is a literal, `False` if not.

        **Usage in a template**:

        - `node`: https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck
        
        ```jinja
        {% set title = node | title_any(language=['en']) %}
        {{ node }} is a literal: {% node | is_literal %}<br/>
        '{{ title }}' is a literal: {% title | is_literal %}<br/>
        ```

        ```html
        https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck is a literal: False
        'Della Duck' is a literal: True
        ```

        Args:
            node (Node): the node to test

        Returns:
            bool: `True` is `node` is a literal, `False` if not.
        """
        return isinstance(node, Literal)

    @staticmethod
    @pass_environment
    def rdf_property(environment: RDFEnvironment, subject: IdentifiedNode, predicate: str, language: str=None, unique: bool=False) -> List[Identifier]:
        """Return the objects for the pattern (`subject`, `predicate`, `OBJ`).
        If an optional language code is provided, the results will be filtered to only
        contain literals with that language.
        When used as a Jinja filter, the value passed is the `subject`.

        **Usage in a template**:

        - `node`: https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck
        
        ```jinja
        schema:names: {{ node | rdf_property(SCHEMA.name) }}<br/>
        Japanese schema:names: {{ node | rdf_property(SCHEMA.name, 'ja') }}<br/>
        rdfs:labels: {{ node | rdf_property(RDFS.label) }}<br/>
        ```

        ```html
        schema:names: [ 'Della And', 'Della Duck', 'Ντέλλα Ντακ', 'Della Duck', 'Bella Pato', 'デラ・ダック', … ]
        Japanese schema:names: [ 'デラ・ダック' ]
        rdfs:labels: []
        ```

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            subject (IdentifiedNode): the subject resource
            predicate (str): URI of the property
            language (str, optional): language code like `en` or `fr`. Defaults to `None`.
            unique (bool, optional): Set to `True` if only unique results should be returned. Defaults to `False`.

        Returns:
            List[rdflib.term.Identifier]: a list of nodes (`URIRef`, `Literal` or `BNode`)
        """
        
        graph = environment.graph
        objects = list(graph.objects(subject=subject, predicate=URIRef(predicate), unique=unique))
        if language:
            if language != UNTAGGED:
                objects = [
                    _object 
                        for _object in objects
                        if isinstance(_object, Literal) and _object.language == language
                    ]
            else:
                objects = [
                    _object 
                        for _object in objects
                        if isinstance(_object, Literal) and not _object.language
                    ]

        return objects
    
    @staticmethod
    @pass_environment
    def rdf_property_any(environment: RDFEnvironment, subject: IdentifiedNode, predicate: str, language: str = None) -> Identifier:
        """Return one arbitrary object for the pattern (`subject`, `predicate`, `OBJ`).
        If an optional language code is provided, only a literal with that language will
        be returned.
        When used as a Jinja filter, the value passed is the `subject`.

        **Usage in a template**:

        - `node`: https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck
        
        ```jinja
        any schema:name: {{ node | rdf_property_any(SCHEMA.name) }}<br/>
        any Japanese schema:name: {{ node | rdf_property_any(SCHEMA.name, 'ja') }}<br/>
        any rdfs:label: {{ node | rdf_property_any(RDFS.label) }}<br/>
        ```

        ```html
        any schema:name: 'Della And'
        any Japanese schema:name: 'デラ・ダック'
        any rdfs:label: None
        ```

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            subject (IdentifiedNode): the subject resource
            predicate (str): URI of the property
            language (str, optional): language code like `en` or `fr`. Defaults to `None`.

        Returns:
            Identifier: a `URIRef`, `Literal` or `BNode`
        """
        objects = RDFFilters.rdf_property(environment, subject, predicate, language)
        return objects.pop() if len(objects) > 0 else None

    @staticmethod
    @pass_environment
    def rdf_inverse_property(environment: RDFEnvironment, object: IdentifiedNode, predicate: str, unique: bool=False) -> List[IdentifiedNode]:
        """Return the subjects for the pattern (`SUBJ`, `predicate`, `object`).
        When used as a Jinja filter, the value passed is the `object`.

        **Usage in a template**:

        - `node`: https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck
        
        ```jinja
        {# Find Della's children by using `hasParent` in the inverse direction. #}
        {% set children =  node | rdf_inverse_property(FAMILY.hasParent) %}
        Della's children: 
        <ul>
        {% for child in children %}
          <li>{{ child }}</li>
        {% endfor %}
        </ul>
        ```

        ```html
        Della's children:
        <ul>
          <li>https://berlinonline.github.io/jinja-rdf-demo/example/ducks/Dewey</li>
          <li>https://berlinonline.github.io/jinja-rdf-demo/example/ducks/Huey</li>
          <li>https://berlinonline.github.io/jinja-rdf-demo/example/ducks/Louie</li>
        </ul>
        ```

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            object (IdentifiedNode): The object resource.
            predicate (str): URI of the predicate
            unique (bool, optional): Set to `True` if only unique results should be returned. Defaults to `False`.

        Returns:
             List[rdflib.IdentifiedNode]: a list of subject nodes (`URIRef` or `BNode`)
        """
        graph = environment.graph
        subjects = list(graph.subjects(predicate=URIRef(predicate), object=object, unique=unique))
        return subjects

    @staticmethod
    @pass_environment
    def rdf_inverse_property_any(environment: RDFEnvironment, object: IdentifiedNode, predicate: str) -> IdentifiedNode:
        """Return one arbitrary subject for the pattern (`SUBJ`, `predicate`, `object`).
        When used as a Jinja filter, the value passed is the `object`.

        **Usage in a template**:

        - `node`: https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck
        
        ```jinja
        {# Pick any of Della's children by using `hasParent` in the inverse direction. #}
        {% set child =  node | rdf_inverse_property_any(FAMILY.hasParent) %}
        Della's child: {{ child }}
        ```

        ```html
        Della's child: https://berlinonline.github.io/jinja-rdf-demo/example/ducks/Huey
        ```

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            object (IdentifiedNode): the object resource
            predicate (str): URI of the predicate

        Returns:
            IdentifiedNode: one instance of `IdentifiedNode`, either a `URIRef` or a `BNode`.
        """
        subjects = RDFFilters.rdf_inverse_property(environment, object, predicate)
        return subjects.pop() if len(subjects) > 0 else None


    @staticmethod
    @pass_environment
    def sparql_query(environment: RDFEnvironment, resourceURI: URIRef, query: str) -> Result:
        """Run a custom SPARQL query, where each occurrence of `?resourceUri`
        is replaced with the `resourceURI` parameter. Returns an rdflib.query.Result object.
        What this actually is depends on the type of query (see
        https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#rdflib.query.Result). In the
        typical case of a SELECT query the result is an iterator of rdflib.query.ResultRow obejcts,
        where each row represents one result and gives access to the variable bindings as attributes
        (`result.variable`) or via `[]` notation (`result['variable']).
        
        Returns an iterator over the 
        resultset, where each result contains the bindings for the selected variables
        (in the case of a SELECT query).
        See https://rdflib.readthedocs.io/en/latest/apidocs/rdflib.html#rdflib.query.Result.

        **Usage in a template**:

        - `node`: https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DellaDuck

        ```jinja
        {% set sibling_query = '''
        SELECT DISTINCT ?sibling
        WHERE {
            ?resourceUri family:hasParent ?parent .
            ?sibling family:hasParent ?parent .
            FILTER(?sibling != ?resourceUri)
        }
        '''%}
        {% set results = node | sparql_query(sibling_query) %}
        {% if results %}
            <ul>
            {% for result in results %}
                <li>{{ result['sibling'] }}</li>
            {% endfor %}
            </ul>
        {% endif %}
        ```

        ```html
        <ul>
            <li>https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DonaldDuck</li>
        </ul>
        ```

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            resourceURI (URIRef): URIRef to drop into the query
            query (str): the actual query

        Returns:
            rdflib.query.Result: the query result
        """

        graph = environment.graph
        query = query.replace("?resourceUri", f"<{resourceURI}>")
        result = graph.query(query)
        return result

    @staticmethod
    @pass_environment
    def statements_as_subject(environment: RDFEnvironment, resource: IdentifiedNode, as_list: bool=False) -> Generator:
        """Return all statements/triples in the graph where the current resource as
        passed to the filter is the subject.

        **Usage in a template**:

        - `node`: https://berlinonline.github.io/jinja-rdf-demo/example/ducks/

        ```jinja
        Statements with literal objects about {{ node }}:
        {%- if statements | length > 0 %}
            <table>
                <tr>
                    <th>Property</th>
                    <th>Literal</th>
                </tr>
                {% for s, p, o in statements -%}
                    {%- if o | is_literal %}
                        <tr>
                            <td>{{ p }}</td>
                            <td>"{{ o }}"</td>
                        </tr>
                    {%- endif -%}
                {%- endfor %}
            </table>
        {% endif %}
        ```
        
        ```html
        Statements with literal objects about https://berlinonline.github.io/jinja-rdf-demo/example/ducks/:
        <table>
            <tr>
                <th>Property</th>
                <th>Literal</th>
            </tr>
            <tr>
                <td>http://purl.org/dc/terms/created</td>
                <td>"2024-12-13"</td>
            </tr>
            <tr>
                <td>http://purl.org/dc/terms/description</td>
                <td>"Excerpt of the family tree of the fictional character Donald Duck. Sources for the family tree are Wikipedia, for names in different languages Wikidata."</td>
            </tr>
            <tr>
                <td>http://purl.org/dc/terms/modified</td>
                <td>"2025-01-21"</td>
            </tr>
            <tr>
                <td>http://purl.org/dc/terms/title</td>
                <td>"Duck Family Tree"</td>
            </tr>
        </table>
        ```

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            resource (IdentifiedNode): The resource as passed to the filter as the value.
            as_list (bool): If True, return a list instead of a generator. Defaults to `False`.
            Useful if we want to know the size of the resultset before iterating through it.

        Yields:
            Generator: The matching statements
        """

        graph = environment.graph
        statements = graph.triples( (resource, None, None) )
        if as_list:
            statements = list(statements)
        return statements

    @staticmethod
    @pass_environment
    def statements_as_object(environment: RDFEnvironment, resource: IdentifiedNode, as_list: bool=False) -> Generator:
        """Return all statements/triples in the graph where the current resource as
        passed to the filter is the object.

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            resource (IdentifiedNode): The resource as passed to the filter as the value.
            as_list (bool): If True, return a list instead of a generator. Defaults to `False`.
            Useful if we want to know the size of the resultset before iterating through it.

        Yields:
            Generator: The matching statements 
        """

        graph = environment.graph
        statements = graph.triples( (None, None, resource) )
        if as_list:
            statements = list(statements)
        return statements
    
    @staticmethod
    @pass_environment
    def get_text(environment: RDFEnvironment, resource: IdentifiedNode, properties: list, languages: list=[], return_first: bool=False, default: str=None) -> List[Literal]:
        """Find all literals connected to `resource` via any of the `properties`, for all `languages`
        and return them as a list. This is e.g. used to get all titles, or all descriptions of a resource,
        by passing a list of desired title-properties (`rdfs:label`, `dct:title`, `schema:name` etc.) or
        description-properties (`rdfs:comment`, `dct:description`, `schema:description` etc.).

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            resource (IdentifiedNode): the resource for which to find literals
            properties (list): the list of properties to use
            languages (list, optional): list of language codes. Defaults to `[]`.
            return_first (bool, optional): If `True`, only return the first literal found. Defaults to `False`.
            default (str, optional): If no matching literals are found, return this. Defaults to `None`.

        Returns:
            List[Literal]: the list of literals found
        """

        literals = []

        # append UNTAGGED as default
        languages.append(UNTAGGED)

        for language in languages:
            LOG.debug(f" getting literals for language: {language}")
            for property in properties:
                LOG.debug(f"   checking {property}")
                if literal := RDFFilters.rdf_property_any(environment, resource, property, language):
                    if return_first:
                        return literal
                    literals.append(literal)
        if len(literals) == 0 and default:
            literals = [ default ]
        if return_first:
            if len(literals) == 0:
                return None
            else:
                return literals.pop()
        return literals

    @staticmethod
    @pass_environment
    def title(environment: RDFEnvironment, resource: IdentifiedNode, languages: list=[], return_first: bool=False, default: str=None) -> List[Literal]:
        """Find all titles (as defined by in the `environment`) for all languages specified and return them
        as a list.

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            resource (IdentifiedNode): the resource for which to find title
            languages (list): list of language codes
            return_first (bool, optional): If True, only return the first title found. Defaults to False.
            default (str): If no matching titles are found, return this.

        Returns:
            list: the list of titles found
        """

        return RDFFilters.get_text(environment=environment,
                                   resource=resource,
                                   properties=DEFAULT_TITLE_PROPERTIES,
                                   languages=languages,
                                   return_first=return_first,
                                   default=default)

    @staticmethod
    @pass_environment
    def title_any(environment: RDFEnvironment, resource: IdentifiedNode, languages: list=[], default: str=None) -> Literal:
        return RDFFilters.title(environment=environment, resource=resource, languages=languages, return_first=True, default=default)
    
    @staticmethod
    @pass_environment
    def description(environment: RDFEnvironment, resource: IdentifiedNode, languages: list=[], return_first: bool=False, default: str=None) -> List[Literal]:
        """Find all descriptions (as defined by in the `environment`) for all languages specified and return them
        as a list.

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            resource (IdentifiedNode): the resource for which to find title
            languages (list): list of language codes
            return_first (bool, optional): If True, only return the first title found. Defaults to False.
            default (str): If no matching titles are found, return this.

        Returns:
            list: the list of titles found
        """

        return RDFFilters.get_text(environment=environment,
                                   resource=resource,
                                   properties=DEFAULT_DESCRIPTION_PROPERTIES,
                                   languages=languages,
                                   return_first=return_first,
                                   default=default)

    @staticmethod
    @pass_environment
    def description_any(environment: RDFEnvironment, resource: IdentifiedNode, languages: list=[], default: str=None) -> Literal:
        return RDFFilters.description(environment=environment, resource=resource, languages=languages, return_first=True, default=default)

    @staticmethod
    @pass_environment
    def relative_uri(environment: RDFEnvironment, resource: IdentifiedNode) -> str:
        """Returns the URI of this resource relative to the site URL.

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            resource (IdentifiedNode): the resource for which we want to get the relative URI

        Returns:
            str: the relative URI
        """

        resource_uri = str(resource)
        path = resource_uri
        if resource_uri.startswith(environment.site_url):
            path = urlparse(resource_uri).path
        elif resource_uri.startswith(environment.resource_prefix):
            path = '/' + resource_uri.removeprefix(environment.resource_prefix)

        return path
