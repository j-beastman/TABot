# from deeplake.core.vectorstore.deeplake_vectorstore import VectorStore
# import openai
import typing as T
import re
from langchain.document_loaders import DirectoryLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import DeepLake
from langchain.document_loaders import DataFrameLoader
from github import Github, Auth
from pull_from_snowflake import pull_data_from_snowflake
from github.GithubException import RateLimitExceededException
import time

from constants import (
    ACTIVELOOP_TOKEN,
    GIT_TOKEN,
    VECTOR_STORE_PATH, 
    DR_TRUST_DIR, 
    DR_TRUST_FILTER,
)

REPOS = [
    "datarobot-docs",
    "public_api_client",
    # "datarobot-predict" <-- this throws errors (from api_ref.md)
]

from deeplake_utils import (
    get_embeddings,
    pull_deeplake_dataset,
    pull_docs_from_db,
)

EMBEDDING = get_embeddings()

# Store RFPs and Misc
def load_all_rfps() -> T.List[Document]:
    df = pull_data_from_snowflake()
    df['Content'] = df['QUESTION'] + ' ' + df['RESPONSE']
    df.drop(['QUESTION', 'RESPONSE'], axis=1, inplace=True)
    loader = DataFrameLoader(df, page_content_column="Content")
    rfp_docs = loader.load()
    return rfp_docs

# All RFPs are stored in the Snowflake DB
def load_misc(directory, filter, split=False) -> T.List[Document]:
    loader = DirectoryLoader(f"./{directory}", glob=filter)
    print(f"Loading {directory} directory for any {filter}")
    data = loader.load()
    if split:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=500,
        )
        print(f"Splitting {len(data)} documents")
        r_docs = splitter.split_documents(data)
        print(type(r_docs), "MISC DOCS TYPE")
        return r_docs

    print(f"Created {len(data)} documents from {directory}")
    
    return data

def update_vector_database():
    print("Load and split local documents & vectordb documents")
    # if local_docs doesn't become a list of documents, shouldn't this throw an error?
    local_documents:T.List[Document] = (load_all_rfps() + 
                                        load_misc(DR_TRUST_DIR, DR_TRUST_FILTER, split=True) + 
                                        load_github_repos())
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
    
    
if __name__ == "__main__":
    update_vector_database()