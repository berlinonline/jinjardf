import argparse

def inject_raw_tags(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    modified_lines = []
    inside_code_block = False

    for line in lines:
        if line.strip().startswith("```"):
            if not inside_code_block:
                # Start of a code block
                modified_lines.append("{% raw %}\n")
                inside_code_block = True
            else:
                # End of a code block
                inside_code_block = False
            modified_lines.append(line)
            if not inside_code_block:
                modified_lines.append("{% endraw %}\n")
        else:
            modified_lines.append(line)

    for modified_line in modified_lines:
        print(modified_line, end="")

parser = argparse.ArgumentParser(
    description="Surround code block in input Markdown file with {% raw %} and {% endraw %}.")
parser.add_argument('--input',
                    help="Path to the Markdown file",
                    type=str,
                    )
args = parser.parse_args()

inject_raw_tags(args.input)