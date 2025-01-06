from types import NoneType
from typing import Generator
import pytest
from rdflib import RDF, Literal, URIRef
from rdflib.namespace import DCTERMS
from rdflib.term import Identifier

from berlinonline.jinjardf.rdf_filters import UNTAGGED, RDFFilters
from berlinonline.jinjardf.tests import (
    DUCKS,
    LITERALS,
    SCHEMA,
    duck_environment,
    literal_environment,
)


class TestRDFget(object):

    def test_returns_resource_with_correct_uri_for_string(self):
        uri = 'http://schema.org/Person'
        resource = RDFFilters.rdf_get(uri)
        assert resource.toPython() == uri 

    def test_returns_resource_for_resource(self):
        uri = 'http://schema.org/Person'
        resource = URIRef(uri)
        assert RDFFilters.rdf_get(resource) == resource

class TestRDFProperty(object):

    def test_returns_all_objects(self, literal_environment):
        objects = RDFFilters.rdf_property(literal_environment, subject=LITERALS.something, predicate=DCTERMS.title)
        assert isinstance(objects, list)
        assert len(objects) == 4
        assert isinstance(objects[0], Identifier)


    def test_returns_correct_object_with_language_tag(self, literal_environment):
        objects = RDFFilters.rdf_property(literal_environment, subject=LITERALS.something, predicate=DCTERMS.title, language='en')
        assert isinstance(objects, list)
        assert len(objects) == 1
        _object = objects.pop()
        assert _object.language
        assert str(_object) == "english"

    def test_returns_empty_list_with_nonexistant_language_tag_as_list(self, literal_environment):
        objects = RDFFilters.rdf_property(literal_environment, subject=LITERALS.something, predicate=DCTERMS.title, language='xx')
        assert isinstance(objects, list)
        assert len(objects) == 0

class TestRDFPropertyAny(object):

    def test_returns_one_object(self, literal_environment):
        _object = RDFFilters.rdf_property_any(literal_environment, subject=LITERALS.something, predicate=DCTERMS.title)
        assert isinstance(_object, Identifier)

    def test_returns_untagged(self, literal_environment):
        _object = RDFFilters.rdf_property_any(literal_environment, subject=LITERALS.something, predicate=DCTERMS.title, language=UNTAGGED)
        assert isinstance(_object, Literal)
        assert str(_object) == "untagged"
        _object = RDFFilters.rdf_property_any(literal_environment, subject=LITERALS.something_2, predicate=DCTERMS.title, language=UNTAGGED)
        assert isinstance(_object, Literal)
        assert str(_object) == "untagged"
    
    def test_returns_correct_language(self, literal_environment):
        _object = RDFFilters.rdf_property_any(literal_environment, subject=LITERALS.something, predicate=DCTERMS.title, language='de')
        assert isinstance(_object, Literal)
        assert str(_object) == "deutsch"
        _object = RDFFilters.rdf_property_any(literal_environment, subject=LITERALS.something_2, predicate=DCTERMS.title, language='fr')
        assert isinstance(_object, Literal)
        assert str(_object) == "français"
    
    def test_returns_none_with_nonexistant_language_tag(self, literal_environment):
        _object = RDFFilters.rdf_property_any(literal_environment, subject=LITERALS.something, predicate=DCTERMS.title, language='xx')
        assert _object is None
    

class TestRDFInverseProperty(object):

    def test_return_all_subjects_with_as_list(self, duck_environment):
        subjects = RDFFilters.rdf_inverse_property(duck_environment, object=SCHEMA.Person, predicate=RDF.type, as_list=True)
        assert isinstance(subjects, list)
        assert len(subjects) == 12

    def test_return_one_subject_without_as_list(self, duck_environment):
        subject = RDFFilters.rdf_inverse_property(duck_environment, object=SCHEMA.Person, predicate=RDF.type)
        assert isinstance(subject, URIRef)

class TestSPARQLQuery(object):

    def test_resource_uri_replaced_correctly(self, duck_environment):
        query = """
            PREFIX schema: <http://schema.org/>
            PREFIX family: <https://berlinonline.github.io/jinja-rdf/example/ducks/vocab/>
            SELECT ?mother
            WHERE { 
                ?resourceUri family:hasParent ?mother.
                ?mother schema:gender 'female' .
            }
        """
        results = RDFFilters.sparql_query(duck_environment, resourceURI=DUCKS.DonaldDuck, query=query)
        assert len(results) == 1
        for result in results:
            assert result['mother'] == DUCKS.HortenseMcDuck

class TestTitle(object):

    @pytest.mark.parametrize("data", [
        {
            'resourceUri': LITERALS.something,
            'languages': ['de', 'en'],
            'expected': [Literal('deutsch', lang='de'), Literal('english', lang='en'), Literal('untagged', lang=None)]
        },
        {
            'resourceUri': LITERALS.something_2,
            'languages': ['da', 'it'],
            'expected': [Literal('untagged', lang=None)]
        },
        {
            'resourceUri': LITERALS.something_3,
            'languages': ['da', 'it'],
            'expected': [Literal('dansk', lang='da')]
        },
    ])
    def test_title_returns_list(self, literal_environment, data):
        titles = RDFFilters.title(literal_environment, data['resourceUri'], languages=data['languages'])
        assert isinstance(titles, list)
        assert titles == data['expected']

    @pytest.mark.parametrize("data", [
        {
            'resourceUri': LITERALS.something,
            'languages': ['de', 'en'],
            'resultType': Literal,
            'expected': Literal('deutsch', lang='de'),
            'comment': "first choice exists, so return it"
        },
        {
            'resourceUri': LITERALS.something,
            'languages': ['da', 'en'],
            'resultType': Literal,
            'expected': Literal('english', lang='en'),
            'comment': "first choice doesn't exist, so return second choice"
        },
        {
            'resourceUri': LITERALS.something_2,
            'languages': ['da', 'it'],
            'resultType': Literal,
            'expected': Literal('untagged', lang=None),
            'comment': "no choice exists, so return untagged literal if present"
        },
        {
            'resourceUri': LITERALS.something_3,
            'languages': ['it'],
            'resultType': NoneType,
            'expected': None,
            'comment': "no choice exists and no untagged exists, so return None"
        },
    ])
    def test_title_any_returns_literal(self, literal_environment, data):
        title = RDFFilters.title_any(literal_environment, data['resourceUri'], languages=data['languages'])
        assert isinstance(title, data['resultType'])
        assert title == data['expected']

class TestStatementsAsSubject(object):

    def test_statements_as_subject(self, duck_environment):
        statements = RDFFilters.statements_as_subject(duck_environment, DUCKS.HortenseMcDuck)
        assert isinstance(statements, Generator)
        count = 0
        for s, p, o in statements:
            count += 1
            assert s == DUCKS.HortenseMcDuck
            assert isinstance(p, URIRef)
            assert isinstance(o, Identifier)
        assert count == 9