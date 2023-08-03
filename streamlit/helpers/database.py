from langchain.vectorstores import DeepLake, VectorStore

# from logging import logger
from .models import get_embeddings


def get_dataset_path(data_source: str, credentials: dict) -> str:
    dataset_path = f"hub://{credentials['activeloop_org_name']}/{data_source}"
    return dataset_path


def get_vector_store(data_source: str, credentials: dict) -> VectorStore:
    # either load existing vector store or upload a new one to the hub
    embeddings = get_embeddings()
    dataset_path = get_dataset_path(data_source, credentials)
    # logger.info(f"Dataset '{dataset_path}' exists -> loading")
    vector_store = DeepLake(
        dataset_path=dataset_path,
        read_only=True,
        embedding_function=embeddings,
        token=credentials["activeloop_token"],
    )
    # logger.info(f"Vector Store {dataset_path} loaded!")
    return vector_store
