import os

def get_project_files(directory, exclude_dirs=None, exclude_extensions=None):
    """
    Recursively gets all file paths in a given directory, excluding specified directories and file extensions.

    Args:
        directory (str): The root directory to start searching from.
        exclude_dirs (list): A list of directory names to exclude (e.g., ['.git', '__pycache__']).
        exclude_extensions (list): A list of file extensions to exclude (e.g., ['.pyc', '.log']).

    Returns:
        list: A list of absolute paths to the files.
    """
    if exclude_dirs is None:
        exclude_dirs = ['.git', '__pycache__', 'venv', '.vscode']
    if exclude_extensions is None:
        exclude_extensions = ['.pyc', '.log', '.DS_Store']

    file_paths = []
    for root, dirs, files in os.walk(directory):
        # Modify dirs in-place to exclude directories from traversal
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if not any(file.endswith(ext) for ext in exclude_extensions):
                file_paths.append(os.path.join(root, file))
    return file_paths

def read_file_content(file_path):
    """
    Reads the content of a single file.

    Args:
        file_path (str): The absolute path to the file.

    Returns:
        str: The content of the file, or None if an error occurs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def get_project_context(directory):
    """
    Reads the content of all relevant files in a project directory and returns them as a single string.

    Args:
        directory (str): The root directory of the project.

    Returns:
        str: A concatenated string of all file contents, formatted with file paths.
    """
    all_content = []
    file_paths = get_project_files(directory)
    for file_path in file_paths:
        content = read_file_content(file_path)
        if content:
            # Format: --- START FILE: path/to/file.py ---\ncontent\n--- END FILE: path/to/file.py ---\n
            # Make path relative to the provided directory for cleaner output
            relative_path = os.path.relpath(file_path, directory)
            all_content.append(f"--- START FILE: {relative_path} ---\n{content}\n--- END FILE: {relative_path} ---\n")
    return "\n".join(all_content)