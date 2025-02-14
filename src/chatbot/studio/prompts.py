from backend.Tools.services.sample_service import *
# from src.chatbot.studio.response_formatter import response_formatter_node
# from src.chatbot.studio.validator import validator_node
# from src.chatbot.studio.data_summarizer import data_summarizer_node
from backend.Tools.services.module_to_json import functions_to_json


TOOLSET1 = [get_sample_name, retrieve_sample_info, fetch_protocol, fetchChildren, fetch_all_descendants, add_links]
# TOOLSET2 = [data_summarizer_node, response_formatter_node, validator_node]


# Define each prompt as a separate constant

# List of members
MEMBERS = ["link_retriever", "data_summarizer", "descendant_metadata_retriever", "basic_sample_info_retriever"]

# Options including members and 'FINISH'
OPTIONS = MEMBERS + ["responder"]

WORKERS = ["validator", "data_summarizer", "FINISH"]

SYSTEM_MESSAGE = (
    "You are a helpful assistant tasked with answering user questions about a data management platform called NExtSEEK."
)

WORK_GROUP_A = [
    {"agent": "basic_sample_info_retriever",
    "role": "Retrieve basic metadata for the sample",
    "toolbox": functions_to_json(TOOLSET1)
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
            "role": '1.(optional) Summarize conversation and data if more than 8 elements in aggregatedMessages',
            "toolbox": None
        },
        {
            "agent": "response_formatter",
            "role": "2. Format the response for the user",
            "toolbox": None
        },
        {
            "agent": "validator",
            "role": "3. Validate the response",
            "toolbox": None
        },
        {
            "agent": "FINISH",
            "role": "4.Finish the conversation",
            "toolbox": None
        }
    ]

SYS_MSG_TOOLSET_3 = (
    "You are a helpful assistant tasked with summarizing information about samples and their associated metadata."
    "You will be given a sample UID and you will use the tools provided to retrieve the relevant information. Depending "
    "on the user query, you will choose to either summarize the sample information or the metadata the"
    "descendants of that sample. For instance, if the user asks for only the tissue descendants of a sample, you should "
    "use the filter parameter in the summarize_all_metadata_info tool to retrieve only the metadata information for the "
    "descendants that match the tissue pattern ('TIS'). If the user only asks for the sample information, you should use the "
    "summarize_sample_info tool."
    "Your output should be in the following format: "
    "Summary: [summary of retrieved information]"
)
