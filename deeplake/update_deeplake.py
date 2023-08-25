import typing as T
import os

from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import DeepLake
from langchain.document_loaders import PyPDFLoader
from langchain.docstore.document import Document

from helpers.scrapers import get_cs40_docs

# CLASSES = {
#         "cs40": {
#             "id": "lck5atzpw5k69m",
#         }
#     }

CLASS = "cs40"
VECTOR_STORE_PATH = f"hub://69-69/{CLASS}"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
SOURCE_DOCUMENTS_DIR = f"data/{CLASS}/Piazza_docs"
SOURCE_DOCUMENTS_FILTER = "**/*.txt"
ACTIVELOOP_TOKEN = "eyJhbGciOiJIUzUxMiIsImlhdCI6MTY5MjkxMzI3MCwiZXhwIjoxNjk4ODc0ODU5fQ.eyJpZCI6ImpiZWFzdG1hbiJ9.lL5vN_cuJM5J0BIYwEt0-K3dbBPcm6IE2PoZzlZp8JhSfd2EHmOkcRVWW-kgdgCe9t1gj2m6dw3fWZEZavfFTw"  # noqa: E501

SPLITTER = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=1000,
        )
print("dont do this until we have a way to compare local and what's on deeplake")
# exit()

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

# Download content from cs40 website, 
source_dictionary = get_cs40_docs()

# Need to implement adding Piazza Docs too...
docs = (load_pdfs("deeplake/data/pdf") + 
        load_docs("deeplake/data/txt", filter=SOURCE_DOCUMENTS_FILTER, split=True))

for doc in docs:
    source_dictionary[doc.metadata]

# # Will download the model the first time it runs (slowly)
# # Apparently using embedding function is deprecated?
# embedding_function = SentenceTransformerEmbeddings(
#     model_name=EMBEDDING_MODEL_NAME,
#     cache_folder="cache/",
# )

# # This will automatically create a new Deep Lake dataset if the
# # dataset_path does not exist
# DeepLake.from_documents(
#     docs,
#     embedding_function,
#     dataset_path=VECTOR_STORE_PATH,
#     token=ACTIVELOOP_TOKEN,
# )

def update_vector_database():
    print("Load and split local documents & vectordb documents")
    # if local_docs doesn't become a list of documents, shouldn't this throw an error?
    local_documents:T.List[Document] = (load_pdfs("deeplake/data/pdf") + 
                            load_docs("deeplake/data/txt", filter=SOURCE_DOCUMENTS_FILTER, split=True))
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
    for index in indices_to_be_deleted: # TODO: Write to a file which ones are being deleted?
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
            embedding=EMBEDDING,
            dataset_path=VECTOR_STORE_PATH,
            token=ACTIVELOOP_TOKEN,
        )
    