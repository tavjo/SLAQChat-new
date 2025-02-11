from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import START, StateGraph, END, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode
from typing import List, Optional
from typing_extensions import Annotated, TypedDict, Sequence, Literal
from langgraph.graph.message import add_messages
from langgraph.types import Command
# from pydantic import BaseModel, ConfigDict
# from langgraph.checkpoint.sqlite import SqliteSaver
import sys
import os
from baml_client import b as baml
from studio.models import AgentState, ConversationState
from studio.helpers import get_resource, update_resource, default_resource_box, get_available_workers, update_available_workers

from studio.prompts import (
    SYSTEM_MESSAGE,
    SYS_MSG_TOOLSET_3
)

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)


from backend.Tools.services.llm_service import summarize_sample_info
from src.chatbot.studio.basic_sample_info import basic_sample_info, TOOLSET1

# import env variables
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def supervisor_node(state: ConversationState) -> Command[Literal["basic_sample_info_retriever","responder"]]:
    work_groupA = [
        {"agent": "basic_sample_info_retriever",
        "role": "Retrieve basic metadata for the sample",
        "messages": {
            "system_message": SYSTEM_MESSAGE,
            "user_query": state["messages"][0].content,
            "aggregatedMessages": [msg.content for msg in state["messages"]]
        },
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
            "messages": {
            "system_message": SYSTEM_MESSAGE,
            "user_query": state["messages"][0].content,
            "aggregatedMessages": [msg.content for msg in state["messages"]]
        },
            "toolbox": ["data_summarizer", "response_formatter", "validator", "FINISH"],
            "tools_description": {
                "data_summarizer": "Summarize the data if response is longer than 100 words",
                "response_formatter": "Format the response if data_summarizer is used",
                "validator": "Validate the response",
                "FINISH": "Finish the conversation"
            }
        }
    ]
    if "available_workers" not in state or not state["available_workers"]:
        state["available_workers"] = work_groupA  # make a copy to update dynamically

    available_workers_list = [i["agent"] for i in state["available_workers"]]
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
    
    if "resource" not in state or not state["resource"]:
        state["resource"] = {}
    
    messages = {
        "system_message": SYSTEM_MESSAGE,
        "user_query": state["messages"][0].content,
        "aggregatedMessages": [aggregated_agent_responses],
        "available_workers": available_workers,
        "resource": state["messages"][-1].resource
    }
    response = baml.Supervise(messages, available_workers)
    goto = response.Next_worker.agent
    print(f"Next Worker: {goto}\nJustification: {response.justification}")
    if goto in available_workers_list:
        available_workers_list.remove(goto)
        available_workers = [worker for worker in available_workers if worker["agent"] != goto]
    print(f"Available Workers: {available_workers_list}")
    print(f"Available Workers: {available_workers}")
    return Command(update={"messages": [HumanMessage(content=response.justification, resource=state["resource"], name="supervisor")]},goto=goto)


########################################################
# Create agents
########################################################

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

async def create_worker(tools, func):
    async def chatbot(state: AgentState):
        summedMessages = [msg.content for msg in state["messages"]]
        user_query = state["messages"][0].content
        system_message = SYSTEM_MESSAGE
        messages = {
            "system_message": system_message,
            "user_query": user_query,
            "aggregatedMessages": summedMessages,
            "resource": state["messages"][-1].resource
        }
        result = await func(messages = messages)
        return {"messages": [result["result"]], "resource": result["resource"]}

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("agent", chatbot)

    tool_node = ToolNode(tools)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges(
        "agent",
        tools_condition,
    )
    graph_builder.add_edge("tools", "agent")
    graph_builder.set_entry_point("agent")
    return graph_builder.compile()


########################################################
# Tools
########################################################



toolset3 = [summarize_sample_info]


########################################################
# LLMs with bound tools
########################################################

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

## build agents
data_summarizer = create_agent(llm, toolset3, SYS_MSG_TOOLSET_3)

async def basic_sample_info_retriever_node(state: AgentState, tools = TOOLSET1, func = basic_sample_info) -> Command[Literal["supervisor"]]:
    basic_sample_info_retriever = await create_worker(tools, func)

    result = await basic_sample_info_retriever.ainvoke(state)
    print(result)
    response = result["messages"][-1].content
    print(result["resource"])
    return Command(
        update={
            "messages":[
                HumanMessage(content=response, resource=result["resource"], name="basic_sample_info_retriever")
            ]
        },
        goto="supervisor",
    )

def data_summarizer_node(state: AgentState) -> Command[Literal["responder"]]:
    # user_query = state["messages"][-1].user_query
    messages = {
        "system_message": SYSTEM_MESSAGE,
        "user_query": state["messages"][0].content,
        "aggregatedMessages": [msg.content for msg in state["messages"]],
        "resource": state["resource"]
        }
    result = baml.SummarizeData(messages)
    reource = result.messages.resource
    return Command(
        update={
            "messages":[
                HumanMessage(content=result.summary, name="data_summarizer")
                ]
            },
        goto="responder",
    )

