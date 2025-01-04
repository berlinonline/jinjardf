import http.server
import logging
import os
import shutil
import socketserver
from urllib.parse import urljoin
from typing import Dict

import yaml
from jinja2 import FileSystemLoader
from rdflib import OWL, RDF, RDFS, Namespace, URIRef
from rdflib.paths import OneOrMore

from berlinonline.jinjardf.helper import replace_curies, split_curie
from berlinonline.jinjardf.rdf_environment import RDFEnvironment
from berlinonline.jinjardf.rdf_filters import RDFFilters

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

DEFAULT_BASEPATH = '/'
DEFAULT_RESTRICTION = """
  SELECT ?resourceUri
  WHERE {{
    ?resourceUri ?predicate ?object
    FILTER(STRSTARTS(STR(?resourceUri), '{}'))
  }}
"""
DEFAULT_PREFIXES = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "dct": "http://purl.org/dc/terms/",
}
DEFAULT_DATASET_PATH = 'data/data.ttl'
DEFAULT_TEMPLATE_PATH = 'templates'
DEFAULT_TEMPLATE = 'default.html.jinja'
DEFAULT_OUTPUT_PATH = 'output'

def generate_output_path_from_resource(resource: URIRef, resource_prefix: str, output_path: str) -> str:
    path = resource.split(resource_prefix).pop()
    local_name = resource.split('/').pop()
    LOG.info(f" local_name: {local_name}")
    if not local_name:
        local_name = "index"
    else:
        path = path.split(local_name)[0]
    output_path = os.path.join(output_path, path, local_name) + '.html'
    return output_path

