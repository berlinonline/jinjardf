import argparse
import re

# Regular expression to match raw URLs in docstrings
URL_PATTERN = re.compile(r'(https?://[^\s]+)')

def inject_markdown_links(filepath: str):
    """
    Processes a Python file, converting URLs in docstrings to Markdown links.

    Args:
        filepath (str): The path to the Python file.
    """

    def replace_url(match):
        url = match.group(1)
        return f"[{url}]({url})"


    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    processed_lines = []
    inside_codeblock = False

    for line in lines:
        if line.strip().startswith("```"):
            inside_codeblock = not inside_codeblock
        if inside_codeblock:
            processed_lines.append(line)
        else:
            processed_lines.append(URL_PATTERN.sub(replace_url, line))

    for processed_line in processed_lines:
        print(processed_line, end="")

parser = argparse.ArgumentParser(
    description="Replace links with markdown links.")
parser.add_argument('--input',
                    help="Path to the source file",
                    type=str,
                    )
args = parser.parse_args()

inject_markdown_links(args.input)