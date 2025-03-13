# src/chatbot/studio/update_records.py

import sys
import os
import time

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

# from backend.Tools.services.sample_service import *
from backend.Tools.services.module_to_json import functions_to_json

from src.chatbot.studio.helpers import update_resource, default_resource_box, async_navigator_handler, get_resource
# from backend.Tools.schemas import UpdatePipelineMetadata
import asyncio
from langchain_core.messages import HumanMessage
from src.chatbot.studio.models import ConversationState, ToolResponse
from src.chatbot.studio.helpers import create_tool_call_node
from langgraph.types import Command
from typing_extensions import Literal
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

from src.chatbot.studio.prompts import TOOLSET3, INITIAL_STATE
TOOL_DISPATCH = {
    attr.__name__: attr for attr in TOOLSET3
}
# from datetime import datetime, timezone

async def update_records(state: ConversationState = INITIAL_STATE)->ToolResponse:
    """
    Main function to handle the asynchronous navigation and tool execution.

    This function uses the async navigator handler to determine the next tool
    to execute based on a user query. It then calls the appropriate tool function
    asynchronously and returns the result.

    Returns:
        result (dict): A dictionary containing the result from the executed tool function, the agent, the toolbox, and the tools_description.
    """

    agent = "archivist"

    AGENT = {
        "agent": agent,
        "role": "Updates metadata for samples",
        "toolbox": functions_to_json(TOOLSET3)
    }
    # response = None
    result = None
    try:
        # Call the async navigator handler
        next_tool, tool_args, justification, explanation = await async_navigator_handler(AGENT, state)
        logger.info(f"Justification: {justification}\nExplanation: {explanation}")
        if tool_args:
            logger.info(f"Tool args: {tool_args}")
        if next_tool ==  "update_metadata_pipeline":
            tool_args = None
            logger.info(f"Executing {next_tool}")
            result = await TOOL_DISPATCH[next_tool]()
            resource_type = "update_info"
        elif next_tool == "get_st_attributes":
            resource_type = "st_attributes"
            tool_args = ('object', tool_args.sample_type)
            logger.info(f"Executing {next_tool} with tool_args: {tool_args}")
            result = await TOOL_DISPATCH[next_tool](*tool_args)
        elif next_tool == "" and len(tool_args) == 0:
            response = ToolResponse(
                result=state.resources if state.resources else default_resource_box(),
                response="No tool was selected. Invalid query.",
                agent=agent,
                justification=justification,
                explanation=explanation
            )
            return response
                
        if result:
            new_resource = {
                resource_type: result,
            }
            update_resource(state, new_resource)
            # logger.debug(f"Result: {result}")
            logger.info("Updating state resources")
            # if resource_type == "st_attributes":
            #     state.resources = ResourceBox(st_attributes=result)
            # elif resource_type == "update_info":
            #     state.resources = ResourceBox(update_info=result)
            # else:
            #     state.resources = default_resource_box()
            logger.debug(f"Updated resource: {state.resources}")
            logger.info(f"Creating response object...")
            response = ToolResponse(
            result=get_resource(state),
            response=f"The {next_tool} tool has been executed successfully. The result is: ```json\n{result}\n```",
            agent=agent,
            justification=justification,
            explanation=explanation
            )
            logger.info(f"Response object created: {response}")
            # msg = HumanMessage(content = response["response"] + "\n" + response["justification"] + "\n" + response["explanation"], name = agent)
            # state.messages.append(msg)
            # update_messages(state, msg)
            # logger.debug(list(response.keys()))
            logger.info(f"Successfully completed tool call {next_tool} for agent : {agent}.")
            return response
        else:
            logger.warning(f"No result from {next_tool}")
            # Return a response with empty result to avoid KeyError
            return ToolResponse(
                result=get_resource(state),
                response=f"No result was returned from {next_tool}",
                agent=agent,
                justification=justification,
                explanation=explanation
            )
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return ToolResponse(
            result=get_resource(state),
            response=f"An error occurred: {e}",
            agent=agent,
            justification=justification,
            explanation=explanation
        )

async def archivist_node(state: ConversationState = INITIAL_STATE, tools = TOOLSET3, func = update_records)-> Command[Literal["supervisor", "validator"]]:
    """
    Asynchronously updates sample metadata and updates the conversation state.

    Args:
        state (ConversationState): The current state of the conversation.
        tools (list): A list of tools to be used by the worker.
        func (callable): The function to be executed by the worker.

    Returns:
        Command[Literal["supervisor"]]: A command object with updated messages and resources, directing the flow to the supervisor.

    Raises:
        Exception: If any error occurs during the execution of the worker or invocation.
    """
    return await create_tool_call_node(state,tools,func,"archivist")

if __name__ == "__main__":
    # initial = HumanMessage(content="Please list the attributes of the MUS sample type.", name="user")
    initial = HumanMessage(content="Please update the records for the samples in the attached file.", name="user")

    # update_messages(INITIAL_STATE,initial)
    INITIAL_STATE.messages.append(initial)
    # asyncio.run(update_records())
    asyncio.run(archivist_node())
