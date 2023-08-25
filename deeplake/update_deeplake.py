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

from helpers.class_scrape import get_cs40_docs
from helpers.piazza_scrape import scrape_piazza
from helpers.deeplake_utils import (
    pull_deeplake_dataset,
    pull_docs_from_db,
    get_embeddings
)
from helpers.constants import (
    VECTOR_STORE_PATH,
    ACTIVELOOP_TOKEN,
    TEXT_FILTER
)

SPLITTER = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=1000,
        )

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

def update_vector_database():
    # Download content from cs40 website, 
    source_dictionary = get_cs40_docs()

    print("Load and split local documents & vectordb documents")
    # if local_docs doesn't become a list of documents, shouldn't this throw an error?
    local_documents:T.List[Document] = (load_pdfs("deeplake/data/pdf") + 
                        load_docs("deeplake/data/txt", filter=TEXT_FILTER, split=True),
                        load_docs("piazzadocs", TEXT_FILTER))
    
    for doc in local_documents:
        source_dictionary[doc.metadata]

    vector_docs:T.List[T.Dict[str, int]] = pull_docs_from_db()
    
    print("Split the metadata from page content in order to create sets.")
    local_contents_set = set(document.page_content for document in local_documents)
    vector_contents_set = set(document['text'] for document in vector_docs)
    
    print("Create set of documents that are in vectordb, but not stored 'locally'")
    old_docs:set = vector_contents_set - local_contents_set

    print("Find the indices of the documents in old_docs")
    filtered_vector_docs = [doc for doc in vector_docs if doc['text'] in old_docs]
    indices_to_be_deleted = []
    for dict in filtered_vector_docs:
        indices_to_be_deleted.append(dict["index"])

    print("Reverse the list so that we delete from largest index to smallest index")
    indices_to_be_deleted.sort(reverse=True)

    print("Create connection to dataset and delete documents that aren't wanted :(")
    ds = pull_deeplake_dataset()
    # TODO: Write to a file which ones are being deleted?
    for index in indices_to_be_deleted: 
        print("deleting doc")
        ds.text.pop(index)
        ds.embedding.pop(index)
        ds.metadata.pop(index)
        ds.id.pop(index)
    
    print("Create a set of new docs, those that'll be added to the vector db")
    new_docs:set = local_contents_set - vector_contents_set
    restored_list = [doc for doc in local_documents if doc.page_content in new_docs]

    print("Writing to 'stuff.txt' contents of files being uploaded")
    with open("data/stuff.txt", "w") as file:
        for document in restored_list:
            file.write(document.page_content)
            file.write("==END==\n")
    
    if (len(restored_list) != 0):
        DeepLake.from_documents(
            restored_list,
            embedding=get_embeddings(),
            dataset_path=VECTOR_STORE_PATH,
            token=ACTIVELOOP_TOKEN,
        )
    