class SiteGenerator(object):
    base_path: str
    resource_prefix: str
    prefixes: dict
    sparql_prefixes: str
    template_prefixes: dict
    restriction_query: str
    output_path: str
    default_template: str
    class_template_mapping: dict
    resource_template_index: dict
    environment: RDFEnvironment

    def __init__(self, config_path: str):

        if not os.path.isfile(config_path):
            raise ConfigException(f" no file found at {config_path}")

        with open(config_path) as config_file:
            LOG.info(f" loading configuration from {config_path} ...")
            self.config = yaml.safe_load(config_file)
        
        if not self.config:
            raise ConfigException(f" config at {config_path} is empty")

        if 'base_url' not in self.config:
            raise ConfigException(f"No 'base_url' field found in {config_path}.")
        self.base_url = self.config['base_url']
        LOG.info(f" reading base_url: '{self.base_url}' ...")

        self.base_path = self.read_config('base_path', DEFAULT_BASEPATH)

        self.resource_prefix = urljoin(self.base_url, os.path.join(self.base_path, ''))

        self.prefixes = self.read_config('prefixes', DEFAULT_PREFIXES)
        self.sparql_prefixes = self.prefix_dict_to_sparql(self.prefixes)
        self.template_prefixes = self.prefix_dict_to_template_prefixes(self.prefixes)
        
        self.restriction_query = self.read_config('restriction_query', DEFAULT_RESTRICTION.format(self.resource_prefix))

        dataset_path = self.read_config('dataset_path', DEFAULT_DATASET_PATH)
        template_path = self.read_config('template_path', DEFAULT_TEMPLATE_PATH)
        self.default_template = self.read_config('default_template', DEFAULT_TEMPLATE)
        
        class_template_mappings = self.config.get('class_template_mappings', {})
        self.class_template_mapping = {}
        self.expand_class_template_mappings(class_template_mappings)
        
        loader = FileSystemLoader(template_path)

        self.output_path = self.read_config('output_path', DEFAULT_OUTPUT_PATH)

        self.environment = RDFEnvironment(dataset=dataset_path, extensions=[RDFFilters], loader=loader)

    def read_config(self, config_key: str, default):
        """Read a value from the config and return it. If config_key is not included,
        return the default instead. Write an appropriate log message for each case.

        Args:
            config_key (str): the key for this setting in the config dictionary
            default (_type_): the default value for this setting

        Returns:
            _type_: Either the value read from the config or the default.
        """
        value = self.config.get(config_key, default)
        if config_key not in self.config:
            LOG.info(f" {config_key} not found in config, using default '{default}' ...")
        else:
            LOG.info(f" reading {config_key}: '{value}' ...")
        return value

    def extract_resources(self):
        """Run the restriction_query on the loaded RDF data to determine the set
        of resources to include in the static site.
        """
        results = self.environment.graph.query(self.restriction_query)
        resources = set()
        for result in results:
            resources.add(result['resourceUri'])
        LOG.info(f" got resources for generator: {sorted(resources)}")
        return resources

    def expand_class_template_mappings(self, class_template_mappings: dict) -> Dict[URIRef, str]:
        for curie, template in class_template_mappings.items():
            prefix, localname = split_curie(curie)
            if prefix in self.prefixes:
                self.class_template_mapping[URIRef(replace_curies(curie, self.prefixes))] = template
            else:
                raise ConfigException(f" prefix in mapping '{curie}'->'{template}' not defined")
        if OWL.Thing not in self.class_template_mapping:
            self.class_template_mapping[OWL.Thing] = self.default_template

    def clear_site(self):
        if os.path.isdir(self.output_path):
            shutil.rmtree(self.output_path)

    def generate_site(self, resources: list):
        prefixes = self.template_prefixes
        os.makedirs(self.output_path, exist_ok=True)
        resource_class_index = self.compute_resource_class_index(resources)
        class_superclass_index = self.compute_class_superclass_index(resource_class_index)
        self.resource_template_index = self.compute_resource_template_index(resources, resource_class_index, class_superclass_index)

        for resource, template_name in self.resource_template_index.items():
            LOG.info(f" rendering {resource} with template {template_name} ...")
            template = self.environment.get_template(template_name)
            rendered = template.render(node=resource, **prefixes)
            output_path = generate_output_path_from_resource(resource, self.resource_prefix, self.output_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            LOG.info(f" writing to {output_path} ...")
            with open(output_path, "w") as file:
                file.write(rendered)
    
    def serve_site(self, port: int=8000): # pragma: no cover
        os.chdir(self.output_path)
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"Serving {self.output_path} at http://localhost:{port}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down the server.")
                httpd.server_close()

    def prefix_dict_to_sparql(self, prefixes: dict) -> str:
        sparql_prefixes = "\n".join(f"PREFIX {prefix}: {url}" for prefix, url in prefixes.items())
        return sparql_prefixes

    def prefix_dict_to_template_prefixes(self, prefixes: dict) -> dict:
        template_prefixes = { prefix.upper(): Namespace(url) for prefix, url in prefixes.items() }
        return template_prefixes
    
    def compute_resource_class_index(self, resources: list) -> Dict[URIRef, list]:
        """Compute an index dict from resources to classes (rdf:type). The index is computed
        based on the current RDF graph, and only resources are included in the index that are
        contained in the list of resources passed to the function.

        Args:
            resources (list): The list of resources to be considered.

        Returns:
            dict: A dict from resource URIs to class URIs, or None if no class is defined.
        """
        resource_class_index = {}
        LOG.info("determining resource_class_index ...")
        for resource in resources:
            resource_class_index[resource] = []
        for resourceUri, p, classUri in self.environment.graph.triples( ( None, RDF.type, None ) ): 
            if resourceUri in resources:
                resource_class_index[resourceUri].append(classUri)
        LOG.info(f" resource_class_index: {resource_class_index}")
        return resource_class_index
    
    def compute_class_superclass_index(self, resource_class_index: dict) -> Dict[URIRef, list]:
        """Compute an index dict from class URIs to lists of class URIs which are their 
        superclasses, based on the current RDF graph. We consider all classes that are included
        in the `resource_class_index`.
        The list of superclasses is ordered from least to most specific. Also, every list of
        superclasses that doesn't already begin with owl:Thing will have owl:Thing added as the 
        least specific superclass. This means that all resource keys in the index have at least 
        [ owl:Thing ] as their list of superclasses.

        Args:
            resource_class_index (dict): An index dict from resource URIs to lists of class URIs.

        Returns:
            Dict[URIRef, list]: An index dict from class URIs to lists of class URIs (the superclasses).
        """

        class_superclass_index = {}
        LOG.info("determining class_superclass_index ...")
        allClassUris = set([classUri 
                         for classUris in resource_class_index.values()
                         for classUri in classUris ])
        # classUris = set(resource_class_index.values())
        for classUri in allClassUris:
            superclasses = []
            for s, p, o in self.environment.graph.triples( (classUri, RDFS.subClassOf*OneOrMore, None) ):
                superclasses.append(o)
            # Every branch of superclasses implicitly ends in owl:Thing. We materialize that here:
            if classUri is not OWL.Thing:
                superclasses.append(OWL.Thing)
            superclasses.reverse() # we want from least to most specific
            class_superclass_index[classUri] = superclasses
        LOG.info(f" class_superclass_index: {class_superclass_index}")
        return class_superclass_index

    def compute_resource_template_index(self, resources: list, resource_class_index: dict, class_superclass_index: dict) -> Dict[URIRef, str]:
        """Compute an index dict from resource URIs to template names.

        Args:
            resources (list): The list of resources to be considered
            resource_class_index (dict): The index of resources to classes
            class_superclass_index (dict): The index of classes to superclasses

        Returns:
            Dict[URIRef, str]: The index from resource URIs to template names.
        """
        LOG.info("determining resource_template_index ...")
        mapping_classes = self.class_template_mapping.keys()
        resource_template_index = {}
        # the following only covers resources which have a type
        for resource, classUris in resource_class_index.items():
            for classUri in classUris:
                superclasses = class_superclass_index[classUri] + [classUri]
                intersection = [ superclass for superclass in superclasses if superclass in mapping_classes ]
                template_class = intersection.pop()
                resource_template_index[resource] = self.class_template_mapping[template_class]
        # get all resources that do not have a class and assign them the default template
        not_covered = {resource: DEFAULT_TEMPLATE
                       for resource in resources
                       if resource_class_index[resource] == []}
        # merge both mappings
        resource_template_index = not_covered | resource_template_index
        LOG.info(f" resource_template_index: {resource_template_index}")
        return resource_template_index

class ConfigException(Exception):
    pass