import os
import chromadb
import uuid
from git import Repo
from typing import List
from lspclient import LanguageServer
from lspclient.requests import InitializeRequest, TextDocumentDocumentSymbolRequest
from lspclient.types import DocumentSymbolParams

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
            functions = extract_functions_with_lsp(content)  # Extract functions using LSP
            if functions:
                metadata["functions"] = functions  # Store extracted functions
            return FileChunk(content=content, metadata=metadata)
    except UnicodeDecodeError:
        print(f"Skipping non-text file: {file_path}")
        return None
    except Exception as e:
        print(f"Error extracting metadata for file {file_path}: {e}")
        return None

def extract_functions_with_lsp(content):
    # Connect to an LSP server (e.g., pyls)
    server = LanguageServer('pyls')
    initialize_request = InitializeRequest()
    server.send_request(initialize_request)

    # Send a request for document symbols
    document_symbol_request = TextDocumentDocumentSymbolRequest(
        params=DocumentSymbolParams(textDocument={'uri': 'file://' + content})  # Construct URI
    )
    response = server.send_request(document_symbol_request)

    # Extract function names from the response
    functions = []
    for symbol_info in response:
        if symbol_info.kind == 'Function':
            functions.append(symbol_info.name)
    return functions

def clone_and_process_repository(repo_url, repo_path):
    if not os.path.exists(repo_path):
        # Clone the repository if it's not already cloned
        Repo.clone_from(repo_url, repo_path)
    process_repository(repo_url, repo_path)  # Pass repo_url and repo_path to the function

def process_repository(repo_url, repo_path):
    for root, dirs, files in os.walk(repo_path):
        if '.git' in dirs:
            dirs.remove('.git')  # Skip the .git directory
        for file_name in files:
            if file_name.endswith('.py'):  # Process only Python files
                file_path = os.path.join(root, file_name)
                file_chunk = extract_file_chunks(file_path)
                if file_chunk:
                    collection.add(documents=[file_chunk.content], ids=[file_chunk.uuid], metadatas=[file_chunk.metadata])

# Example usage:
repo_url = "https://github.com/renjialan/final_project_python"
repo_path = "/Users/oliveren/Documents/projects/repo_name"
clone_and_process_repository(repo_url, repo_path)
