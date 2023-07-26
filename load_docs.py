# from deeplake.core.vectorstore.deeplake_vectorstore import VectorStore
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import DeepLake
# import openai
# import os
import streamlit as st
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings


EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
SOURCE_DOCUMENTS_DIR = "data/Piazza_docs"
SOURCE_DOCUMENTS_FILTER = "**/*.txt"


def load_docs(directory, filter, split=False):
    loader = DirectoryLoader(f"./{directory}", glob=filter)
    # TODO: I don't think that there is a need to split the Piazza documents
    #   because they're all split up already!
    #   however, this will be necessary for loading in the textbook and such
    print(f"Loading {directory} directory for any {filter}")
    data = loader.load()
    if split:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=1000,
        )
        print(f"Splitting {len(data)} documents")
        r_docs = splitter.split_documents(data)
        return r_docs
    
    print(f"Created {len(data)} documents from {directory}")
    return data

chunked_text = load_docs(SOURCE_DOCUMENTS_DIR, SOURCE_DOCUMENTS_FILTER)

vector_store_path = "hub://69-69/text_embeddings" 

# Will download the model the first time it runs (slowly)
embedding_function = SentenceTransformerEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    cache_folder="data/",
)

print("Complete")

vector_store = DeepLake.from_documents(
            chunked_text,
            embedding_function,
            dataset_path=vector_store_path,
            token="eyJhbGciOiJIUzUxMiIsImlhdCI6MTY5MDIyMDA1NSwiZXhwIjoxNjkwODI0ODM5fQ.eyJpZCI6ImpiZWFzdG1hbiJ9.AmMWPDqYBtHy_wBvj7WjfiX-iBGv4BPiJDVLZBhDEWLrQX3L4NkSRJebgVDm-JsIDevLBTa7N9hFc4yGfFOmvA",
        )