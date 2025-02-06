from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import START, StateGraph, MessagesState, END
from langgraph.prebuilt import tools_condition, ToolNode
from typing import List
from typing_extensions import Annotated, TypedDict, Sequence, Literal
from langgraph.graph.message import add_messages
from langgraph.types import Command
# from pydantic import BaseModel, ConfigDict
# from langgraph.checkpoint.sqlite import SqliteSaver
import sys
import os
from baml_client import b as baml

from studio.prompts import (
    SYS_MSG_TOOLSET_1,
    SYS_MSG_TOOLSET_2,
    SYS_MSG_TOOLSET_3,
    SYS_MSG_LINK_ADDER,
)

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.services.sample_service import get_sample_name, fetch_protocol, retrieve_sample_info, fetchChildren, fetch_all_descendants, add_links

from backend.Tools.services.llm_service import summarize_sample_info

# import env variables
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


# Define router type for structured output

# class Router(TypedDict):
#     """Worker to route to next. If no workers needed, route to FINISH."""
#     next: Literal["descendant_metadata_retriever", "link_retriever", "basic_sample_info_retriever","responder"]



def supervisor_node(state: MessagesState) -> Command[Literal["link_retriever", "descendant_metadata_retriever", "basic_sample_info_retriever","responder"]]:
    work_groupA = {
    "descendant_metadata_retriever":"Retrieve descendant metadata for the sample",
    "link_retriever": "Retrieve link for the sample and/or the associatedprotocol",
    "basic_sample_info_retriever": "Retrieve basic sample info for the sample",
    "responder": "Validate and respond to the user's query",
}
    if "available_workers" not in state:
        state["available_workers"] = work_groupA  # make a copy to update dynamically

    available_workers = state["available_workers"]
    # Step 1: Aggregate responses from all agents
    aggregated_agent_responses = ""
    for msg in state["messages"]:
        # If the message has a 'name' attribute, include it in the aggregation.
        agent_name = getattr(msg, "name", None)
        if agent_name:
            aggregated_agent_responses += f"Agent '{agent_name}' said: {msg.content}\n"
        else:
            aggregated_agent_responses += f"{msg.content}\n"
    
    response = baml.Supervise(aggregated_agent_responses, available_workers)
    goto = response.Next_worker
    print(f"Next Worker: {goto}")
    if goto in available_workers:
        del available_workers[goto]
    print(f"Available Workers: {available_workers}")
    # Save the updated available_workers back to state
    state["available_workers"] = available_workers
    return Command(update={
        "messages":[
            HumanMessage(content=response.aggregatedMessages,user_query=response.user_query)
        ]}
        ,goto=goto)


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


toolset1 = [get_sample_name, retrieve_sample_info]

toolset2 = [fetchChildren, fetch_all_descendants]#fetchAllMetadata

toolset3 = [summarize_sample_info]

toolset4 = [add_links, fetch_protocol]

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

def data_summarizer_node(state: MessagesState) -> Command[Literal["responder"]]:
    # messages = [
    #     HumanMessage(content=state["messages"][-1].content, name="data_summarizer")
    # ]
    # result = data_summarizer.invoke(messages)
    user_query = state["messages"][-1].user_query
    result = baml.SummarizeData(state["messages"][-1].content, user_query)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result.summary, name="data_summarizer", user_query=user_query)
            ]
        },
        goto="responder",
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

# class postRouter(TypedDict):
#     """Worker to route to next. If no workers needed, route to FINISH."""
#     next: Literal["data_summarizer","response_formatter","validator","FINISH"]

def responder_node(state: MessagesState) -> Command[Literal["data_summarizer","response_formatter","validator","FINISH"]]:

    work_groupB = {
    "data_summarizer":"1.(optional) Summarize the data if response is longer than 100 words",
    "response_formatter":"2.(optional) Format the response if data_summarizer is used",
    "validator":"3.Validate the response",
    "FINISH":"4.Finish the conversation"
    }
        # Initialize the available workers map if not already in state
    if "available_workers" not in state:
        state["available_workers"] = work_groupB  # make a copy to update dynamically

    available_workers = state["available_workers"]
    # Aggregate the content of each HumanMessage into a single string
    inputMessage = state["messages"][-1].content
    user_query = state["messages"][-1].user_query
    prev_worker = state["messages"][-1].name if state["messages"][-1].name else ""
    # inputMessage = "\n".join([msg.content for msg in state["messages"]])
    # print(inputMessage)
    response = baml.Respond(inputMessage, workers=available_workers, user_query=user_query, prev_worker=prev_worker)
    goto = response.Next_worker
    print(f"Next Worker: {goto}")
    if goto in available_workers:
        del available_workers[goto]
    print(f"Available Workers: {available_workers}")
    # Save the updated available_workers back to state
    state["available_workers"] = available_workers
    return Command(update={
            "messages":[
                HumanMessage(content=response.aggregatedMessages,user_query=user_query, available_workers=available_workers)
            ]
        },goto=goto)

def validator_node(state: AgentState) -> Command[Literal["responder"]]:
    # # Aggregate the content of each HumanMessage into a single string
    # aggregated_messages = "\n".join([msg.content for msg in state["messages"]])
    aggregated_messages = state["messages"][-1].content
    user_query = state["messages"][-1].user_query
    print(user_query)
    response = baml.ValidateResponse(user_query=user_query, response=aggregated_messages)
    goto = response.Next_worker
    print(response.name)
    if response.Valid:
        new_aggregate = response.originalMessage
    else:
        new_aggregate = response.Clarifying_Question
    return Command(
        update={
            "messages": [
                HumanMessage(content=new_aggregate, name="validator", user_query=user_query)
            ]
        },
        goto=goto,
    )

def response_formatter_node(state: MessagesState) -> Command[Literal["responder"]]:
    user_query = state["messages"][-1].user_query
    result = baml.FormatResponse(user_query,state["messages"][-1].content)
    print(result)
    goto = result.Next_worker
    name = "response_formatter"
    return Command(
        update={
            "messages": [
                HumanMessage(content=result.formattedResponse, name=name, user_query=user_query)
            ]
        },
        goto=goto,
    )

def finish_node(state: MessagesState) -> Command[Literal["__end__"]]:
    messages = state["messages"][-1].content
    print(messages)
    goto = END
    return Command(goto=goto)    

def sampleRetrieverGraph(state: MessagesState, memory = None):
    builder = StateGraph(MessagesState)
    builder.add_edge(START, "supervisor")
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("basic_sample_info_retriever", basic_sample_info_retriever_node)
    builder.add_node("descendant_metadata_retriever", descendant_metadata_retriever_node)
    builder.add_node("data_summarizer", data_summarizer_node)
    builder.add_node("link_retriever", link_retriever_node)
    builder.add_node("validator", validator_node)
    builder.add_node("responder", responder_node)
    builder.add_node("response_formatter", response_formatter_node)
    builder.add_node("FINISH", finish_node)

    # Compile graph
    if memory is not None:
        graph = builder.compile(checkpointer=memory)
    else:
        graph = builder.compile()
    return graph

# Example use without memory
graph = sampleRetrieverGraph(state = MessagesState)
