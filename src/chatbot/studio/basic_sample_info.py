# src/chatbot/studio/basic_sample_info.py

import sys
import os
import time
import logging
import traceback

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.services.sample_service import *
from backend.Tools.services.module_to_json import functions_to_json

from src.chatbot.studio.helpers import async_navigator_handler, update_resource, default_resource_box, get_resource
import asyncio
from langchain_core.messages import HumanMessage, AIMessage
from src.chatbot.studio.models import ConversationState, ToolResponse
from src.chatbot.studio.helpers import create_tool_call_node
from langgraph.types import Command
from typing_extensions import Literal
from dotenv import load_dotenv
# from datetime import datetime, timezone

load_dotenv()

from src.chatbot.studio.prompts import TOOLSET1, INITIAL_STATE
TOOL_DISPATCH = {
    attr.__name__: attr for attr in TOOLSET1
}

# Configure logger
logger = logging.getLogger(__name__)

async def basic_sample_info(state: ConversationState = INITIAL_STATE)->ToolResponse:
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
        next_tool, tool_args, justification, explanation = await async_navigator_handler(AGENT, state)
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
            logger.warning("No tool was selected. Invalid query.")
            response = ToolResponse(
                result=get_resource(state),
                response="No tool was selected. Invalid query.",
                agent=agent,
                justification=justification,
                explanation=explanation
            )
            return response
        
        logger.info(f"Executing {next_tool} with args: {uid}")
        
        try:
            result = await TOOL_DISPATCH[next_tool](uid)
        except KeyError:
            logger.error(f"Tool '{next_tool}' not found in TOOL_DISPATCH")
            return ToolResponse(
                result=get_resource(state),
                response=f"Error: Tool '{next_tool}' not available",
                agent=agent,
                justification=justification,
                explanation=explanation
            )
        except Exception as tool_error:
            logger.error(f"Error executing {next_tool}: {tool_error}", exc_info=True)
            return ToolResponse(
                result=get_resource(state),
                response=f"Error executing {next_tool}: {tool_error}",
                agent=agent,
                justification=justification,
                explanation=explanation
            )
        
        if result:
            new_resource = {
                resource_type: result
            }
            update_resource(state, new_resource)
            logger.debug(f"Updated resource: {get_resource(state)}")
        else:
            logger.info(f"No result from {next_tool}")
        
        return ToolResponse(
            result=get_resource(state),
            response=f"The {next_tool} tool has been executed successfully. The result is: {result}",
            agent=agent,
            justification=justification,
            explanation=explanation
        )
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"An error occurred: {e}\n{error_trace}")
        return ToolResponse(
            result=get_resource(state),
            response=f"An error occurred: {e}",
            agent=agent,
            justification=justification,
            explanation=explanation
        )

async def basic_sample_info_retriever_node(state: ConversationState = INITIAL_STATE, tools = TOOLSET1, func = basic_sample_info)-> Command[Literal["supervisor", "validator"]]:
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
    return await create_tool_call_node(state,tools,func,"basic_sample_info_retriever")


if __name__ == "__main__":
    # asyncio.run(basic_sample_info())
    initial_state: ConversationState = {
        "messages": [HumanMessage(content="Can you tell me more about the sample with UID PAV-220630FLY-1031?", name="user"),
                     AIMessage(content="""Parsed User Query: ```json
{'uid': 'PAV-220630FLY-1031', 'sampletype': None, 'assay': None, 'attribute': None, 'terms': None}
```
Justification: The query explicitly mentions a UID, which is a unique identifier for a sample. There are no other specific attributes, sample types, assays, or terms mentioned in the query.
Explanation: The user query is asking for more information about a specific sample identified by the UID 'PAV-220630FLY-1031'.
""", name="query_parser")
                     ],
        # "messages": [HumanMessage(content="What is the weather today?")],
        "resources": default_resource_box(),
    }
    INITIAL_STATE.messages.extend(initial_state["messages"])
    asyncio.run(basic_sample_info_retriever_node())
    # print(results)
