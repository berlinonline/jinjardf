import os
import pathlib

import pytest
from rdflib import Namespace, URIRef, OWL
import yaml

from berlinonline.jinjardf.site_generator import (
    DEFAULT_BASEPATH,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_PREFIXES,
    DEFAULT_RESTRICTION,
    DEFAULT_TEMPLATE,
    ConfigException,
    SiteGenerator,
    generate_output_path_from_resource
)


def build_config_path(config_name: str) -> str:
    test_folder = pathlib.Path(__file__).parent.resolve()
    return os.path.join(test_folder, "config", config_name)

def build_output_path(output_filename: str) -> str:
    test_folder = pathlib.Path(__file__).parent.resolve()
    return os.path.join(test_folder, DEFAULT_OUTPUT_PATH, output_filename)

class TestInstantiation(object):

    def test_missing_config_raises_error(self):
        with pytest.raises(ConfigException):
            SiteGenerator(build_config_path('missing.yml'))
    
    def test_empty_config_raises_error(self):
        with pytest.raises(ConfigException):
            SiteGenerator(build_config_path('empty_config.yml'))

    def test_bad_yaml_raises_error(self):
        with pytest.raises(yaml.parser.ParserError):
            SiteGenerator(build_config_path('bad_yaml_config.yml'))
    
    def test_no_base_url_raises_error(self):
        with pytest.raises(ConfigException):
            SiteGenerator(build_config_path('no_base_url.yml'))
    
    def test_only_base_url_uses_default_settings(self):
        test_folder = pathlib.Path(__file__).parent.resolve()
        os.chdir(test_folder)
        generator = SiteGenerator(build_config_path('only_base_url.yml'))
        assert generator.base_url == 'https://berlinonline.github.io'
        assert generator.base_path == DEFAULT_BASEPATH
        assert generator.default_template == DEFAULT_TEMPLATE
        assert generator.output_path == DEFAULT_OUTPUT_PATH
        assert generator.prefixes == DEFAULT_PREFIXES
        assert generator.restriction_query == DEFAULT_RESTRICTION.format(generator.resource_prefix)
        resources = generator.extract_resources()
        assert isinstance(resources, set)
        assert len(resources) == 3
        assert URIRef('https://berlinonline.github.io/jinjardf/example/') in resources
        generator.clear_site()
        generator.generate_site(resources)
        assert os.path.isfile(build_output_path('index.html'))
        assert os.path.isfile(build_output_path('jinjardf/example/index.html'))
        assert os.path.isfile(build_output_path('jinjardf/something.html'))

    def test_class_hierarchy(self):
        UPPER = Namespace('https://berlinonline.github.io/jinja-rdf/example/class_hierarchy/')
        VOID = Namespace('http://rdfs.org/ns/void#')
        test_folder = pathlib.Path(__file__).parent.resolve()
        os.chdir(test_folder)
        generator = SiteGenerator(build_config_path('things_with_prefixes.yml'))
        resources = generator.extract_resources()
        assert UPPER.Mammal in resources # resource our namespace
        assert VOID.dataset not in resources # resource not in our namespace
        generator.clear_site()
        generator.generate_site(resources)
        assert os.path.isfile(build_output_path('index.html')) # output file in root folder
        assert os.path.isfile(build_output_path('class_hierarchy/Mammal.html')) # nested output file
        assert os.path.isfile(build_output_path('things/fido.html')) # nested output file
        
class TestResourceClassIndex(object):

    def test_resource_class_index(self):
        BO = Namespace('https://berlinonline.github.io/')
        TEST = Namespace('https://berlinonline.github.io/test#')
        test_folder = pathlib.Path(__file__).parent.resolve()
        os.chdir(test_folder)
        generator = SiteGenerator(build_config_path('types.yml'))
        resources = generator.extract_resources()
        resource_class_index = generator.compute_resource_class_index(resources)
        
        # resources with one class
        assert resource_class_index[URIRef(BO)] == [TEST.Thing]
        assert resource_class_index[BO.one] == [TEST.Thing_1]

        # resource with more than one class
        assert set(resource_class_index[BO.two]) == set([TEST.Thing_1, TEST.Thing_2])

        # resource without class
        assert resource_class_index[BO.three] == []

