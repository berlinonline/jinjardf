"""
`jinjardf.site_generator` generates a static HTML site based on an RDF graph. It does so by
iterating through the graph's resources and applying the appropriate Jinja template to it.
One page will be generated for each resource selected from the graph.

## Configuration

The site generator is configured using a YAML file like this:

```python
generator = SiteGenerator('/path/to/config.yml')
```

The YAML file looks like this:

```yaml
base_url: 'https://berlin.github.io' # the base hostname & protocol for your site, e.g. http://example.com
base_path: '/lod-budget' # the subpath of your site
dataset_path: 'data/temp/all.part.nt' # the path to the RDF file containing the graph (can be any format that
# rdflib can parse).
template_path: 'templates' # the path to the folder containing the Jinja templates
output_path: '_site/' # the output path where all generated HTML files will be placed
prefixes: # a list of prefixes that should be available throughout the site-generation process
  rdf: http://www.w3.org/1999/02/22-rdf-syntax-ns#
  rdfs: http://www.w3.org/2000/01/rdf-schema#
  schema: https://schema.org/
  void: http://rdfs.org/ns/void#
  xsd: http://www.w3.org/2001/XMLSchema#
include: # a list of files and folders that should be copied into the output_path
  - assets/
class_template_mappings: # mappings from classes to templates
  "void:Dataset": "dataset.html.jinja"
```

If you want to run the generator locally for test purposes, you can also pass a second parameter with
URL of the local test site (usually something like `http://localhost:8000`).

## Template Variables

In the templates that have been loaded by the site generator, a number of variables are
available:

- `node`: The node from the input graph that is currently being processed. In other words, resource
for which the current page is being built. `node` is usually an instance of `rdflib.URIRef`, but can
for most purposes be use like a `str` (the URI of the node).
- `base_url`: The base URL of the site, e.g. `https://berlin.github.io`
- `base_path`: The base path of the site, e.g. `/lod-budget`
- `resource_prefix`: BASE_URL + BASE_PATH – the URIs of all resources included in the site are in this namespace
- `prefixes`: A dictionary of prefixes that have been configured for the site generator.
- All prefixes in `prefixes` are also available directly in upper case in the template and are instances
of `rdflib.Namespace`. E.g., if `void: http://rdfs.org/ns/void#` is defined in the configuration, then
in the template we can do `{{ VOID.Dataset }}` to get `http://rdfs.org/ns/void#Dataset`.
"""
from  http.server import SimpleHTTPRequestHandler
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
from berlinonline.jinjardf.theme import Theme

import progressbar

progressbar.streams.wrap_stderr()
LOG = logging.getLogger(__name__)

DEFAULT_BASEPATH = '/'
DEFAULT_RESTRICTION = """
  SELECT ?resourceUri
  WHERE {{
    ?resourceUri ?predicate ?object
    FILTER(STRSTARTS(STR(?resourceUri), '{}'))
  }}
"""
"""
The default SPARQL query for selection of resources from the input graph, if
`restriction_query` is not defined in the YAML config.
It selects all subject URIs which start with the site's resource prefix
(BASE_URL + BASE_PATH).
"""

DEFAULT_PREFIXES = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "dct": "http://purl.org/dc/terms/",
}
"""
A couple of default prefixes that are made available if `prefixes` is not set
in the YAML config.
"""

DEFAULT_DATASET_PATH = 'data/data.ttl'
"""
The default path to the file containing the input RDF graph.
"""

DEFAULT_TEMPLATE_PATH = 'templates'
"""
The default path to the template folder.
"""

DEFAULT_TEMPLATE = 'default.html.jinja'
"""
The name of the default template that gets applied whenever no matching template could be
found in `class_template_mappings`.
"""

DEFAULT_OUTPUT_PATH = 'output'
"""
The default path to the folder where all generated HTML files will be copied.
"""

def generate_output_path_from_resource(resource: URIRef, resource_prefix: str, output_path: str) -> str:
    path = resource.split(resource_prefix).pop()
    local_name = resource.split('/').pop()
    LOG.debug(f" local_name: {local_name}")
    if not local_name:
        local_name = "index"
    else:
        path = path.split(local_name)[0]
    output_path = os.path.join(output_path, path, local_name) + '.html'
    return output_path

def copy_includes(includes, output_path):
    import errno

    def copyanything(src, dst):
        try:
            shutil.copytree(src, dst)
        except OSError as exc: # python >2.5
            if exc.errno in (errno.ENOTDIR, errno.EINVAL):
                shutil.copy(src, dst)
            else:
                raise

    for include in includes:
        destination = os.path.join(output_path, include)
        LOG.info(f" copying {include} to {destination}")
        copyanything(include, destination)



