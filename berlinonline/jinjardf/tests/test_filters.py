from types import NoneType
from typing import Generator
import pytest
from rdflib import RDF, BNode, Literal, URIRef
from rdflib.namespace import DCTERMS
from rdflib.term import Identifier

from berlinonline.jinjardf.rdf_environment import RDFEnvironment
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
        uri = 'https://schema.org/Person'
        resource = RDFFilters.rdf_get(uri)
        assert resource.toPython() == uri 

    def test_returns_resource_for_resource(self):
        uri = 'https://schema.org/Person'
        resource = URIRef(uri)
        assert RDFFilters.rdf_get(resource) == resource

class TestToPython(object):

    @pytest.mark.parametrize('data', [
        {
            'node': Literal("hello"),
            'expected': 'hello',
            'type': str
        },
        {
            'node': Literal(42),
            'expected': 42,
            'type': int
        },
        {
            'node': Literal(True),
            'expected': True,
            'type': bool
        },
        {
            'node': URIRef('https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DonaldDuck'),
            'expected': 'https://berlinonline.github.io/jinja-rdf-demo/example/ducks/DonaldDuck',
            'type': str
        },
        {
            'node': None,
            'expected': None,
            'type': NoneType
        }
    ])
    def test_return_value_has_correct_type(self, data):
        value = RDFFilters.toPython(data['node'])
        assert value == data['expected']
        assert isinstance(value, data['type'])

class TestTypeCheckers(object):

    @pytest.mark.parametrize('data', [
        {
            'node': Literal("hello"),
            'expected': False,
        },
        {
            'node': BNode(),
            'expected': False,
        },
        {
            'node': URIRef('http://example.com/foo/bar'),
            'expected': True,
        },
    ])
    def test_is_iri(self, data):
        assert RDFFilters.is_iri(data['node']) == data['expected']

    @pytest.mark.parametrize('data', [
        {
            'node': Literal("hello"),
            'expected': False,
        },
        {
            'node': BNode(),
            'expected': True,
        },
        {
            'node': URIRef('http://example.com/foo/bar'),
            'expected': False,
        },
    ])
    def test_is_bnode(self, data):
        assert RDFFilters.is_bnode(data['node']) == data['expected']

    @pytest.mark.parametrize('data', [
        {
            'node': Literal("hello"),
            'expected': False,
        },
        {
            'node': BNode(),
            'expected': True,
        },
        {
            'node': URIRef('http://example.com/foo/bar'),
            'expected': True,
        },
    ])
    def test_is_resource(self, data):
        assert RDFFilters.is_resource(data['node']) == data['expected']

    @pytest.mark.parametrize('data', [
        {
            'node': Literal("hello"),
            'expected': True,
        },
        {
            'node': BNode(),
            'expected': False,
        },
        {
            'node': URIRef('http://example.com/foo/bar'),
            'expected': False,
        },
    ])
    def test_is_literal(self, data):
        assert RDFFilters.is_literal(data['node']) == data['expected']

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

    def test_return_all_subjects(self, duck_environment):
        subjects = RDFFilters.rdf_inverse_property(duck_environment, object=SCHEMA.Person, predicate=RDF.type)
        assert isinstance(subjects, list)
        assert len(subjects) == 12

class TestRDFInversePropertyAny(object):

    def test_return_one_subject(self, duck_environment):
        subject = RDFFilters.rdf_inverse_property_any(duck_environment, object=SCHEMA.Person, predicate=RDF.type)
        assert isinstance(subject, URIRef)

    def test_return_none(self, duck_environment):
        subject = RDFFilters.rdf_inverse_property_any(duck_environment, object=SCHEMA.Person, predicate=DUCKS.imagined_property)
        assert subject is None


class TestSPARQLQuery(object):

    def test_resource_uri_replaced_correctly(self, duck_environment):
        query = """
            PREFIX schema: <https://schema.org/>
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

    def test_title_returns_default(self, literal_environment):
        default_title = Literal('(no title)')
        titles = RDFFilters.title(literal_environment, LITERALS.something_no_title, languages=['de'], default=default_title)
        assert titles == [ default_title ]

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
    def test_title_any_returns_literal(self, literal_environment: RDFEnvironment, data: list):
        title = RDFFilters.title_any(literal_environment, data['resourceUri'], languages=data['languages'])
        assert isinstance(title, data['resultType'])
        assert title == data['expected']

    def test_title_any_returns_default(self, literal_environment):
        default_title = Literal('(no title)')
        titles = RDFFilters.title_any(literal_environment, LITERALS.something_no_title, languages=['de'], default=default_title)
        assert titles == default_title


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

class TestRelativeURI(object):

    @pytest.mark.parametrize('data', [
        {
            'resourceUri': LITERALS.something,
            'site_url': 'https://berlinonline.github.io/jinja-rdf/example/literals',
            'expected': '/jinja-rdf/example/literals/something'
        },
        {
            'resourceUri': LITERALS.something,
            'site_url': 'http://localhost:8000',
            'expected': '/something'
        },
        {
            'resourceUri': SCHEMA.Person,
            'site_url': 'https://berlinonline.github.io/jinja-rdf/example/literals',
            'expected': str(SCHEMA.Person)
        },
        {
            'resourceUri': 'https://berlinonline.github.io/jinja-rdf/example/literals/foo/bar',
            'site_url': 'https://berlinonline.github.io/jinja-rdf/example/literals',
            'expected': '/jinja-rdf/example/literals/foo/bar'
        },
        {
            'resourceUri': 'https://berlinonline.github.io/jinja-rdf/example/literals/foo/bar',
            'site_url': 'http://localhost:8000',
            'expected': '/foo/bar'
        },
        {
            'resourceUri': 'https://berlinonline.github.io/jinja-rdf/example/literals/assets/css/style.css',
            'site_url': 'https://berlinonline.github.io/jinja-rdf/example/literals',
            'expected': '/jinja-rdf/example/literals/assets/css/style.css'
        },
        {
            'resourceUri': 'https://berlinonline.github.io/jinja-rdf/example/literals/assets/css/style.css',
            'site_url': 'http://localhost:8000',
            'expected': '/assets/css/style.css'
        },
    ])
    def test_relative_uri_generated_correctly(self, literal_environment: RDFEnvironment, data: list):
        literal_environment.site_url = data['site_url']
        assert RDFFilters.relative_uri(literal_environment, data['resourceUri']) == data['expected']
