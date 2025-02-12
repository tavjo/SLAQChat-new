# src/chatbot/studio/basic_sample_info.py

import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.services.sample_service import get_sample_name, fetch_protocol, retrieve_sample_info, fetchChildren, fetch_all_descendants, add_links

from src.chatbot.studio.helpers import async_navigator_handler, update_resource, default_resource_box
import asyncio
from langchain_core.messages import HumanMessage
from src.chatbot.studio.models import ConversationState
from src.chatbot.studio.helpers import create_worker
from langgraph.types import Command
from typing_extensions import Literal

TOOLSET1 = [get_sample_name, retrieve_sample_info, fetch_protocol, fetchChildren, fetch_all_descendants, add_links]

async def basic_sample_info(state: ConversationState)->dict|None:
    """
    Main function to handle the asynchronous navigation and tool execution.

    This function uses the async navigator handler to determine the next tool
    to execute based on a user query. It then calls the appropriate tool function
    asynchronously and returns the result.

    Returns:
        result (dict): A dictionary containing the result from the executed tool function, the agent, the toolbox, and the tools_description.
    """

    agent = "basic_sample_info_retriever"
    toolbox=["get_sample_name", "retrieve_sample_info", "fetch_protocol", "fetchChildren", "fetch_all_descendants", "add_links"]
    tools_description={
                "get_sample_name": "Get the name of the sample.",
                "retrieve_sample_info": "Retrieve the sample information for a given sample UID.",
                "fetch_protocol": "Fetch the protocol for a given sample UID.",
                "fetchChildren": "Fetch the children of a given sample UID.",
                "fetch_all_descendants": "Fetch all descendants of a given sample UID.",
                "add_links": "Add links to the sample information."
            }

    AGENT = {
        "agent": agent,
        "role": "retrieves sample information from the database",
        "toolbox": toolbox,
        "tools_description": tools_description,
    }
    try:
        # Call the async navigator handler
        next_tool, tool_args, justification = await async_navigator_handler(AGENT, state)

        print(f"Next tool: {next_tool}")
        print(f"Tool args: {tool_args[0]}")

        tool_dispatch = {
            "get_sample_name": get_sample_name,
            "retrieve_sample_info": retrieve_sample_info,
            "fetch_protocol": fetch_protocol,
            "fetchChildren": fetchChildren,
            "fetch_all_descendants": fetch_all_descendants,
            "add_links": add_links,
        }

        uid = tool_args[0] if isinstance(tool_args, list) else tool_args

        if next_tool == "retrieve_sample_info":
            resource_type = "sample_metadata"
        elif next_tool == "fetch_protocol":
            resource_type = "protocolURL"
        elif next_tool == "fetchChildren":
            resource_type = "UIDs"
        elif next_tool == "fetch_all_descendants":
            resource_type = "UIDs"
        elif next_tool == "add_links":
            resource_type = "sampleURL"

        result = await tool_dispatch[next_tool](uid)
        
        if result:
            new_resource = {
                resource_type: result,
            }
            update_resource(state, new_resource)
            print(f"Updated resource: {state['resources']}")
        else:
            print(f"No result from {next_tool}")
        
        response = {
            "result": f"The {next_tool} tool has been executed successfully. The result is: {result}",
            "agent": agent,
            "tool": next_tool,
            "new_resource": new_resource,
            "justification": justification
        }
        
        return response
        # return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

async def basic_sample_info_retriever_node(state: ConversationState, tools = TOOLSET1, func = basic_sample_info) -> Command[Literal["supervisor"]]:
    basic_sample_info_retriever = await create_worker(tools, func)

    result = await basic_sample_info_retriever.ainvoke(state)
    print(result["messages"][-1].content)
    update_resource(state, result["resources"])
    print(state["resources"])
    updated_messages = state["messages"] + [HumanMessage(content=result["messages"][-1].content, name="basic_sample_info_retriever")]
    return Command(
        update={
            "messages": updated_messages,
            "resources": result["resources"]
        },
        goto="supervisor",
    )

if __name__ == "__main__":
    # asyncio.run(basic_sample_info())
    initial_state: ConversationState = {
        "messages": [HumanMessage(content="Can you tell me more about the sample with UID PAV-220630FLY-1031?")],
        "resources": default_resource_box(),
    }
    # results = asyncio.run(basic_sample_info(initial_state))
    results = asyncio.run(basic_sample_info_retriever_node(initial_state))
    print(results)
