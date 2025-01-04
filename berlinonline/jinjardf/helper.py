def replace_curies(text: str, namespaces: dict)->str:
    """Apply a list of namespace mappings (prefix->namespace URI) to an
    arbitrary text containing CURIEs. Replace all CURIEs with the full URI.

    Args:
        text (str): The string containing CURIEs
        namespaces (dict): A dict with mappings from prefixes ('rdfs') to
        to namespace URIs ('http://www.w3.org/2000/01/rdf-schema#').

    Returns:
        str: The string with all CURIEs replaced with full URIs.
    """

    for prefix, namespaceURI in namespaces.items():
        text = text.replace(prefix + ":", namespaceURI)
    
    return text

def split_curie(curie: str) -> tuple[str, str]:
    if ':' in curie:
        parts = curie.split(":")
        parts = [ None if part == '' else part for part in parts]
        return parts[0], parts[1]
    else:
        raise BadCurieException(f"'{curie}' does not look like a CURIE.")

class BadCurieException(Exception):
    pass