def responder_node(state: AgentState) -> Command[Literal["data_summarizer","response_formatter","validator","FINISH"]]:
    work_groupB = [
        {
            "agent": "data_summarizer",
            "role": "1.(optional) Summarize the data if response is longer than 100 words",
            "messages": {
                "system_message": SYSTEM_MESSAGE,
                "user_query": state["messages"][0].content,
                "aggregatedMessages": [msg.content for msg in state["messages"]],
                "resource": state["resource"]
            },
            "toolbox": None,
            "tools_description": None
        },
        {
            "agent": "response_formatter",
            "role": "2. Format the response for the user",
            "messages": {
                "system_message": SYSTEM_MESSAGE,
                "user_query": state["messages"][0].content,
                "aggregatedMessages": [msg.content for msg in state["messages"]],
                "resource": state["resource"]
            },
            "toolbox": None,
            "tools_description": None
        },
        {
            "agent": "validator",
            "role": "3. Validate the response",
            "messages": {
                "system_message": SYSTEM_MESSAGE,
                "user_query": state["messages"][0].content,
                "aggregatedMessages": [msg.content for msg in state["messages"]],
                "resource": state["resource"]
            },
            "toolbox": None,
            "tools_description": None
        },
        {
            "agent": "FINISH",
            "role": "4.Finish the conversation",
            "messages": {
                "system_message": SYSTEM_MESSAGE,
                "user_query": state["messages"][0].content,
                "aggregatedMessages": [msg.content for msg in state["messages"]],
                "resource": state["resource"]
            },
            "toolbox": None,
            "tools_description": None
        }
    ]
        # Initialize the available workers map if not already in state
    if "available_workers" not in state:
        state["available_workers"] = work_groupB  # make a copy to update dynamically

    available_workers = state["available_workers"]
    available_workers_list = [i["agent"] for i in available_workers]
    messages = {
        "system_message": SYSTEM_MESSAGE,
        "user_query": state["messages"][0].content,
        "aggregatedMessages": [msg.content for msg in state["messages"]],
        "resource": state["resource"]
    }
    response = baml.Respond(messages, workers=available_workers)
    goto = response.Next_worker.agent
    print(f"Next Worker: {goto}\nJustification: {response.justification}")
    if goto in available_workers_list:
        available_workers_list.remove(goto)
        available_workers = [worker for worker in available_workers if worker["agent"] != goto]
    print(f"Available Workers: {available_workers_list}")
    available_workers = [i for i in available_workers_list]
    return Command(update={
            "messages":[
                HumanMessage(content=response.justification, name="responder")]},
                goto=goto)

def validator_node(state: AgentState) -> Command[Literal["responder"]]:
    messages = {
        "system_message": SYSTEM_MESSAGE,
        "user_query": state["messages"][0].content,
        "aggregatedMessages": [msg.content for msg in state["messages"]],
        "resource": state["resource"]
    }
    response = baml.ValidateResponse(inputMessage=messages)
    goto = "responder"
    print(f"Agent: {response.name}\nJustification: {response.justification}")
    if response.Valid:
        new_aggregate = str(response.Valid) + "\n" + response.justification
    else:
        new_aggregate = response.Clarifying_Question
    return Command(
        update={
            "messages":[
                HumanMessage(content=new_aggregate, name="validator")
            ]
        },
        goto=goto,
    )

def response_formatter_node(state: AgentState) -> Command[Literal["responder"]]:
    messages = {
    "system_message": SYSTEM_MESSAGE,
    "user_query": state["messages"][0].content,
    "aggregatedMessages": [msg.content for msg in state["messages"]],
    "resource": state["resource"]
}
    result = baml.FormatResponse(messages)
    print(result)
    print(f"Agent: {result.name}\nJustification: {result.justification}")
    goto = "responder"
    name = "response_formatter"
    return Command(
        update={
            "messages":[
                HumanMessage(content=result.formattedResponse, name=name)
            ]
        },
        goto=goto,
    )

def finish_node(state: AgentState) -> Command[Literal["__end__"]]:
    reply = state["messages"][-1].content
    print(reply)
    goto = END
    return Command(goto=goto)    

def sampleRetrieverGraph(state: MessagesState, memory = None):
    builder = StateGraph(MessagesState)
    builder.add_edge(START, "supervisor")
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("basic_sample_info_retriever", basic_sample_info_retriever_node)
    builder.add_node("data_summarizer", data_summarizer_node)
    builder.add_node("validator", validator_node)
    builder.add_node("responder", responder_node)
    builder.add_node("response_formatter", response_formatter_node)
    builder.add_node("FINISH", finish_node)
    builder.add_edge("responder", "FINISH")
    builder.add_edge("FINISH", END)

    # Compile graph
    if memory is not None:
        graph = builder.compile(checkpointer=memory)
    else:
        graph = builder.compile()
    return graph

# Example use without memory
graph = sampleRetrieverGraph(state = MessagesState)
