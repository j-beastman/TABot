from pathlib import Path
from langchain import PromptTemplate

PAGE_ICON = "👾"
APP_NAME = "TA Bot"
PROJECT_URL = "https://github.com/j-beastman/TABot"

K = 6
FETCH_K = 30
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 1000
TEMPERATURE = 0.7
MAX_TOKENS = 6000
MODEL_N_CTX = 1000
DISTANCE_METRIC = "cos"
MAXIMAL_MARGINAL_RELEVANCE = True

ENABLE_ADVANCED_OPTIONS = True
ENABLE_LOCAL_MODE = False

MODEL_PATH = Path.cwd() / "models"
GPT4ALL_BINARY = "ggml-gpt4all-j-v1.3-groovy.bin"

DATA_PATH = Path.cwd() / "data"
DEFAULT_DATA_SOURCE = "text_embeddings"

MODE_HELP = """
`OpenAI` uses the openai library to make API calls \n
"""

LOCAL_MODE_DISABLED_HELP = """
This is a demo hosted with limited resources. Local Mode is not enabled.\n
To use Local Mode deploy the app on your machine of choice with `ENABLE_LOCAL_MODE` set to `True`.
"""

AUTHENTICATION_HELP = f"""
Your credentials are only stored in your session state.\n
The keys are neither exposed nor made visible or stored permanently in any way.\n
Feel free to check out [the code base]({PROJECT_URL}) to validate how things work.
"""

USAGE_HELP = """
These are the accumulated OpenAI API usage metrics.\n
The app uses `gpt-3.5-turbo` for chat and `text-embedding-ada-002` for embeddings.\n
Learn more about OpenAI's pricing [here](https://openai.com/pricing#language-models)
"""

OPENAI_HELP = """
You can sign-up for OpenAI's API [here](https://openai.com/blog/openai-api).\n
Once you are logged in, you find the API keys [here](https://platform.openai.com/account/api-keys)
"""

ACTIVELOOP_HELP = """
You can create an ActiveLoops account (including 500GB of free database storage) [here](https://www.activeloop.ai/).\n
Once you are logged in, you find the API token [here](https://app.activeloop.ai/profile/gustavz/apitoken).\n
The organisation name is your username, or you can create new organisations
[here](https://app.activeloop.ai/organization/new/create)
"""

UPLOAD_HELP = """
You can upload a single or multiple files. With each upload, all files in the batch are embedded into a single
    vector store.\n
**Important**: If you upload new files after you already have uploaded files, a new vector store that includes all
    previously uploaded files is created.
This means for each combination of uploaded files, a new vector store is created.\n
To treat your new upload independently, you need to remove the previous uploads by clicking the `X`, right next to the
    uploaded file name.\n
**!!! All uploaded files are removed permanently from the app after the vector stores are created !!!**
"""

CHAT_HISTORY = [
    (
        "I want you to act as a Tufts University Ungraduate student who is "
        + "working as a Teaching Assistant for a computer science course. Your goal is to answer students' "
        + "questions so that they can perform better on their homeworks and exams. All of your answers "
        + "should be clear without being too verbose. They should also be in "
        + "passive voice and never refer to you. For example, you should not say "
        + "something like 'I don't know' or 'I found'. Your responses should also "
        + "never explicitly mention the context you are using to generate your answers.",
        "I will act as a Tufts University Ungraduate student who is "
        + "working as a Teaching Assistant for a computer science course.",
    )
]

BOOSTED_SEARCH_TEMPLATE = PromptTemplate(
    input_variables=[
        "user_query",
        "additional_search_prompts",
        "initial_search_results",
    ],
    template=(
        """
            USER QUERY: "{user_query}"

            SEARCH RESULTS: These are the results of searching for the user's query
            {initial_search_results}

            SYSTEM:
            Using the above SEARCH RESULTS and the most recent element of USER QUERY,
            write a numbered list of five new search queries to look up additional information
            relevant to answering the user's query in a vector database.
            
            For best results, queries should mimic the expected text content of the records
            to be retrieved, rather than being phrased like a traditional search engine query.
            Create two general searches relevant to the whole query,
            and three searches relevant to the three most important topics found in the
            SEARCH RESULTS.

            {additional_search_prompts}

            EXAMPLE ANSWER:
            1. <general search query 1>
            2. <general search query 2>
            3. <search query for one topic in the SEARCH RESULTS>
            4. <search query for another topic in the SEARCH RESULTS>
            5. <search query for a final topic in the SEARCH RESULTS>
            """
    ),
)
# Prompt to query each of the 5
BOOSTED_FINAL_OUTPUT_TEMPLATE = PromptTemplate(
    input_variables=[
        "context",
        "user_query",
        "additional_output_prompts",
    ],
    template=(
        """
            CONTEXT:
            {context}

            SYSTEM:
            - Do not guess or make up any information that is not
              provided in the above CONTEXT.
            - Ignore CONTEXT that is irrelevant to the provided PROMPT.

            {additional_output_prompts}

            PROMPT: {user_query}
            """
    ),
)