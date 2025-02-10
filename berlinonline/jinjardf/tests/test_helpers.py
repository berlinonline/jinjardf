import pytest

from berlinonline.jinjardf.helper import BadCurieException, replace_curies, split_curie, is_valid_package_path


class TestReplaceCuries(object):

    @pytest.mark.parametrize("data", [
        {
            "text": "foaf:Person",
            "prefixes": {
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "foaf": "http://xmlns.com/foaf/0.1/"
            },
            "output": "http://xmlns.com/foaf/0.1/Person"
        },
        {
            "text": "foaf:Person",
            "prefixes": {
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "void": "http://rdfs.org/ns/void#"
            },
            "output": "foaf:Person"
        },
        {
            "text": "A foaf:Person is not the same as a foaf:Organization, and not the same as an rdfs:Class or a void:Dataset",
            "prefixes": {
                "foaf": "http://xmlns.com/foaf/0.1/",
                "void": "http://rdfs.org/ns/void#"
            },
            "output": "A http://xmlns.com/foaf/0.1/Person is not the same as a http://xmlns.com/foaf/0.1/Organization, and not the same as an rdfs:Class or a http://rdfs.org/ns/void#Dataset"
        },
    ])
    def testCurieReplacementIsCorrect(self, data):
        assert replace_curies(data['text'], data['prefixes']) == data['output']

class TestSplitCurie(object):

    @pytest.mark.parametrize("data", [
        {
            'curie': 'foo:bar',
            'prefix': 'foo',
            'localPart': 'bar'
        },
        {
            'curie': 'foo:',
            'prefix': 'foo',
            'localPart': None
        },
        {
            'curie': ':bar',
            'prefix': None,
            'localPart': 'bar'
        },
    ])
    def test_curie_split_correctly(self, data):
        prefix, localPart = split_curie(data['curie'])
        assert data['prefix'] == prefix
        assert data['localPart'] == localPart

    def test_bad_curies_raise_error(self):
        with pytest.raises(BadCurieException):
            split_curie('foobar')

class TestPackagePathValidation(object):

    @pytest.mark.parametrize("data", [
        {
            'path': 'foo',
            'expected': True
        },
        {
            'path': '1foo',
            'expected': False
        },
        {
            'path': ' foo',
            'expected': False
        },
        {
            'path': 'foo.bar.baz',
            'expected': True
        },
        {
            'path': 'foo/bar/baz',
            'expected': False
        },
        {
            'path': 'foo-bar-baz',
            'expected': False
        },
        {
            'path': '',
            'expected': False
        },
    ])
    def test_is_valid_package_path(self, data):
        assert is_valid_package_path(data['path']) == data['expected']