class TestClassSuperclassIndex(object):

    def test_class_superclass_index(self):
        TEST = Namespace('https://berlinonline.github.io/test#')
        test_folder = pathlib.Path(__file__).parent.resolve()
        os.chdir(test_folder)
        generator = SiteGenerator(build_config_path('types.yml'))
        resources = generator.extract_resources()
        resource_class_index = generator.compute_resource_class_index(resources)
        class_superclass_index = generator.compute_class_superclass_index(resource_class_index)
        
        assert TEST.Thing_x not in class_superclass_index.keys() # not a class of a resource in BO
        assert TEST.Thing_3 not in class_superclass_index.keys() # not a direct class of a resource in BO
        assert TEST.Thing_4 not in class_superclass_index.keys() # not a direct class of a resource in BO
        assert TEST.Thing_5 not in class_superclass_index.keys() # not a direct class of a resource in BO

        assert class_superclass_index[TEST.Thing] == [ OWL.Thing ]
        assert class_superclass_index[TEST.Thing_1] == [ OWL.Thing, TEST.Thing_5, TEST.Thing_4, TEST.Thing_3 ]
        assert class_superclass_index[TEST.Thing_2] == [ OWL.Thing, TEST.Thing_5 ]
        assert class_superclass_index[TEST.Thing_6] == [ OWL.Thing ]

class TestResourceTemplateIndex(object):

    def test_resource_template_index(self):
        EXAMPLE = Namespace('https://berlinonline.github.io/jinja-rdf/example/')
        THINGS = Namespace('https://berlinonline.github.io/jinja-rdf/example/things/')
        test_folder = pathlib.Path(__file__).parent.resolve()
        os.chdir(test_folder)
        generator = SiteGenerator(build_config_path('things_with_prefixes.yml'))
        resources = generator.extract_resources()
        resource_class_index = generator.compute_resource_class_index(resources)
        class_superclass_index = generator.compute_class_superclass_index(resource_class_index)
        resource_template_index = generator.compute_resource_template_index(resources, resource_class_index, class_superclass_index)
        assert resource_template_index[URIRef(EXAMPLE)] == 'dataset.html.jinja'
        assert resource_template_index[THINGS.fido] == 'dog.html.jinja'
        assert resource_template_index[THINGS.love] == 'default.html.jinja'
        assert resource_template_index[THINGS.unidentifiedAnimal] == 'animal.html.jinja'
        assert resource_template_index[THINGS.boddy2024] == 'event.html.jinja'

    def test_resource_template_index_fails_with_missing_prefixes(self):
        test_folder = pathlib.Path(__file__).parent.resolve()
        os.chdir(test_folder)
        with pytest.raises(ConfigException):
            SiteGenerator(build_config_path('things.yml'))

    def test_prefer_defined_template_over_default(self):
        MULTIPLE = Namespace('http://example.com/multiple/')
        test_folder = pathlib.Path(__file__).parent.resolve()
        os.chdir(test_folder)
        generator = SiteGenerator(build_config_path('multiple_types.yml'))
        resources = generator.extract_resources()
        resource_class_index = generator.compute_resource_class_index(resources)
        class_superclass_index = generator.compute_class_superclass_index(resource_class_index)
        resource_template_index = generator.compute_resource_template_index(resources, resource_class_index, class_superclass_index)
        assert resource_template_index[MULTIPLE.thing] == 'typeA.html.jinja'
        assert resource_template_index[MULTIPLE.thing2] == 'typeA.html.jinja'
        assert resource_template_index[MULTIPLE.thing3] == 'typeA.html.jinja'
        assert resource_template_index[MULTIPLE.thing4] == 'default.html.jinja'



class TestGeneratePath(object):

    @pytest.mark.parametrize("data", [
        {
            'resource': URIRef('https://berlinonline.github.io/'),
            'output_path': 'output',
            'resource_prefix': 'https://berlinonline.github.io/',
            'expected': 'output/index.html'
        },
        {
            'resource': URIRef('https://berlinonline.github.io/jinjardf/example/'),
            'output_path': 'output',
            'resource_prefix': 'https://berlinonline.github.io/',
            'expected': 'output/jinjardf/example/index.html'
        },
        {
            'resource': URIRef('https://berlinonline.github.io/jinjardf/something'),
            'output_path': 'output',
            'resource_prefix': 'https://berlinonline.github.io/',
            'expected': 'output/jinjardf/something.html'
        },
    ])
    def test_generate_path(self, data):
        assert generate_output_path_from_resource(data['resource'], data['resource_prefix'], data['output_path']) == data['expected']