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

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.services.sample_service import get_sample_name, fetch_protocol, retrieve_sample_info, fetchChildren, fetch_all_descendants, fetchAllMetadata, add_links

# import env variables
from dotenv import load_dotenv
load_dotenv()

# checkpoint
memory = SqliteSaver.from_conn_string(":memory:")

members = ["link_retriever", "data_summarizer", "descendant_metadata_retriever", "basic_sample_info_retriever"]
options = members + ["FINISH"]

# System messages
sys_msg = "You are a supervisor tasked with managing a conversation between the"
f"following workers: {members}."
"Given the following user request,"
" respond with the worker to act next. Each worker will perform a"
" task and respond with their results and status. "
" When finished with all tasks, respond with FINISH."
# Define router type for structured output
class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal["link_retriever", "data_summarizer", "descendant_metadata_retriever", "basic_sample_info_retriever","FINISH"]
    # messages: Annotated[Sequence[BaseMessage], add_messages]


# Create supervisor node function
def supervisor_node(state: MessagesState) -> Command[Literal["link_retriever", "data_summarizer", "descendant_metadata_retriever", "basic_sample_info_retriever", "FINISH", "_end_"]]:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    messages = [
        {"role": "system", "content": sys_msg},
    ] + state["messages"]
    response = llm.with_structured_output(Router).invoke(messages)
    goto = response["next"]
    print(f"Next Worker: {goto}")
    if goto == "FINISH":
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
msg1 = "You are a helpful assistant tasked with retrieving and summarizing information about samples from a database that stores metadata about research samples and data according to FAIR data principles and NIH standards. You will be given a sample UID and you will use the tools provided to retrieve the relevant information. Depending on the user query, you will choose to either retrieve the sample name or the sample information. If you are asked for the sample name, use the retrieve_sample_name tool. If you are asked for information about a sample, use the retrieve_sample_info tool. You should use the answer given by the tools utilized unless the query returns an error or empty list. For instance, when asked for the name of a sample, you should provide the name given by the database after running the appropriate query unless the query returns an error or empty list."


# sys_msg for toolset 2
msg2 = "You are a helpful assistant tasked with summarizing information about children, descendants, and associated metadata for a given sample from a database that stores metadata about research samples and data according to FAIR data principles and NIH standards. You will be given a sample UID and you will use the tools provided to retrieve the relevant information. Depending on the user query, you will choose to either retrieve the children of that sample, all descendants of the sample, and/or metadata about the descendants of that sample. You should use the answer given by the database unless the query returns an error or empty list."


# sys_msg for toolset 3
msg3 = "You are a helpful assistant tasked with summarizing information about samples and their associated metadata from a database that stores metadata about research samples and data according to FAIR data principles and NIH standards. You will be given a sample UID and you will use the tools provided to retrieve the relevant information. Depending on the user query, you will choose to either summarize the sample information or the metadata for all or a subset of descendants of that sample. For instance, if the user asks for only the tissue descendants of a sample, you should use the filter parameter in the summarize_all_metadata_info tool to retrieve only the metadata information for the descendants that match the tissue pattern. If the user only asks for the sample information, you should use the summarize_sample_info tool. You should use the answer given by the database unless the query returns an error or empty list."


msg4 = "You are a helpful assistant tasked with adding links to sample and protocol uids from a database." 
"You will be given a sample UID and you will use the tools provided to create the links based on the user query." 
"You will add the links to the message received from the previous worker and return the updated message."

## build agents
basic_sample_info_retriever = create_agent(llm, toolset1, msg1)
descendant_metadata_retriever = create_agent(llm, toolset2, msg2)
data_summarizer = create_agent(llm, toolset3, msg3)
link_retriever = create_agent(llm, toolset4, msg4)

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

def descendant_metadata_retriever_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    result = descendant_metadata_retriever.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="descendant_metadata_retriever")
            ]
        },
        goto="supervisor",
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

builder = StateGraph(MessagesState)
builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor_node)
builder.add_node("basic_sample_info_retriever", basic_sample_info_retriever_node)
builder.add_node("descendant_metadata_retriever", descendant_metadata_retriever_node)
builder.add_node("data_summarizer", data_summarizer_node)
builder.add_node("link_retriever", link_retriever_node)
# builder.add_edge("supervisor", END)
# builder.add_edge("link_retriever", END)
    

# Compile graph
graph = builder.compile(checkpointer=memory)