class SiteGenerator(object):
    base_url: str
    base_path: str
    resource_prefix: str
    site_url: str
    themes: list
    prefixes: dict
    sparql_prefixes: str
    template_prefixes: dict
    restriction_query: str
    output_path: str
    include: list
    default_template: str
    class_template_mapping: dict
    resource_template_index: dict
    environment: RDFEnvironment

    def __init__(self, config_path: str, cli_site_url: str=None):

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
        self.site_url = self.read_config('site_url', self.base_url)
        if cli_site_url:
            LOG.info(f" current site_url ({self.site_url}) is overridden by the command line parameter: {cli_site_url}")
            self.site_url = cli_site_url

        self.prefixes = {}

        self.themes = self.read_config('themes', {})
        self.install_themes()

        self.prefixes = self.prefixes | self.read_config('prefixes', DEFAULT_PREFIXES)
        self.template_prefixes = self.prefix_dict_to_template_prefixes(self.prefixes)
        
        self.restriction_query = self.read_config('restriction_query', DEFAULT_RESTRICTION.format(self.resource_prefix))

        dataset_path = self.read_config('dataset_path', DEFAULT_DATASET_PATH)
        template_path = self.read_config('template_path', DEFAULT_TEMPLATE_PATH)
        self.default_template = self.read_config('default_template', DEFAULT_TEMPLATE)
        
        class_template_mappings = self.read_config('class_template_mappings', {})
        self.class_template_mapping = {}
        self.expand_class_template_mappings(class_template_mappings)
        
        loader = FileSystemLoader(template_path)

        self.output_path = self.read_config('output_path', DEFAULT_OUTPUT_PATH)
        self.include = self.read_config('include', [])

        self.environment = RDFEnvironment(dataset=dataset_path,
                                          resource_prefix=self.resource_prefix,
                                          site_url=self.site_url,
                                          prefixes=self.prefixes,
                                          extensions=[RDFFilters],
                                          loader=loader)

        self.template_arguments = {
            'base_url': self.base_url,
            'base_path': self.base_path,
            'resource_prefix': self.resource_prefix,
            'prefixes': self.prefixes
        }

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

    def install_themes(self):
        """Instantiate the themes specified in the config file and copy their resource files
        (templates, assets, config)."""

        for theme_name in self.themes:
            LOG.debug(f" installing theme: {theme_name}")
            theme = Theme(theme_name)
            theme.copy_templates('templates')
            theme.copy_assets('assets')
            config_files = theme.copy_config('config')
            for config_path in config_files:
                LOG.debug(f"reading config from {config_path}")
                with open(config_path) as config_file:
                    theme_config = yaml.safe_load(config_file)
                    theme_prefixes = theme_config['prefixes']
                    self.prefixes = self.prefixes | theme_prefixes

    def extract_resources(self):
        """Run the restriction_query on the loaded RDF data to determine the set
        of resources to include in the static site.
        """
        results = self.environment.graph.query(self.restriction_query)
        resources = set()
        LOG.info(" extracting resources")
        for result in results:
            resources.add(result['resourceUri'])
        LOG.debug(f" got resources for generator: {sorted(resources)}")
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
        arguments = self.template_arguments | self.template_prefixes
        os.makedirs(self.output_path, exist_ok=True)
        copy_includes(self.include, self.output_path)
        resource_class_index = self.compute_resource_class_index(resources)
        class_superclass_index = self.compute_class_superclass_index(resource_class_index)
        self.resource_template_index = self.compute_resource_template_index(resources, resource_class_index, class_superclass_index)

        with progressbar.ProgressBar(max_value=len(self.resource_template_index)) as bar:
            progress_counter = 0
            for resource, template_name in self.resource_template_index.items():
                LOG.debug(f" rendering {resource} with template {template_name} ...")
                template = self.environment.get_template(template_name)
                rendered = template.render(node=resource, **arguments)
                output_path = generate_output_path_from_resource(resource, self.resource_prefix, self.output_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                LOG.debug(f" writing to {output_path} ...")
                with open(output_path, "w") as file:
                    file.write(rendered)
                bar.update(progress_counter)
                progress_counter += 1
    
    def serve_site(self, port: int=8000): # pragma: no cover
        os.chdir(self.output_path)
        with socketserver.TCPServer(("", port), CustomHandler) as httpd:
            print(f"Serving {self.output_path} at http://localhost:{port}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down the server.")
                httpd.server_close()

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
        LOG.debug("determining resource_class_index ...")
        for resource in resources:
            resource_class_index[resource] = []
        for resourceUri, p, classUri in self.environment.graph.triples( ( None, RDF.type, None ) ): 
            if resourceUri in resources:
                resource_class_index[resourceUri].append(classUri)
        LOG.debug(f" resource_class_index: {resource_class_index}")
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
        LOG.debug("determining class_superclass_index ...")
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
        LOG.debug(f" class_superclass_index: {class_superclass_index}")
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
        LOG.debug("determining resource_template_index ...")
        mapping_classes = self.class_template_mapping.keys()
        resource_template_index = {}
        # the following only covers resources which have a type
        for resource, classUris in resource_class_index.items():
            # problem here: if len(classUris) > 1, the last one wins, all others are ignored
            # we need a way to prioritize
            for classUri in classUris:
                superclasses = class_superclass_index[classUri] + [classUri]
                intersection = [ superclass for superclass in superclasses if superclass in mapping_classes ]
                template_class = intersection.pop()
                resource_template_index[resource] = self.class_template_mapping[template_class]
        # get all resources that do not have a class and assign them the default template
        not_covered = {resource: self.default_template
                       for resource in resources
                       if resource_class_index[resource] == []}
        # merge both mappings
        resource_template_index = not_covered | resource_template_index
        LOG.debug(f" resource_template_index: {resource_template_index}")
        return resource_template_index

class ConfigException(Exception):
    pass

class CustomHandler(SimpleHTTPRequestHandler): # pragma: no cover
    """A custom request handler that can serve *.html files without their file extension.
    I.e., I can request `xxxxx` and get `xxxxx.html`.
    """
    def do_GET(self):
        # Check if the request is for a file without extension
        if self.path == '/':
            self.path == 'index.html'
        elif not os.path.splitext(self.path)[1]:  # No extension in the requested path
            self.path += ".html"  # Append .html extension
            
        # Call the parent handler to serve the file
        super().do_GET()
