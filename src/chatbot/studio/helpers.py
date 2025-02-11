# src/chatbot/studio/helpers.py
# import asyncio
# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.chatbot.baml_client.async_client import b
from studio.prompts import SYSTEM_MESSAGE
from typing import Optional
from studio.models import ResourceBox, WorkerState, ConversationState
import asyncio
from langchain_core.messages import HumanMessage

async def async_navigator_handler(
    agent: WorkerState,
):
    """
    Asynchronously handles navigation using the BAML client.

    Parameters:
    - agent (str): The agent identifier.
    - toolbox (list[str]): A list of tool names available for navigation.
    - tools_description (dict[str, str]): A dictionary mapping tool names to their descriptions.
    - user_query (str): The user's query to be processed.
    - summedMessages (Optional[list[str]]): A list of previous messages to be considered.

    Returns:
    - tuple: A tuple containing the next tool to use and its arguments.

    Raises:
    - Exception: If an error occurs during the navigation process.
    """
    try:
        # Call the BAML Navigate function asynchronously.
        nav_stream = b.stream.Navigate(agent)
        
        # Await the final, fully parsed response.
        nav_response = await nav_stream.get_final_response()
        
        # Extract the tool choice and its argument.
        next_tool = nav_response.next_tool
        print(f"Next tool: {next_tool}\n Justification: {nav_response.justification}")
        tool_args = nav_response.tool_args
        return next_tool, tool_args
    except Exception as e:
        # Log the exception or handle it as needed
        print(f"An error occurred during navigation: {e}")
        raise


# Example: A default empty resources function if needed.
def default_resource_box() -> ResourceBox:
    return {
        "sample_metadata": [],
        "protocolURL": "",
        "sampleURL": "",
        "UIDs": []
    }
def available_workers() -> list[WorkerState]:
    return []

# Helper function to update the resource information.
def update_resource(state: ConversationState, new_resource: ResourceBox) -> None:
    """
    Merge new resource data into the state's resources.
    Fields from new_resource that are not None (or non-empty) overwrite the existing ones.
    """
    for key, value in new_resource.items():
        if value:  # You might want to check more specifically depending on the type.
            state["resources"][key] = value

def update_available_workers(state: ConversationState, new_workers: list[WorkerState]) -> None:
    state["available_workers"] = new_workers

def get_available_workers(state: ConversationState) -> list[WorkerState]:
    return state["available_workers"]

# Helper function to retrieve the current resources.
def get_resource(state: ConversationState) -> ResourceBox:
    return state["resources"]

# Example usage:
# (Make sure to run this inside an async event loop)
# result = asyncio.run(async_navigator_handler(
#     agent= {
#         "agent": "basic_sample_info_retriever",
#         "role": "sample_retriever",
#         "messages": {
#             "system_message": SYSTEM_MESSAGE,
#             "user_query": "Can you tell me more about the sample with UID PAV-220630FLY-1031?",
#             "aggregatedMessages": ["Can you tell me more about the sample with UID PAV-220630FLY-1031?"]
#         },
#         "toolbox": ["get_sample_name", "retrieve_sample_info", "add_links"],
#         "tools_description": {
#             "get_sample_name": "Get the name of the sample.",
#             "retrieve_sample_info": "Retrieve the sample information for a given sample UID.",
#             "add_links": "Add links to the sample."
#         }
#     }
# ))
# print(result)