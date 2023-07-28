# from deeplake.core.vectorstore.deeplake_vectorstore import VectorStore
# import openai
# import os
import streamlit as st
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import DeepLake

CLASS = "cs40"
VECTOR_STORE_PATH = f"hub://69-69/{CLASS}"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
SOURCE_DOCUMENTS_DIR = f"data/{CLASS}/Piazza_docs"
SOURCE_DOCUMENTS_FILTER = "**/*.txt"
ACTIVELOOP_TOKEN = st.secrets["ACTIVELOOP_TOKEN"]


def combine_piazza_docs(directory, filter, split=False):
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


chunked_text = combine_piazza_docs(SOURCE_DOCUMENTS_DIR, SOURCE_DOCUMENTS_FILTER)

# Will download the model the first time it runs (slowly)
embedding_function = SentenceTransformerEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    cache_folder="cache/",
)

# This will automatically create a new Deep Lake dataset if the
# dataset_path does not exist
DeepLake.from_documents(
    chunked_text,
    embedding_function,
    dataset_path=VECTOR_STORE_PATH,
    token=ACTIVELOOP_TOKEN,
)
