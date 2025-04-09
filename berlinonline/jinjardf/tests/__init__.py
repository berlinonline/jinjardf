import os
import pathlib
from posixpath import dirname
import shutil

import pytest
from rdflib import Namespace

from berlinonline.jinjardf.rdf_environment import RDFEnvironment

DUCKS = Namespace('https://berlinonline.github.io/jinja-rdf/example/ducks/')
FAMILY = Namespace('https://berlinonline.github.io/jinja-rdf/example/ducks/vocab/')
LITERALS = Namespace('https://berlinonline.github.io/jinja-rdf/example/literals/')
SCHEMA = Namespace('https://schema.org/')

def create_environment(filename: str, resource_prefix: str, site_url: str, sparql_prefixes='') -> RDFEnvironment:
    # load test data
    test_folder = pathlib.Path(__file__).parent.resolve()
    data_path = os.path.join(test_folder, "data", filename)
    return RDFEnvironment(dataset=data_path, resource_prefix=resource_prefix, site_url=site_url, sparql_prefixes=sparql_prefixes)


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
def duck_environment_with_prefixes():
    """Fixture to load the duck test data
    """
    # load test data
    site_url = 'https://berlinonline.github.io/jinja-rdf/example/ducks'
    resource_prefix = site_url + '/'
    sparql_prefixes = 'PREFIX schemax: <https://schema.org/>\
    PREFIX familx: <https://berlinonline.github.io/jinja-rdf/example/ducks/vocab/>\
    '
    environment = create_environment(filename='ducks.ttl', resource_prefix=resource_prefix, site_url=site_url, sparql_prefixes=sparql_prefixes)

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

def _create_temporary_folder(folder_name: str) -> str:
    """Create a temporary folder for testing.

    Args:
        folder_name (str): the name of the folder

    Returns:
        str: the full path ofthe created folder
    """
    current_dir = dirname(os.path.realpath(__file__))
    folder_path = os.path.join(current_dir, folder_name)

    # create the folder
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    return folder_path

def _remove_temporary_folder(folder_path: str):
    """Remove a temporary folder."""
    shutil.rmtree(folder_path)

@pytest.fixture
def temporary_template_folder():
    """Fixture to create a temporary template folder and delete it after
    the test."""

    template_folder_path = _create_temporary_folder('_temp_templates')

    yield template_folder_path

    _remove_temporary_folder(template_folder_path)

@pytest.fixture
def temporary_asset_folder():
    """Fixture to create a temporary asset folder and delete it after
    the test."""

    asset_folder_path = _create_temporary_folder('_temp_assets')

    yield asset_folder_path

    _remove_temporary_folder(asset_folder_path)

@pytest.fixture
def temporary_config_folder():
    """Fixture to create a temporary config folder and delete it after
    the test."""

    config_folder_path = _create_temporary_folder('_temp_config')

    yield config_folder_path

    _remove_temporary_folder(config_folder_path)

