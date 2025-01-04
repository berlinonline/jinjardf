from jinja2 import Environment
from rdflib import Graph



class RDFEnvironment(Environment):
    """Subclass of a Jinja 2 Environment for applying templates to
    RDF data. Keeps a reference to the RDF graph which contains the
    data.
    """
    def __init__(self, dataset: str, **kwargs):
        super().__init__(**kwargs)
        self.graph = Graph()
        if (dataset):
            self.graph.parse(dataset)
