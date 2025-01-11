import os
import pathlib

import pytest
from rdflib import Namespace

from berlinonline.jinjardf.rdf_environment import RDFEnvironment

DUCKS = Namespace('https://berlinonline.github.io/jinja-rdf/example/ducks/')
FAMILY = Namespace('https://berlinonline.github.io/jinja-rdf/example/ducks/vocab/')
LITERALS = Namespace('https://berlinonline.github.io/jinja-rdf/example/literals/')
SCHEMA = Namespace('https://schema.org/')

def create_environment(filename: str, resource_prefix: str, site_url: str) -> RDFEnvironment:
    # load test data
    test_folder = pathlib.Path(__file__).parent.resolve()
    data_path = os.path.join(test_folder, "data", filename)
    return RDFEnvironment(dataset=data_path, resource_prefix=resource_prefix, site_url=site_url)


@pytest.fixture
def duck_environment():
    """Fixture to load the duck test data
    """
    # load test data
    site_url = 'https://berlinonline.github.io/jinja-rdf/example/ducks'
    resource_prefix = site_url + '/'
    environment = create_environment(filename='ducks.ttl', resource_prefix=resource_prefix, site_url=site_url)
    yield environment
    # empty the graph
    environment.graph.remove( (None, None, None) )

@pytest.fixture
def literal_environment():
    """Fixture to load some literals as test data
    """
    # load test data
    site_url = 'https://berlinonline.github.io/jinja-rdf/example/literals'
    resource_prefix = site_url + '/'
    environment = create_environment(filename='literals.ttl', resource_prefix=resource_prefix, site_url=site_url)
    yield environment
    # empty the graph
    environment.graph.remove( (None, None, None) )

