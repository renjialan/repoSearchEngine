import os
import shutil
import chromadb
import uuid


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


def search_files(query):
    results = collection.query(query_texts=[query])
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    found_files = []
    for document, metadata in zip(documents, metadatas):
        file_chunk = FileChunk(content=document, metadata=metadata)
        file_path = file_chunk.metadata.get('file_path', 'Unknown')
        found_files.append(file_path)
        print("Found file:", file_path)
    return found_files



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
            return FileChunk(content=content, metadata={"file_path": os.path.basename(file_path)})  # Return a FileChunk object
    except UnicodeDecodeError:
        print(f"Skipping non-text file: {file_path}")
        return None

    
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
search_files(search_query)

found_files = search_files(search_query)
print("Files found:", found_files)