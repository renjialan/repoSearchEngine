import os
import chromadb
import uuid
from git import Repo
from typing import List
import re
from typing import List, Tuple 

# Configuration
save_path = "./database/"
collection_name = "file_chunks"

# Ensure the database directory exists
if not os.path.exists(save_path):
    os.makedirs(save_path)

# ChromaDB client and collection
chroma_client = chromadb.PersistentClient(path=save_path)
collection = chroma_client.get_or_create_collection(name=collection_name)

class FileChunk:
    def __init__(self, content, metadata=None):
        self.uuid = str(uuid.uuid4())
        self.content = content
        self.metadata = metadata or {}

def extract_file_chunks(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            # Extract metadata here if needed
            metadata = {"file_path": os.path.basename(file_path)}  # Default metadata
            classes, functions = extract_classes_and_functions(content)
            if classes:
                metadata["classes"] = classes
            if functions:
                metadata["functions"] = ", ".join(functions)  # Convert list to comma-separated string
            return FileChunk(content=content, metadata=metadata)
    except UnicodeDecodeError:
        print(f"Skipping non-text file: {file_path}")
        return None
    except Exception as e:
        print(f"Error extracting metadata for file {file_path}: {e}")
        return None




def extract_classes_and_functions(content: str) -> Tuple[List[str], List[str]]:
    classes = []  # Placeholder for extracted classes
    functions = []  # Placeholder for extracted functions

    # Regular expression pattern to match function definitions
    function_pattern = re.compile(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")

    # Iterate through each line to identify classes and functions
    for line in content.split('\n'):
        line = line.strip()  # Remove leading and trailing whitespaces
        if line.startswith('def '):
            match = function_pattern.match(line)
            if match:
                function_name = match.group(1)  # Extract function name
                print("Found function:", function_name)  # Debugging print statement
                functions.append(function_name)

    return classes, functions

# def print_functions_horizontally(functions: List[str]):
#     """
#     Prints the list of functions horizontally, separated by commas.
#     """
#     for i, func in enumerate(functions):
#         if i < len(functions) - 1:
#             print(func, end=", ")
#         else:
#             print(func)


def search_files(query):
    results = collection.query(query_texts=[query])
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    found_items = []
    for document, metadata in zip(documents, metadatas):
        file_chunk = FileChunk(content=document, metadata=metadata)
        file_path = file_chunk.metadata.get('file_path', 'Unknown')
        classes = file_chunk.metadata.get('classes', [])
        functions = file_chunk.metadata.get('functions', [])
        found_items.append({"file_path": file_path, "classes": classes, "functions": functions})
        print("Found file:", file_path)
        print("Classes:", classes)
        print("Functions:")
        print(functions)  # Print functions horizontally
    return found_items


# Rest of your code remains unchanged
class PythonFileChunk(FileChunk):
    def __init__(self, content, metadata=None, classes=None):
        super().__init__(content, metadata)
        self.classes = classes or []

def clone_and_process_repository(repo_url, repo_path):
    if not os.path.exists(repo_path):
        # Clone the repository if it's not already cloned
        Repo.clone_from(repo_url, repo_path)
        os.chdir(repo_path)  # Change current directory to the cloned repository
    process_repository(repo_url, repo_path)  # Pass repo_url and repo_path to the function

def process_repository(repo_url, repo_path):
    for root, dirs, files in os.walk(repo_path):
        if '.git' in dirs:
            dirs.remove('.git')  # Skip the .git directory
        for file_name in files:
            if file_name == '.gitignore':  # Skip .gitignore file
                continue
            file_path = os.path.join(root, file_name)
            file_chunk = extract_file_chunks(file_path)
            if file_chunk:
                collection.add(documents=[file_chunk.content], ids=[file_chunk.uuid], metadatas=[file_chunk.metadata]) 

# Example usage:
repo_url = "https://github.com/renjialan/final_project_python"
repo_path = "/Users/oliveren/Documents/projects/repo_name"
clone_and_process_repository(repo_url, repo_path)

# Example search:
search_query = "migration"
found_classes = search_files(search_query)
for found_class in found_classes:
    file_path = found_class['file_path']
    classes = found_class['classes']
    functions = found_class['functions']
    # Process each found class and its associated metadata
    print(f"Classes found in '{file_path}': {classes}")
