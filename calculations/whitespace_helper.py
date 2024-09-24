import sys

def replace_newlines_with_spaces(file_path):
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Replace newlines with spaces
        modified_content = content.replace('\n', ' ')

        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)

        print(f"Successfully replaced newlines with spaces and wrote back to the file: {file_path}")

    except Exception as e:
        print(f"An error occurred while processing the file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python whitespace_helper.py.py <file_path>")
    else:
        replace_newlines_with_spaces(sys.argv[1])