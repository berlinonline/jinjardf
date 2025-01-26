import argparse

def delete_first_asterisk_line(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    modified_lines = []
    first_asterisk_line_found = False

    for line in lines:
        if not first_asterisk_line_found and line.startswith("*"):
            first_asterisk_line_found = True
        else:
            modified_lines.append(line)        

    for modified_line in modified_lines:
        print(modified_line, end="")

parser = argparse.ArgumentParser(
    description="Delete the first line of the TOC (the first line to start with a *).")
parser.add_argument('--input',
                    help="Path to the Markdown file",
                    type=str,
                    )
args = parser.parse_args()

delete_first_asterisk_line(args.input)