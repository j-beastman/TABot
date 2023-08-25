import typing as T
import os

import deeplake
from deeplake.core.dataset import Dataset
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import DeepLake


from constants import (
    VECTOR_STORE_PATH,
    EMBEDDING_MODEL_NAME,
    ACTIVELOOP_ORG_NAME,
    ACTIVELOOP_TOKEN
)

def get_embeddings():
    return SentenceTransformerEmbeddings(
        model_name=EMBEDDING_MODEL_NAME, cache_folder="cache/"
    )

def pull_deeplake_dataset() -> Dataset:
    # either load existing vector store or upload a new one to the hub
    ds = deeplake.load(path=VECTOR_STORE_PATH, token=ACTIVELOOP_TOKEN, read_only=False)
    return ds

def pull_docs_from_db():
    try:
        ds = pull_deeplake_dataset()
        text = []
        index = []
        for i, sample in enumerate(ds.max_view):
            text.append(ds.text[i].data()["value"])
            index.append(i)
        # The indices are listed from smallest to largest
        return [{'text': key, 'index': index} for key, index in zip(text, index)]
    except AttributeError:
        print("Dataset was empty")

def create_empty_db(new_vector_store_name):
    def load_misc(directory):
        loader = DirectoryLoader(f"./{directory}")

        print(f"Loading {directory} directory for any {filter}")
        data = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=10,
        )
        r_docs = splitter.split_documents(data)
        return r_docs
    vectorstore_name =  f"hub://{ACTIVELOOP_ORG_NAME}/{new_vector_store_name}"
    chunked_text = load_misc("data/snippets")
    embedding_function = get_embeddings()
    DeepLake.from_documents(
        chunked_text,
        embedding_function,
        dataset_path=vectorstore_name,
        token=ACTIVELOOP_TOKEN,
    )

    