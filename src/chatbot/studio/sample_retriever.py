from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import START, StateGraph, MessagesState, END
from langgraph.prebuilt import tools_condition, ToolNode
from typing import List
from typing_extensions import Annotated, TypedDict, Sequence, Literal
from langgraph.graph.message import add_messages
from langgraph.types import Command
# from pydantic import BaseModel, ConfigDict
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

from backend.Tools.services.sample_service import get_sample_name, fetch_protocol, retrieve_sample_info, fetchChildren, fetch_all_descendants, add_links

from backend.Tools.services.llm_service import summarize_sample_info, summarize_all_metadata_info

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

def supervisor_node(state: MessagesState) -> Command[Literal["link_retriever", "data_summarizer", "descendant_metadata_retriever", "basic_sample_info_retriever","FINISH"]]:
    # Step 1: Aggregate responses from all agents
    aggregated_agent_responses = ""
    for msg in state["messages"]:
        # If the message has a 'name' attribute, include it in the aggregation.
        agent_name = getattr(msg, "name", None)
        if agent_name:
            aggregated_agent_responses += f"Agent '{agent_name}' said: {msg.content}\n"
        else:
            aggregated_agent_responses += f"{msg.content}\n"
    
    # Step 2: Create a prompt that instructs the LLM to summarize all responses
    prompt = (
        "Please provide a comprehensive summary of the following agent responses:\n"
        f"{aggregated_agent_responses}\n"
        "Based on the original user request, decide which worker should act next. "
        "If the query is ambiguous or requires more details, ask a clarifying question instead of proceeding."
    )
    
    # Step 3: Build the messages list with the supervisor system prompt and the aggregated prompt
    messages = [
        {"role": "system", "content": SYS_MSG_SUPERVISOR},
        {"role": "user", "content": prompt},
    ] + state["messages"]
    
    # Step 4: Invoke the LLM with the structured output to get the next command and summary
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


toolset1 = [get_sample_name, retrieve_sample_info, fetch_protocol]

toolset2 = [fetchChildren, fetch_all_descendants]#fetchAllMetadata

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


def finish_node(state: MessagesState) -> Command[Literal["__end__"]]:
    goto = END
    return Command(
        update = {"messages": state["messages"]},
        goto=goto
        )
    #                update={"messages": [HumanMessage(content="Thank you for using NExtSEEK-Chat! Please visit our website (https://nextseek.mit.edu/) for more information. Have a great day!", name="FINISH")]})

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
