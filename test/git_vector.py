import os
from git import Repo
import chromadb
from chromadb.utils import embedding_functions
import uuid

# Configuration
save_path = "./database/"
collection_name = "repo_embeddings"
sentence_transformer_embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name='BAAI/bge-small-en-v1.5')

# Ensure the database directory exists
if not os.path.exists(save_path):
    os.makedirs(save_path)

# ChromaDB client and collection
chroma_client = chromadb.PersistentClient(path=save_path)
collection = chroma_client.get_or_create_collection(name=collection_name, embedding_function=sentence_transformer_embedding_function)

def embed_files(repo_path):
    for root, _, files in os.walk(repo_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, "rb") as file:
                content = file.read()
                # Extract embeddings from the content
                embeddings = sentence_transformer_embedding_function.extract([content])
            # Store the embedding in ChromaDB
            collection.add(documents=[embeddings[0]], ids=[str(uuid.uuid4())])

def process_repository(repo_url):
    # Path to the local directory where the repository will be cloned
    clone_path = "./cloned_repo"

    # Clone the repository if it doesn't exist
    if not os.path.exists(clone_path):
        Repo.clone_from(repo_url, clone_path)

    # Convert files into embeddings
    embed_files(clone_path)

# Example usage:
repo_url = "https://github.com/renjialan/final_project_python"
process_repository(repo_url)

