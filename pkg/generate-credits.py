# Call this manually every time the metadata in pkg/credits changes.
# Commit the generated files.

# Requires:
# - ImageMagick
# - Git Bash (on Windows)

# Usage: python pkg/generate-credits.py

from glob import glob
from os.path import basename, splitext
from subprocess import run

def get_confirmed_names(filename):
    with open(filename, 'r') as file:
        lines = [line.rstrip() for line in file]
        # The first line should always be Confirmed:
        lines = lines[1:]
        # After the confirmed names, there may be Not Confirmed: names.
        if 'Not Confirmed:' in lines:
            lines = lines[0:lines.index('Not Confirmed:')]

        # Lines should either start with "- " or "    " if continuing the previous name, wrapped and indented:
        return [line[2:] for line in lines if len(line) > 0]

def main():
    # Generate about-boe.xml from about-boe-template.xml:
    with open('pkg/credits/about-boe-template.xml', 'r') as template_file:
        template = template_file.read()
        content = template

        name_files = glob('pkg/credits/*.txt')
        name_dict = {}
        num_dict = {}
        total_num = 0
        for name_file in name_files:
            heading, _ = splitext(basename(name_file))
            name_dict[heading] = get_confirmed_names(name_file)
            num_dict[heading] = len(name_dict[heading])
            total_num += len(name_dict[heading])

        def replace_tabbed_lines(placeholder, lines, tabs):
            return content.replace(placeholder, ('\n' + ('\t' * tabs)).join(lines.splitlines()))
            
        # {{Warning}}:
        content = replace_tabbed_lines('{{Warning}}', 'WARNING! This file is generated by pkg/generate-credits.py from\ntpkg/credits/about-boe-template.xml. Do not modify it manually!', 1)

        # {{Height}}: 10 * (total # of lines, which includes 2 at the top and 4 per section break)
        content = content.replace('{{Height}}', str(10 * (total_num + 10)))

        # {{0}}: '<br/>' * (total # of confirmed names in pkg/credits/*.txt)
        content = content.replace('{{0}}', '<br/>' * total_num)

        # {{1}}: '<br/>' * (# of programmers)
        content = content.replace('{{1}}', '<br/>' * num_dict['Programming'])

        # {{2}}: '<br/>' * (# of artists)
        content = content.replace('{{2}}', '<br/>' * num_dict['Graphics'])

        # {{3}}: '<br/>' * (# of testers)
        content = content.replace('{{3}}', '<br/>' * num_dict['Testing'])
        
        # {{4}}: '<br/>' * (# of donors)
        content = content.replace('{{4}}', '<br/>' * num_dict['Funding'])

        list_break = ' <br/>\n'

        # {{5}}: Programmer name lines
        name_lines = list_break.join(name_dict["Programming"]) + list_break
        content = replace_tabbed_lines('{{5}}', name_lines, 8)

        # {{6}}: Artist name lines
        name_lines = list_break.join(name_dict["Graphics"]) + list_break
        content = replace_tabbed_lines('{{6}}', name_lines, 7)

        # {{7}}: Tester name lines
        name_lines = list_break.join(name_dict["Testing"]) + list_break
        content = replace_tabbed_lines('{{7}}', name_lines, 12)

        # {{8}}: Donor names
        name_lines = list_break.join(name_dict["Funding"]) + list_break
        content = replace_tabbed_lines('{{8}}', name_lines, 7)

        with open('rsrc/dialogs/about-boe.xml', 'w') as output_file:
            output_file.write(content)

        # Generate startanim.png using ImageMagick

        image_lines_col1 = []
        image_lines_col2 = []

        # Note: blank lines need to have a space in them for some reason
        def add_heading(heading):
            image_lines_col1.append(f'- {heading.upper()} -')
            image_lines_col1.append(' ')
            image_lines_col2.extend([' ', ' '])
            
            # (Complicated)
            # Split the names into two columns, still vertically alphabetized,
            # while keeping multi-line names on the same column!
            names = name_dict[heading]
            left_column = True

            idx = 0
            while idx < len(names):
                current_column = image_lines_col1 if left_column else image_lines_col2
                current_column.append(names[idx])
                multiline_idx = idx + 1
                while multiline_idx < len(names) and names[multiline_idx].startswith(' '):
                    current_column.append(names[multiline_idx])
                    multiline_idx += 1
                    idx += 1
                left_column = len(image_lines_col1) <= len(image_lines_col2)
                idx += 1

            while len(image_lines_col1) != len(image_lines_col2):
                current_column = image_lines_col1 if left_column else image_lines_col2
                current_column.append(' ')

            image_lines_col1.append(' ')
            image_lines_col2.append(' ')

        add_heading('Programming')
        add_heading('Graphics')
        add_heading('Testing')
        add_heading('Funding')

        # when one column starts with blank lines, ImageMagick doesn't offset the top correctly.
        # So we pass the number of lines to y-offset the right column image
        col2_blank_lines_start = 0
        for line in image_lines_col2:
            if line == ' ':
                col2_blank_lines_start += 1
            else:
                break

        run(['bash', 'pkg/generate-startanim-col.sh', '1', '0'], input='\n'.join(image_lines_col1), encoding='ascii')
        # print(col2_blank_lines_start)
        run(['bash', 'pkg/generate-startanim-col.sh', '2', str(col2_blank_lines_start)], input='\n'.join(image_lines_col2), encoding='ascii')
        run(['bash', 'pkg/generate-startanim.sh'])

if __name__ == "__main__":
    main()