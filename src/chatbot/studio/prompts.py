import os, sys

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.services.sample_service import *
from backend.Tools.services.multiSample_metadata_service import *
from backend.Tools.services.update_metadata import *
# from backend.Tools.services.module_to_json import functions_to_json
from langchain_core.messages import SystemMessage
from src.chatbot.studio.models import ConversationState
import uuid
from datetime import datetime, timezone
from src.chatbot.studio.helpers import populate_toolbox, WorkerState


TOOLSET1 = [get_sample_name, retrieve_sample_info, fetch_protocol, fetchChildren, fetch_all_descendants, add_links]
TOOLSET2 = [get_metadata_by_uids, get_uids_by_terms_and_field]
TOOLSET3 = [update_metadata_pipeline, get_st_attributes]

CONFIG = {"recursion_limit": 20,"configurable": {"thread_id": "1"}}

SYSTEM_MESSAGE = (
    "You are a helpful assistant tasked with answering user questions about a data management platform called NExtSEEK." 
    "You also have the ability to update the metadata of the samples in the platform given a correctly formatted csv file." 
    "NEVER make up an answer. If you cannot answer the question, clearly state that you do not know the answer or that you do not have the tools necessary to answer the question."
)

INITIAL_STATE: ConversationState = ConversationState(
    messages=[SystemMessage(content=SYSTEM_MESSAGE, name="system")],
    version=1,
    session_id=str(uuid.uuid4()),
    timestamp=datetime.now(timezone.utc),
    last_worker="user"
)

WORK_GROUP_A = [
    WorkerState(agent="basic_sample_info_retriever",
    role="Retrieves basic metadata for a single sample",
    toolbox=populate_toolbox(TOOLSET1)),
    WorkerState(agent="multi_sample_info_retriever",
        role="Retrieves metadata for multiple samples",
        toolbox=populate_toolbox(TOOLSET2)),
    WorkerState(agent="archivist",
        role="Updates metadata for samples",
        toolbox=populate_toolbox(TOOLSET3)),
    WorkerState(agent="responder",
        role="Validate and respond to the user's query",
        toolbox=None)
]

WORK_GROUP_B = [
    WorkerState(agent="data_summarizer",
        role='1.(optional) Summarize conversation and data if more than 10 elements in aggregatedMessages',
        toolbox=None),
    WorkerState(agent="response_formatter",
        role="2. Format the response for the user",
        toolbox=None)
    ]

