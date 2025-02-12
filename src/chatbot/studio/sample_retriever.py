# src/chatbot/studio/sample_retriever.py

from langgraph.graph import START, StateGraph, END
from typing_extensions import Literal
from langgraph.types import Command
from pydantic import BaseModel, ConfigDict
from langgraph.checkpoint.sqlite import SqliteSaver
import os
from studio.models import ConversationState
from studio.supervisor import supervisor_node
from studio.responder import responder_node
from studio.response_formatter import response_formatter_node
from studio.validator import validator_node
from studio.data_summarizer import data_summarizer_node
from studio.basic_sample_info import basic_sample_info_retriever_node

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
    reply = state["messages"][-1].content
    print(reply)
    goto = END
    return Command(goto=goto)    

def sampleRetrieverGraph(state: ConversationState, memory = None):
    builder = StateGraph(ConversationState)
    builder.add_edge(START, "supervisor")
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("basic_sample_info_retriever", basic_sample_info_retriever_node)
    builder.add_node("data_summarizer", data_summarizer_node)
    builder.add_node("validator", validator_node)
    builder.add_node("responder", responder_node)
    builder.add_node("response_formatter", response_formatter_node)
    builder.add_node("FINISH", finish_node)
    # builder.add_edge("responder", "FINISH")
    # builder.add_edge("FINISH", END)

    # Compile graph
    if memory is not None:
        graph = builder.compile(checkpointer=memory)
    else:
        graph = builder.compile()
    return graph

# Example use without memory
# graph = sampleRetrieverGraph(state = ConversationState)
