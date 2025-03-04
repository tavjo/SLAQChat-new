# src/chatbot/studio/helpers.py
# import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# from src.chatbot.baml_client.async_client import b
from src.chatbot.studio.models import ResourceBox, WorkerState, ConversationState
# from src.chatbot.studio.prompts import SYSTEM_MESSAGE
# from langgraph.graph import StateGraph
# from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import HumanMessage, AnyMessage, SystemMessage
import time

def available_workers() -> list[WorkerState]:
    from src.chatbot.studio.models import WorkerState
    return []

# Example: A default empty resources function if needed.
def default_resource_box() -> ResourceBox:
    from src.chatbot.studio.models import ResourceBox
    return {
        "sample_metadata": [],
        "protocolURL": "",
        "sampleURL": "",
        "UIDs": [],
        "db_schema": None,
        "parsed_query": None
    }

# Helper function to update the resource information.
def update_resource(state: ConversationState, new_resource: ResourceBox) -> None:
    from src.chatbot.studio.models import ResourceBox, ConversationState
    """
    Merge new resource data into the state's resources.
    Fields from new_resource that are explicitly provided will overwrite the existing ones,
    including empty values (empty lists, empty strings).
    """
    if "resources" not in state or state["resources"] is None:
        state["resources"] = default_resource_box()
    
    for key, value in new_resource.items():
        if key in state["resources"]:  # Only update keys that exist in the ResourceBox
            state["resources"][key] = value  # Update even if value is empty/falsy

def update_available_workers(state: ConversationState, new_workers: list[WorkerState]) -> None:
    from src.chatbot.studio.models import WorkerState, ConversationState
    state["available_workers"] = new_workers


def get_available_workers(state: ConversationState) -> list[WorkerState]:
    from src.chatbot.studio.models import ConversationState, WorkerState
    return state["available_workers"]

# Helper function to retrieve the current resources.
def get_resource(state: ConversationState) -> ResourceBox:
    from src.chatbot.studio.models import ConversationState, ResourceBox
    
    # If resources don't exist or are None, return default ResourceBox
    if "resources" not in state or state["resources"] is None:
        return default_resource_box()
        
    # Ensure returned value is a valid ResourceBox
    resources = state["resources"]
    if not isinstance(resources, dict):
        # If not a dict, return default
        return default_resource_box()
        
    # Validate the structure or convert to proper ResourceBox format
    resource_box: ResourceBox = {
        "sample_metadata": resources.get("sample_metadata", []),
        "protocolURL": resources.get("protocolURL", ""),
        "sampleURL": resources.get("sampleURL", ""),
        "UIDs": resources.get("UIDs", []),
        "db_schema": resources.get("db_schema", None),
        "parsed_query": resources.get("parsed_query", None)
    }
    
    return resource_box

def get_messages(state: ConversationState) -> list[AnyMessage]:
    return state["messages"]

def update_messages(state: ConversationState, new_messages: list[AnyMessage]) -> None:
    if state["messages"][0].name == "system" and len(state["messages"]) == 1:
        state["messages"] = get_messages(state) + new_messages
    else:
        state["messages"] = SystemMessage(content=state["messages"][0].content, name="system") + new_messages

async def async_navigator_handler(
    agent: WorkerState,
    state: ConversationState
):
    from src.chatbot.studio.models import WorkerState, ConversationState
    from src.chatbot.baml_client.async_client import b
    from src.chatbot.studio.prompts import SYSTEM_MESSAGE


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
        if "resources" not in state or state["resources"] is None:
            state["resources"] = default_resource_box()
        
        print(f" State messages: {state['messages']}")

        print("Creating payload...")

        payload = {
        "system_message": SYSTEM_MESSAGE,
        "user_query": state["messages"][1].content,
        "aggregatedMessages": [msg.content for msg in state["messages"]],
        "resource": get_resource(state)
        }
        print("Payload created.")
        print(f" Payload messages: {payload['aggregatedMessages']}")
        # Call the BAML Navigate function asynchronously.
        start_time = time.time()
        print("Calling BAML Navigator function...")
        nav_stream = b.stream.Navigate(agent, payload)
        
        # Await the final, fully parsed response.
        nav_response = await nav_stream.get_final_response()
        
        # Extract the tool choice and its argument.
        next_tool = nav_response.next_tool
        # print(f"Next tool: {next_tool}\n Justification: {nav_response.justification}")
        tool_args = nav_response.tool_args
        print(f"Navigation completed in {time.time() - start_time:.2f} seconds.")
        return next_tool, tool_args, nav_response.justification, nav_response.explanation
    except Exception as e:
        # Log the exception or handle it as needed
        print(f"An error occurred during navigation: {e}")
        raise

def create_agent(llm, tools, msg):
    from src.chatbot.studio.models import ConversationState
    from langchain_core.messages import HumanMessage
    from langgraph.graph import StateGraph
    from langgraph.prebuilt import tools_condition, ToolNode
    llm_with_tools = llm.bind_tools(tools)
    def chatbot(state: ConversationState):
        return {"messages": [llm_with_tools.invoke(state["messages"] + [{"role": "system", "content": msg}])]}

    graph_builder = StateGraph(ConversationState)
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
    from src.chatbot.studio.models import ConversationState
    from langchain_core.messages import HumanMessage
    from langgraph.graph import StateGraph
    from langgraph.prebuilt import tools_condition, ToolNode

    async def chatbot(state: ConversationState):
        response = await func(state)
        if response["result"]:
            messages = response["result"] + "\n" + response["justification"]
            return {"messages": [HumanMessage(content=messages)],
                    'resources': response["new_resource"]}
        else:
            return {"messages": [HumanMessage(content="Error retrieving data.")]}

    graph_builder = StateGraph(ConversationState)
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