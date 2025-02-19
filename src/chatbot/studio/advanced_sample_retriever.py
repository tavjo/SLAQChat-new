# src/chatbot/studio/basic_sample_info.py

import sys
import os
import time

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

# from backend.Tools.services.sample_service import *
from backend.Tools.services.module_to_json import functions_to_json

from src.chatbot.studio.helpers import async_navigator_handler, update_resource, default_resource_box
import asyncio
from langchain_core.messages import HumanMessage
from src.chatbot.studio.models import ConversationState
from src.chatbot.studio.helpers import create_worker#, create_agent
from langgraph.types import Command
from typing_extensions import Literal
# from langchain_openai import ChatOpenAI

from src.chatbot.studio.prompts import TOOLSET2
TOOL_DISPATCH = {
    attr.__name__: attr for attr in TOOLSET2
}

async def multi_sample_info(state: ConversationState)->dict|None:
    """
    Main function to handle the asynchronous navigation and tool execution.

    This function uses the async navigator handler to determine the next tool
    to execute based on a user query. It then calls the appropriate tool function
    asynchronously and returns the result.

    Returns:
        result (dict): A dictionary containing the result from the executed tool function, the agent, the toolbox, and the tools_description.
    """

    agent = "multi_sample_info_retriever"

    AGENT = {
        "agent": agent,
        "role": "retrieves information for multiple samples from the database",
        "toolbox": functions_to_json(TOOLSET2)
    }
    try:
        # Call the async navigator handler
        next_tool, tool_args, justification = await async_navigator_handler(AGENT, state)

        print(f"Next tool: {next_tool}")
        print(f"Tool args: {tool_args}")

        if next_tool ==  "get_metadata_by_uids":
            resource_type = "sample_metadata"
        elif next_tool == "get_uids_by_terms_and_field":
            resource_type = "UIDs"
            tool_args = (tool_args[0], tool_args[1])
        
        elif next_tool == "" and len(tool_args) == 0:
            response = {
                "result": "No tool was selected. Invalid query.",
                "agent": agent,
                "justification": justification
            }
            return response
        else:
            result = await TOOL_DISPATCH[next_tool](*tool_args)
        
        if result and result is not None:
            new_resource = {
                resource_type: result,
            }
            update_resource(state, new_resource)
            print(f"Updated resource: {state['resources']}")
            response = {
            "result": f"The {next_tool} tool has been executed successfully. The result is: {result}",
            "agent": agent,
            "tool": next_tool,
            "new_resource": new_resource,
            "justification": justification
            }
            return response
        else:
            print(f"No result from {next_tool}")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

async def multi_sample_info_retriever_node(state: ConversationState, tools = TOOLSET2, func = multi_sample_info) -> Command[Literal["supervisor"]]:
    """
    Asynchronously retrieves sample information using a specified function and updates the conversation state.

    Args:
        state (ConversationState): The current state of the conversation.
        tools (list): A list of tools to be used by the worker.
        func (callable): The function to be executed by the worker.

    Returns:
        Command[Literal["supervisor"]]: A command object with updated messages and resources, directing the flow to the supervisor.

    Raises:
        Exception: If any error occurs during the execution of the worker or invocation.
    """
    try:
        start_time = time.time()
        print("Creating worker...")
        multi_sample_info_retriever = await create_worker(tools,func)
        print(f"Worker created in {time.time() - start_time:.2f} seconds.")

        start_time = time.time()
        print("Invoking multi_sample_info_retriever...")
        result = await multi_sample_info_retriever.ainvoke(state)
        print(f"Invocation completed in {time.time() - start_time:.2f} seconds.")
        if result and result is not None:
            print(result["messages"][-1].content)
            updated_messages = state["messages"] + [HumanMessage(content=result["messages"][-1].content, name="multi_sample_info_retriever")]
        # update_resource(state, result["new_resource"])
        # print(state["resources"])
            return Command(
                update={
                    "messages": updated_messages
                },
                goto="supervisor",
            )
    except Exception as e:
        messages = f"An error occurred while retrieving sample information: {e}"
        updated_messages = state["messages"] + [HumanMessage(content=messages, name="multi_sample_info_retriever")]
        print(messages)
        return Command(
            update={
                "messages": updated_messages
            },
            goto="supervisor",
        )

if __name__ == "__main__":
    # asyncio.run(basic_sample_info())
    initial_state: ConversationState = {
        # "messages": [HumanMessage(content="What organ did each of these samples come from: TIS-200901ENG-11,TIS-200901ENG-12,TIS-210322ENG-9?")],
        "messages": [HumanMessage(content="Please find the UIDs of all samples that are part of the 'CD8 Depletion' study.", name="user"),
                     HumanMessage(content=""" 
        pseudo_query: "SELECT json_metadata->>'UID' AS uid FROM seek_production.samples WHERE json_metadata->>'Study' = 'CD8 Depletion'"\n"justification": "The 'seek_production.samples' table contains the 'json_metadata' column, which holds sample-specific data including the 'Genotype' and 'UID'. The query is designed to extract UIDs of samples that are part of the 'CD8 Depletion' study by filtering based on the relevant key in the JSON metadata."
""", name="schema_mapper")
                     ],
        # "messages": [HumanMessage(content="What is the weather today?")],
        "resources": default_resource_box()
    }
    # results = asyncio.run(basic_sample_info(initial_state))
    results = asyncio.run(multi_sample_info_retriever_node(initial_state))
    print(results)
