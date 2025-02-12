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
    "toolbox": ["get_sample_name", "retrieve_sample_info", "fetch_protocol", "fetchChildren", "fetch_all_descendants", "add_links"],
    "tools_description": {
                "get_sample_name": "Get the name of the sample.",
                "retrieve_sample_info": "Retrieve the sample information for a given sample UID.",
                "fetch_protocol": "Fetch the protocol for a given sample UID.",
                "fetchChildren": "Fetch the children of a given sample UID.",
                "fetch_all_descendants": "Fetch all descendants of a given sample UID.",
                "add_links": "Add links to the sample information.",
            }},
    {
        "agent": "responder",
        "role": "Validate and respond to the user's query",
        "toolbox": ["data_summarizer", "response_formatter", "validator", "FINISH"],
        "tools_description": {
            "data_summarizer": "Summarize the data if response is longer than 100 words",
            "response_formatter": "Format the response if data_summarizer is used",
            "validator": "Validate the response",
            "FINISH": "Finish the conversation"
        }
    }
]

WORK_GROUP_B = [
        {
            "agent": "data_summarizer",
            "role": "1.(optional) Summarize the data if response is longer than 100 words",
            "toolbox": None,
            "tools_description": None
        },
        {
            "agent": "response_formatter",
            "role": "2. Format the response for the user",
            "toolbox": None,
            "tools_description": None
        },
        {
            "agent": "validator",
            "role": "3. Validate the response",
            "toolbox": None,
            "tools_description": None
        },
        {
            "agent": "FINISH",
            "role": "4.Finish the conversation",
            "toolbox": None,
            "tools_description": None
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
