import deeplake
from langchain.vectorstores import DeepLake, VectorStore

from datachad.constants import DATA_PATH
from datachad.logging import logger
from datachad.models import MODES, get_embeddings


def get_dataset_path(data_source: str, options: dict, credentials: dict) -> str:
    # dataset_name = clean_string_for_storing(data_source)
    # we need to differntiate between differently chunked datasets
    # dataset_name += f"-{options['chunk_size']}-{options['chunk_overlap']}-{options['model'].embedding}"
    # if options["mode"] == MODES.LOCAL:
    #     dataset_path = str(DATA_PATH / dataset_name)
    # else:
    dataset_path = f"hub://{credentials['activeloop_org_name']}/{data_source}"
    return dataset_path


def get_vector_store(data_source: str, options: dict, credentials: dict) -> VectorStore:
    # either load existing vector store or upload a new one to the hub
    embeddings = get_embeddings(options, credentials)
    dataset_path = get_dataset_path(data_source, options, credentials)
    logger.info(f"Dataset '{dataset_path}' exists -> loading")
    vector_store = DeepLake(
        dataset_path=dataset_path,
        read_only=True,
        embedding_function=embeddings,
        token=credentials["activeloop_token"],
    )
    logger.info(f"Vector Store {dataset_path} loaded!")
    return vector_store
