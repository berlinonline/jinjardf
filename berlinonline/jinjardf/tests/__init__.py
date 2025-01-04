import os
import pathlib

import pytest
from rdflib import Namespace

from berlinonline.jinjardf.rdf_environment import RDFEnvironment

DUCKS = Namespace('https://berlinonline.github.io/jinja-rdf/example/ducks/')
FAMILY = Namespace('https://berlinonline.github.io/jinja-rdf/example/ducks/vocab/')
LITERALS = Namespace('https://berlinonline.github.io/jinja-rdf/example/literals/')
SCHEMA = Namespace('http://schema.org/')

def create_environment(filename: str) -> RDFEnvironment:
    # load test data
    test_folder = pathlib.Path(__file__).parent.resolve()
    data_path = os.path.join(test_folder, "data", filename)
    return RDFEnvironment(data_path)


@pytest.fixture
def duck_environment():
    """Fixture to load the duck test data
    """
    # load test data
    environment = create_environment("ducks.ttl")
    yield environment
    # empty the graph
    environment.graph.remove( (None, None, None) )

@pytest.fixture
def literal_environment():
    """Fixture to load some literals as test data
    """
    # load test data
    environment = create_environment("literals.ttl")
    yield environment
    # empty the graph
    environment.graph.remove( (None, None, None) )

