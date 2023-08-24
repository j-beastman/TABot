import os
import streamlit as st

from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import DeepLake
from langchain.document_loaders import PyPDFLoader


CLASS = "cs40"
VECTOR_STORE_PATH = f"hub://69-69/{CLASS}"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
SOURCE_DOCUMENTS_DIR = f"data/{CLASS}/Piazza_docs"
SOURCE_DOCUMENTS_FILTER = "**/*.txt"
ACTIVELOOP_TOKEN = "eyJhbGciOiJIUzUxMiIsImlhdCI6MTY5MjkxMzI3MCwiZXhwIjoxNjk4ODc0ODU5fQ.eyJpZCI6ImpiZWFzdG1hbiJ9.lL5vN_cuJM5J0BIYwEt0-K3dbBPcm6IE2PoZzlZp8JhSfd2EHmOkcRVWW-kgdgCe9t1gj2m6dw3fWZEZavfFTw"

SPLITTER = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=1000,
        )
print("dont do this until we have a way to compare local and what's on deeplake")
exit()

def load_docs(directory, filter, split=False):
    loader = DirectoryLoader(f"./{directory}", glob=filter)
    # TODO: I don't think that there is a need to split the Piazza documents
    #   because they're all split up already!
    #   however, this will be necessary for loading in the textbook and such
    print(f"Loading {directory} directory for any {filter}")
    data = loader.load()
    if split:
        print(f"Splitting {len(data)} documents")
        r_docs = SPLITTER.split_documents(data)
        return r_docs

    print(f"Created {len(data)} documents from {directory}")
    return data

def load_pdfs(directory):
    file_names = os.listdir(directory)
    data = []
    for file in file_names:
        loader = PyPDFLoader(f"{directory}/{file}")
        pages = loader.load_and_split(text_splitter=SPLITTER)
        data += pages
    return data

# Need to implement adding Piazza Docs too...
docs = (load_pdfs("deeplake/data/pdf") + 
        load_docs("deeplake/data/txt", filter=SOURCE_DOCUMENTS_FILTER, split=True))

# Will download the model the first time it runs (slowly)
# Apparently using embedding function is deprecated?
embedding_function = SentenceTransformerEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    cache_folder="cache/",
)

# This will automatically create a new Deep Lake dataset if the
# dataset_path does not exist
DeepLake.from_documents(
    docs,
    embedding_function,
    dataset_path=VECTOR_STORE_PATH,
    token=ACTIVELOOP_TOKEN,
)
