from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import START, StateGraph, MessagesState, END
from langgraph.prebuilt import tools_condition, ToolNode
from typing import List
from typing_extensions import Annotated, TypedDict, Sequence, Literal
from langgraph.graph.message import add_messages
from langgraph.types import Command
from pydantic import BaseModel
from langgraph.checkpoint.sqlite import SqliteSaver
import sys
import os

from studio.prompts import (
    # MEMBERS,
    # OPTIONS,
    SYS_MSG_SUPERVISOR,
    SYS_MSG_TOOLSET_1,
    SYS_MSG_TOOLSET_2,
    SYS_MSG_TOOLSET_3,
    SYS_MSG_LINK_ADDER
)

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.services.sample_service import get_sample_name, fetch_protocol, retrieve_sample_info, fetchChildren, fetch_all_descendants, fetchAllMetadata, add_links

# import env variables
from dotenv import load_dotenv
load_dotenv()

# checkpoint
import sqlite3
# In memory
conn = sqlite3.connect(":memory:", check_same_thread = False)
memory = SqliteSaver(conn)

# Define router type for structured output

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal["link_retriever", "data_summarizer", "descendant_metadata_retriever", "basic_sample_info_retriever","FINISH"]


# Create supervisor node function
def supervisor_node(state: MessagesState) -> Command[Literal["link_retriever", "data_summarizer", "descendant_metadata_retriever", "basic_sample_info_retriever", "FINISH", '__end__']]:
    messages = [
        {"role": "system", "content": SYS_MSG_SUPERVISOR},
    ] + state["messages"]
    response = llm.with_structured_output(Router).invoke(messages)
    goto = response["next"]
    print(f"Next Worker: {goto}")
    if goto ==  "FINISH":
        goto = END
    return Command(goto=goto)

########################################################
# Create agents
########################################################

class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]

def create_agent(llm, tools, msg):
    llm_with_tools = llm.bind_tools(tools)
    def chatbot(state: AgentState):
        return {"messages": [llm_with_tools.invoke(state["messages"] + [{"role": "system", "content": msg}])]}

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("agent", chatbot)

    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges(
        "agent",
        tools_condition,
    )
    graph_builder.add_edge("tools", "agent")
    graph_builder.set_entry_point("agent")
    return graph_builder.compile()

def create_worker(llm, tools, msg):
    llm_with_tools = llm.bind_tools(tools)
    def chatbot(state: AgentState):
        return {"messages": [llm_with_tools.invoke(state["messages"] + [{"role": "system", "content": msg}])]}

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("agent", chatbot)

    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_edge("agent", "tools")
    graph_builder.add_edge("tools", "agent")
    graph_builder.set_entry_point("agent")
    return graph_builder.compile()


########################################################
# Tools
########################################################

class SummarizedOutput(BaseModel):
    summary: str
    metadata: dict

def summarize_sample_info(sample_uid: str) -> SummarizedOutput:
   """LLM call to summarize sample information

   Args:
      sample_uid (str): sample UID that will be used to retrieve sample information from the database

   Returns:
      (SummarizedOutput): summary of sample information
   """
   try:
       llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
       sample_metadata = retrieve_sample_info(sample_uid)
       if not sample_metadata:
           raise ValueError("No sample metadata found.")
       prompt = (
           "Please provide a concise and clear summary in a few sentences based solely on the data provided "
           f"in the following dictionary: {sample_metadata[0]}. Avoid repeating the data verbatim and do not "
           "introduce additional information. If any information is unclear, feel free to ask the user for "
           "clarification. If the requested information cannot be retrieved, respond with: "
           "'I'm sorry, I couldn't find the information you're looking for.'"
       )
       messages = [{"role": "user", "content": prompt}]
       result = llm.with_structured_output(SummarizedOutput).invoke(messages)
       return result
   except Exception as e:
       return f"An error occurred while summarizing sample information: {str(e)}"

def summarize_all_metadata_info(sample_uid: str, filter: List[str] = None) -> SummarizedOutput:
   """LLM call to summarize metadata information for all descendants of a sample

   Args:
      sample_uid (str): sample UID that will be used to retrieve metadata information from the database for all descendants of the sample
      filter (List[str], optional): list of uid patterns to filter the metadata information by to retrieve only the metadata information for the descendants that match the patterns
   
   Returns:
      (SummarizedOutput): summary of metadata information
   """
   try:
       llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
       all_metadata = fetchAllMetadata(sample_uid, filter)
       if not all_metadata:
           raise ValueError("No metadata found for the given sample UID.")
       prompt = (
           "Please provide a concise and clear summary in a few sentences based solely on the data provided "
           f"in the following dictionary: {all_metadata}. Avoid repeating the data verbatim and do not "
           "introduce additional information. If any information is unclear, feel free to ask the user for "
           "clarification. If the requested information cannot be retrieved, respond with: "
           "'I'm sorry, I couldn't find the information you're looking for.'"
       )
       messages = [{"role": "user", "content": prompt}]
       result = llm.with_structured_output(SummarizedOutput).invoke(messages)
       return result
   except Exception as e:
       return f"An error occurred while summarizing metadata information: {str(e)}"


toolset1 = [get_sample_name, retrieve_sample_info, fetch_protocol]

toolset2 = [fetchChildren, fetch_all_descendants, fetchAllMetadata]

toolset3 = [summarize_sample_info, summarize_all_metadata_info]

toolset4 = [add_links]

########################################################
# LLMs with bound tools
########################################################

llm = ChatOpenAI(model="gpt-4o", temperature=0)


# Toolset 1: Retrieve sample name and information
# sys_msg for toolset 1


## build agents
basic_sample_info_retriever = create_agent(llm, toolset1, SYS_MSG_TOOLSET_1)
descendant_metadata_retriever = create_agent(llm, toolset2, SYS_MSG_TOOLSET_2)
data_summarizer = create_agent(llm, toolset3, SYS_MSG_TOOLSET_3)
link_retriever = create_agent(llm, toolset4, SYS_MSG_LINK_ADDER)

def basic_sample_info_retriever_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    result = basic_sample_info_retriever.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="basic_sample_info_retriever")
            ]
        },
        goto="supervisor",
    )

def descendant_metadata_retriever_node(state: MessagesState) -> Command[Literal["data_summarizer"]]:
    result = descendant_metadata_retriever.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="descendant_metadata_retriever")
            ]
        },
        goto="data_summarizer",
    )

def data_summarizer_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    result = data_summarizer.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="data_summarizer")
            ]
        },
        goto="supervisor",
    )

def link_retriever_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    result = link_retriever.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="link_retriever")
            ]
        },
        goto="supervisor",
    )

def finish_node(state: MessagesState) -> Command[Literal["__end__"]]:
    goto = END
    return Command(
        update = {"messages": state["messages"]},
        goto=goto
        )

builder = StateGraph(MessagesState)
builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor_node)
builder.add_node("basic_sample_info_retriever", basic_sample_info_retriever_node)
builder.add_node("descendant_metadata_retriever", descendant_metadata_retriever_node)
builder.add_node("data_summarizer", data_summarizer_node)
builder.add_node("link_retriever", link_retriever_node)
builder.add_node("FINISH", finish_node)
    

# Compile graph
graph = builder.compile(checkpointer=memory)
