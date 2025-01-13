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
DEFAULT_DESCRIPTION_PROPERTIES = [
    RDFS.comment,
    DCT.description,
    SCHEMA.description
]

class RDFFilters(Extension):
    """Implementation of a Jinja2 extension that provides various filters for
    working with RDF data. The filters are based on the rdflib library.

    See https://rdflib.readthedocs.io/en/stable/
    """
    
    def __init__(self, environment):
        super().__init__(environment)

        environment.filters['rdf_get'] = self.rdf_property
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
        """Return an rdflib URIRef with the IRI that was passed as the value.
        When used as a Jinja filter, the value passed is the `iri`.

        Args:
            iri (str): The IRI of the resource.

        Returns:
            URIRef: The returned resource.
        """

        return URIRef(iri)

    @staticmethod
    def is_iri(node: Node) -> bool:
        return isinstance(node, URIRef)

    @staticmethod
    def is_bnode(node: Node) -> bool:
        return isinstance(node, BNode)

    @staticmethod
    def is_resource(node: Node) -> bool:
        return isinstance(node, IdentifiedNode)

    @staticmethod
    def is_literal(node: Node) -> bool:
        return isinstance(node, Literal)

    @staticmethod
    @pass_environment
    def rdf_property(environment: RDFEnvironment, subject: IdentifiedNode, predicate: str, language: str=None, unique: bool=False) -> List[Identifier]:
        """Return one or all of the objects for the pattern (`subject`, `predicate`, `OBJ`).
        If an optional language code is provided, the results will be filtered to only
        contain literals with that language.
        When used as a Jinja filter, the value passed is the `subject`.

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            subject (IdentifiedNode): the subject resource
            predicate (str): URI of the property
            language (str, optional): language code like `en` or `fr`. Defaults to None.
            unique (bool, optional): Set to True if only unique results should be returned. Defaults to False.

        Returns:
            List[rdflib.term.Identifier]: a list of nodes (URIRef, Literal or BNode)
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
    def rdf_property_any(environment: RDFEnvironment, subject: IdentifiedNode, predicate: str, language: str = None) -> Literal:
        objects = RDFFilters.rdf_property(environment, subject, predicate, language)
        return objects.pop() if len(objects) > 0 else None

    @staticmethod
    @pass_environment
    def rdf_inverse_property(environment: RDFEnvironment, object: IdentifiedNode, predicate: str, as_list: bool=False, unique: bool=False) -> List[IdentifiedNode]:
        """Return one or all of the subjects for the pattern (`SUBJ`, `predicate`, `object`).
        When used as a Jinja filter, the value passed is the `object`.

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            object (IdentifiedNode): The object resource.
            predicate (str): URI of the predicate
            as_list (bool, optional): Set to True if multiple results should be returned. Defaults to False.
            unique (bool, optional): Set to True if only unique results should be returned. Defaults to False.

        Returns:
             List[rdflib.IdentifiedNode]: a list of subject nodes (URIRef or BNode)
        """
        graph = environment.graph
        subjects = list(graph.subjects(predicate=URIRef(predicate), object=object, unique=unique))
        if as_list:
            return subjects
        else:
            return subjects.pop() if len(subjects) > 0 else None

    @staticmethod
    @pass_environment
    def sparql_query(environment: RDFEnvironment, resourceURI: URIRef, query: str) -> Result:
        """Run a custom SPARQL query, where each occurrence of `?resourceUri`
        is replaced with the `resourceURI` parameter. Returns an iterator over the 
        resultset, where each result contains the bindings for the selected variables
        (in the case of a SELECT query).
        See https://rdflib.readthedocs.io/en/latest/apidocs/rdflib.html#rdflib.query.Result.

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            resourceURI (URIRef): URIRef to drop into the query.
            query (str): the actual query.

        Returns:
            Result: the iterable query result
        """

        graph = environment.graph
        query = query.replace("?resourceUri", f"<{resourceURI.toPython()}>")
        result = graph.query(query)
        return result

    @staticmethod
    @pass_environment
    def statements_as_subject(environment: RDFEnvironment, resource: IdentifiedNode, as_list: bool=False) -> Generator:
        """Return all statements/triples in the graph where the current resource as
        passed to the filter is the subject.

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            resource (IdentifiedNode): The resource as passed to the filter as the value.

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
        """Find all literals connected to `resource` via any of the `properties`, for all `languages` and return them as a list,

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            resource (IdentifiedNode): the resource for which to find literals
            properties (list): the list of properties to use
            languages (list, optional): list of language codes. Defaults to [].
            return_first (bool, optional): If True, only return the first literal found. Defaults to False.
            default (str, optional): If no matching literals are found, return this. Defaults to None.

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
