import logging
from typing import Generator, List

from jinja2.ext import Extension
from jinja2 import pass_environment
from rdflib import IdentifiedNode, Literal, URIRef, RDFS, Namespace
from rdflib.term import Identifier
from rdflib.query import Result

from berlinonline.jinjardf.rdf_environment import RDFEnvironment

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)
DCT = Namespace('http://purl.org/dc/terms/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
SCHEMA = Namespace('http://schema.org/')
UNTAGGED = 'untagged'

DEFAULT_TITLE_PROPERTIES = [
    RDFS.label,
    DCT.title,
    FOAF.name,
    SCHEMA.name,
]

class RDFFilters(Extension):
    """Implementation of a Jinja2 extension that provides various filters for
    working with RDF data. The filters are based on the rdflib library.

    See https://rdflib.readthedocs.io/en/stable/
    """
    
    def __init__(self, environment):
        super().__init__(environment)

        environment.filters['rdf_get'] = self.rdf_property
        environment.filters['rdf_property'] = self.rdf_property
        environment.filters['rdf_inverse_property'] = self.rdf_inverse_property
        environment.filters['sparql_query'] = self.sparql_query
        environment.filters['statements_as_subject'] = self.statements_as_subject
        environment.filters['title'] = self.title
        environment.filters['title_any'] = self.title_any

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
    @pass_environment
    def rdf_property(environment: RDFEnvironment, subject: IdentifiedNode, predicate: str, language: str=None, unique: bool=False) -> List[Identifier]:
        """Return one or all of the objects for the pattern (`subject`, `predicate`, `OBJ`).
        If an optional language code is provided, the results will be filtered to only
        contain literals with that language.
        When used as a Jinja filter, the value passed is the `subject`.

        Args:
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
    def statements_as_subject(environment: RDFEnvironment, resource: IdentifiedNode) -> Generator:
        """Return all statements/triples in the graph where the current resource as
        passed to the filter is the subject.

        Args:
            resource (IdentifiedNode): The resource as passed to the filter as the value.

        Yields:
            Generator: The matching statements 
        """

        graph = environment.graph
        return graph.triples( (resource, None, None) )
    
    @staticmethod
    @pass_environment
    def title(environment: RDFEnvironment, resource: IdentifiedNode, languages: list=[], return_first: bool=False) -> list:
        """Find all titles (as defined by in the `environment`) for all languages specified and return them
        as a list.

        Args:
            environment (RDFEnvironment): the RDFEnvironment
            resource (IdentifiedNode): the resource for which to find title
            languages (list): list of language codes
            return_first (bool, optional): If True, only return the first title found. Defaults to False.

        Returns:
            list: the list of titles found
        """

        titles = []

        # append UNTAGGED as default
        languages.append(UNTAGGED)

        for language in languages:
            LOG.info(f" getting titles for language: {language}")
            for property in DEFAULT_TITLE_PROPERTIES:
                LOG.info(f"   checking {property}")
                if title := RDFFilters.rdf_property_any(environment, resource, property, language):
                    if return_first:
                        return title
                    titles.append(title)
        if len(titles) == 0 and return_first:
            return None
        return titles
    

    @staticmethod
    @pass_environment
    def title_any(environment: RDFEnvironment, resource: IdentifiedNode, languages: list=[]) -> Literal:
        return RDFFilters.title(environment, resource, languages, return_first=True)