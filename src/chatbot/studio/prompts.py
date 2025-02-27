from backend.Tools.services.sample_service import *
from backend.Tools.services.multiSample_metadata_service import *
from backend.Tools.services.module_to_json import functions_to_json
from langchain_core.messages import SystemMessage
from src.chatbot.studio.models import ConversationState


TOOLSET1 = [get_sample_name, retrieve_sample_info, fetch_protocol, fetchChildren, fetch_all_descendants, add_links]
TOOLSET2 = [get_metadata_by_uids, get_uids_by_terms_and_field]


SYSTEM_MESSAGE = (
    "You are a helpful assistant tasked with answering user questions about a data management platform called NExtSEEK."
)

INITIAL_STATE: ConversationState = {
    "messages": [SystemMessage(content=SYSTEM_MESSAGE, name="system")]
}

WORK_GROUP_A = [
    {"agent": "basic_sample_info_retriever",
    "role": "Retrieves basic metadata for a single sample",
    "toolbox": functions_to_json(TOOLSET1)
},
    {
        "agent": "multi_sample_info_retriever",
        "role": "Retrieves metadata for multiple samples",
        "toolbox": functions_to_json(TOOLSET2)
    },
    {
        "agent": "responder",
        "role": "Validate and respond to the user's query",
        "toolbox": None#functions_to_json(TOOLSET2)
    }
]

WORK_GROUP_B = [
        {
            "agent": "data_summarizer",
            "role": '1.(optional) Summarize conversation and data if more than 10 elements in aggregatedMessages',
            "toolbox": None
        },
        {
            "agent": "response_formatter",
            "role": "2. Format the response for the user",
            "toolbox": None
        }
    ]

