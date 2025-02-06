[![Tests](https://github.com/berlinonline/jinjardf/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/berlinonline/jinjardf/actions)
[![Code Coverage](https://codecov.io/github/berlinonline/jinjardf/coverage.svg?branch=main)](http://codecov.io/github/berlinonline/jinjardf?branch=main)

# Jinja-RDF

Jinja-RDF provides the tools necessary to build static sites for RDF graphs:

* several [custom filters](https://berlinonline.github.io/jinjardf/doc/rdf_filters) for [Jinja](https://jinja.palletsprojects.com) for working with RDF data
* a [custom Jinja environment](https://berlinonline.github.io/jinjardf/doc/rdf_environment) that keeps a reference to an RDF graph
* a [site generator](https://berlinonline.github.io/jinjardf/doc/site_generator) class that …
  * reads and interprets the configuration,
  * iterates through a configurable part of the RDF graph,
  * maps RDF resources to Jinja templates based on their class, and
  * outputs static HTML files for each resource.
* a [theme class](https://berlinonline.github.io/jinjardf/doc/theme) to facilitate installing themes of templates for the site generator

## Why?

What is the point of this? – 
RDF is a format for graph data, where (more or less) each node in the graph is identified by a URI.
That makes it a great format for integrating heterogeneous data from different sources.
But if we use made-up URIs that cannot be resolved, we're not taking advantage of the power of the Web, and our data is only half as useful.
So, the point of creating web sites for RDF graphs boils down to #3 of the four Linked Data principles:

1. Use URIs as names for things
2. Use HTTP URIs so that people can look up those names.
3. **When someone looks up a URI, provide useful information, using the standards (RDF, SPARQL).**
4. Include links to other URIs, so that they can discover more things.

(https://www.w3.org/DesignIssues/LinkedData)

## How?

Typically, when you create an RDF dataset, you will introduce or define a lot of new URIs.
These will be the things or data points that are new or unique to your dataset.
E.g., if you create statistical data with the [RDF Data Cube Vocabulary](https://www.w3.org/TR/vocab-data-cube/), your data will introduce a lot of observations, and each of these gets a URI that you define.
If you model an organizational structure and publish it as a dataset (e.g. using the [Organization Ontology](https://www.w3.org/TR/vocab-org/)), you will introduce URIs for organizations, their units, roles, posts and people.

When you define (or "coin") new URIs, you need to decide in which domain they will be.
Any valid domain will be fine to create valid RDF, but if you want to *provide useful information when someone looks up a URI*, it has to be a domain that you own, or where you can publish.
That may sound very obvious, but it's also very important.

Almost every RDF dataset also includes a lot of external URIs that have been defined elsewhere: terms from vocabularies and ontologies, reference resources (e.g. from Wikidata) etc.
While your dataset is effectively adding information to these URIs, you cannot *provide useful information about them* to someone looking them up.

## Dependencies

* Jinja-RDF was tested with Python 3.12, but might work with other versions.
* [Jinja](https://jinja.palletsprojects.com) (`jinja2`) is used as the templating language.
* [RDFLib](https://rdflib.readthedocs.io) (`rdflib`) is used for RDF loading, querying and graph traversal. 
* [PyYAML](https://pyyaml.org/wiki/PyYAML) (`pyyaml`) is used for parsing configuration.

For a complete list of Python dependencies see [requirements.txt](requirements.txt).

## Installation

TODO: Finish

### From Source

If you want to install from source, clone this repository.
Create a virtual environment, activate it, then install the [dependencies](requirements.txt) into it:

```
$ python -m venv venv
$ . venv/bin/activate
(venv) $ pip install -r requirements.txt
```

### Via PyPi


## Inspiration

Jinja-RDF is inspired by [Jekyll-RDF](https://github.com/AKSW/jekyll-rdf), an extension for the Jekyll static site builder.
Jekyll is a Ruby application, and so Jekyll-RDF uses [Ruby-RDF](https://github.com/ruby-rdf).
Ruby-RDF is great, but I had some issues loading largish datasets with it.
Also, I find the Jinja2 templating language more convenient than Liquid, that Jekyll uses.

## License

All code in this repository is published under the [MIT License](License).
