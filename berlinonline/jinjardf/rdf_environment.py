from jinja2 import Environment
from rdflib import Graph



class RDFEnvironment(Environment):
    """Subclass of a Jinja 2 Environment for applying templates to
    RDF data. Keeps a reference to the RDF graph which contains the
    data.
    """
    resource_prefix: str
    sparql_prefixes: str
    site_url: str
    graph: Graph

    def __init__(self, dataset: str, resource_prefix: str, site_url: str, prefixes={}, **kwargs):
        super().__init__(**kwargs)
        self.graph = Graph()
        for prefix, url in prefixes.items():
            self.graph.bind(prefix, url)
        if (dataset):
            self.graph.parse(dataset)
        self.resource_prefix = resource_prefix
        self.site_url = site_url