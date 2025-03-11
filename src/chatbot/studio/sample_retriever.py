# src/chatbot/studio/sample_retriever.py

from langgraph.graph import START, StateGraph, END
from typing_extensions import Literal
from langgraph.types import Command
# from pydantic import BaseModel, ConfigDict
# from langgraph.checkpoint.sqlite import SqliteSaver
import os
import sys
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
print(project_root)
sys.path.append(project_root)

from src.chatbot.studio.models import ConversationState
from src.chatbot.studio.supervisor import supervisor_node
from src.chatbot.studio.responder import responder_node
from src.chatbot.studio.response_formatter import response_formatter_node
from src.chatbot.studio.validator import validator_node
from src.chatbot.studio.data_summarizer import data_summarizer_node
from src.chatbot.studio.basic_sample_info import basic_sample_info_retriever_node
from src.chatbot.studio.schema_retriever import schema_retriever_node
from src.chatbot.studio.advanced_sample_retriever import multi_sample_info_retriever_node
from src.chatbot.studio.conversationalist import conversationalist_node
from src.chatbot.studio.query_parser import query_parser_node
from src.chatbot.studio.prompts import INITIAL_STATE
from src.chatbot.studio.update_records import archivist_node
# import env variables
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# In memory
# conn = sqlite3.connect(":memory:", check_same_thread = False)
# memory = AsyncSqliteSaver(conn)

def finish_node(state: ConversationState) -> Command[Literal["__end__"]]:
    """
    This node is used to finish the conversation.
    """
    reply = state.messages[-1].content
    print(reply)
    goto = END
    return Command(goto=goto)    

def sampleRetrieverGraph(state: ConversationState = INITIAL_STATE, memory = None):
    builder = StateGraph(ConversationState)
    builder.add_edge(START, "conversationalist")
    builder.add_node("conversationalist", conversationalist_node)
    builder.add_node("query_parser", query_parser_node)
    builder.add_node("schema_retriever", schema_retriever_node)
    builder.add_node("archivist", archivist_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("basic_sample_info_retriever", basic_sample_info_retriever_node)
    builder.add_node("data_summarizer", data_summarizer_node)
    builder.add_node("validator", validator_node)
    builder.add_node("responder", responder_node)
    builder.add_node("response_formatter", response_formatter_node)
    builder.add_node("multi_sample_info_retriever", multi_sample_info_retriever_node)
    builder.add_node("FINISH", finish_node)

    # Compile graph
    if memory is not None:
        graph = builder.compile(checkpointer=memory)
    else:
        graph = builder.compile()
    return graph

# Example use without memory
GRAPH = sampleRetrieverGraph()
