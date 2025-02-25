# src/chatbot/studio/basic_sample_info.py

import sys
import os
import time

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.services.sample_service import *
from backend.Tools.services.module_to_json import functions_to_json, module_to_json

from src.chatbot.studio.helpers import async_navigator_handler, update_resource, default_resource_box
import asyncio
from langchain_core.messages import HumanMessage, SystemMessage
from src.chatbot.studio.models import ConversationState
from src.chatbot.studio.helpers import create_worker#, create_agent
from langgraph.types import Command
from typing_extensions import Literal
# from langchain_openai import ChatOpenAI
# from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()

from src.chatbot.studio.prompts import TOOLSET1, INITIAL_STATE
TOOL_DISPATCH = {
    attr.__name__: attr for attr in TOOLSET1
}

async def basic_sample_info(state: ConversationState = INITIAL_STATE)->dict|None:
    """
    Main function to handle the asynchronous navigation and tool execution.

    This function uses the async navigator handler to determine the next tool
    to execute based on a user query. It then calls the appropriate tool function
    asynchronously and returns the result.

    Returns:
        result (dict): A dictionary containing the result from the executed tool function, the agent, the toolbox, and the tools_description.
    """

    agent = "basic_sample_info_retriever"

    AGENT = {
        "agent": agent,
        "role": "retrieves sample information from the database",
        "toolbox": functions_to_json(TOOLSET1)
    }
    try:
        # Call the async navigator handler
        next_tool, tool_args, justification = await async_navigator_handler(AGENT, state)

        # print(f"Next tool: {next_tool}")
        # print(f"Tool args: {tool_args[0]}")

        # uid = tool_args[0] if isinstance(tool_args, list) else tool_args
        uid = tool_args.uid if isinstance(tool_args.uid, str) else tool_args.uid[0]

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
        
        if next_tool == "" and len(tool_args) == 0:
            response = {
                "result": "No tool was selected. Invalid query.",
                "agent": agent,
                "justification": justification
            }
            return response
        
        print(f"Executing {next_tool} with args: {uid}")
        result = await TOOL_DISPATCH[next_tool](uid)
        
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

async def basic_sample_info_retriever_node(state: ConversationState = INITIAL_STATE, tools = TOOLSET1, func = basic_sample_info) -> Command[Literal["supervisor", "FINISH"]]:
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
        basic_sample_info_retriever = await create_worker(tools,func)
        print(f"Worker created in {time.time() - start_time:.2f} seconds.")

        start_time = time.time()
        print("Invoking basic_sample_info_retriever...")
        result = await basic_sample_info_retriever.ainvoke(state)
        print(f"Invocation completed in {time.time() - start_time:.2f} seconds.")
        print(result["messages"][-1].content)
        # update_resource(state, result["new_resource"])
        print(state["resources"])

        updated_messages = state["messages"] + [HumanMessage(content=result["messages"][-1].content, name="basic_sample_info_retriever")]
        return Command(
            update={
                "messages": updated_messages,
                "resources": state["resources"]
            },
            goto="supervisor",
        )
    except Exception as e:
        messages = f"An error occurred while retrieving sample information: {e}"
        updated_messages = state["messages"] + [HumanMessage(content=messages, name="basic_sample_info_retriever")]
        print(messages)
        return Command(
            update={
                "messages": updated_messages
            },
            goto="FINISH",
        )

# async def basic_sample_info_retriever_node(state: ConversationState, tools = TOOLSET1) -> Command[Literal["supervisor"]]:
#     """
#     Asynchronously retrieves sample information using a specified function and updates the conversation state.

#     Args:
#         state (ConversationState): The current state of the conversation.
#         tools (list): A list of tools to be used by the worker.
#         func (callable): The function to be executed by the worker.

#     Returns:
#         Command[Literal["supervisor"]]: A command object with updated messages and resources, directing the flow to the supervisor.

#     Raises:
#         Exception: If any error occurs during the execution of the worker or invocation.
#     """
#     try:
#         start_time = time.time()
#         print("Creating worker...")
#         # basic_sample_info_retriever = await create_worker(tools,func)
#         # prompt = state["messages"] + [SystemMessage(content=SYSTEM_MESSAGE)]
#         # prompt_message = "\n".join([message.content for message in prompt])
#         basic_sample_info_retriever = create_react_agent(
#             model=ChatOpenAI(model="gpt-4o-mini", temperature=0),
#             tools=TOOLSET1,
#             prompt=SYSTEM_MESSAGE   
#         )
#         print(f"Worker created in {time.time() - start_time:.2f} seconds.")

#         start_time = time.time()
#         print("Invoking basic_sample_info_retriever...")
#         result = await basic_sample_info_retriever.ainvoke(state)
#         print(f"Invocation completed in {time.time() - start_time:.2f} seconds.")
#         print(result["messages"][-1].content)
#         # update_resource(state, result["new_resource"])
#         # print(state["resources"])

#         updated_messages = state["messages"] + [HumanMessage(content=result["messages"][-1].content, name="basic_sample_info_retriever")]
#         return Command(
#             update={
#                 "messages": updated_messages,
#                 "resources": state["resources"]
#             },
#             goto="supervisor",
#         )
#     except Exception as e:
#         messages = f"An error occurred while retrieving sample information: {e}"
#         updated_messages = state["messages"] + [HumanMessage(content=messages, name="basic_sample_info_retriever")]
#         print(messages)
#         return Command(
#             update={
#                 "messages": updated_messages
#             },
#             goto="supervisor",
#         )

if __name__ == "__main__":
    # asyncio.run(basic_sample_info())
    initial_state: ConversationState = {
        "messages": [HumanMessage(content="Can you tell me more about the sample with UID PAV-220630FLY-1031?")],
        # "messages": [HumanMessage(content="What is the weather today?")],
        "resources": default_resource_box(),
    }
    # results = asyncio.run(basic_sample_info(initial_state))
    results = asyncio.run(basic_sample_info_retriever_node(initial_state))
    print(results)
