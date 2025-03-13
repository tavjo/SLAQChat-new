# src/chatbot/studio/helpers.py
# import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.chatbot.studio.models import ResourceBox, WorkerState, ConversationState, ParsedQuery, DBSchema, Metadata, SampleTypeAttributes, Table, Column, ToolMetadata, ToolResponse
from langchain_core.messages import BaseMessage, SystemMessage
import time
from backend.Tools.services.module_to_json import functions_to_json
from backend.Tools.services.helpers import timer_wrap
import logging
from langgraph.types import Command
from typing_extensions import Literal
from datetime import datetime, timezone
from langchain_core.messages import HumanMessage
from backend.Tools.schemas import UpdatePipelineMetadata
logger = logging.getLogger(__name__)

########################################################
# Helper functions for state management
########################################################

# Example: A default empty resources function if needed.
def default_resource_box() -> ResourceBox:
    from src.chatbot.studio.models import ResourceBox, SampleTypeAttributes
    return ResourceBox(
        sample_metadata=None,
        protocolURL=None,
        sampleURL=None,
        UIDs=None,
        db_schema=None,
        parsed_query=ParsedQuery(uid=[], sampletype=[], assay=[], attribute=[], terms=[]),
        st_attributes=[SampleTypeAttributes(sampletype="", st_description="", attributes=[])],
        update_info=UpdatePipelineMetadata(success=False, logs=[], errors=None, stats={})
    )

def populate_update_info(update_info: dict) -> UpdatePipelineMetadata:
    return UpdatePipelineMetadata.model_validate(update_info)

def populate_toolbox(toolset: list[str]) -> dict[str, ToolMetadata]:
    from src.chatbot.studio.models import ToolMetadata
    toolbox_info = functions_to_json(toolset)
    # print(f"Toolbox info: {toolbox_info}")
    toolbox = {}
    for toolname, toolmetadata in toolbox_info.items():
        toolbox[toolname] = ToolMetadata.model_validate(toolmetadata)
    return toolbox

def populate_sample_metadata(sample_metadata: dict) -> Metadata:
    return Metadata.model_validate(sample_metadata)

def populate_db_schema(db_schema: dict) -> DBSchema:
    tables = []
    for table in db_schema:
        table_components = {
            "name": table["name"],
            "columns": [Column.model_validate(column) for column in table["columns"]]
        }
        tables.append(Table.model_validate(table_components))
    return DBSchema.model_validate({"tables": tables})

def populate_sample_type_attributes(sample_type_attributes: dict) -> SampleTypeAttributes:
    return SampleTypeAttributes.model_validate(sample_type_attributes)

def populate_parsed_query(parsed_query: dict|ParsedQuery) -> ParsedQuery:
    parsedquerydict = ParsedQuery.model_dump()
    if isinstance(parsed_query, ParsedQuery):
        parsed_query_dict = parsed_query.model_dump()
    else:
        parsed_query_dict = parsed_query
    
    # Update only fields that exist in the model
    for key, value in parsedquerydict.items():
        if key in parsed_query_dict:
            logger.debug(f"Updating resource field: {key}")
            parsed_query_dict[key] = value
        else:
            logger.warning(f"Ignoring unknown resource field: {key}")
    return ParsedQuery.model_validate(parsed_query_dict)

def get_resource(state: ConversationState) -> ResourceBox:    
    # If resources don't exist or are None, return default ResourceBox
    if state.resources is None:
        return default_resource_box()
    
    # Return the ResourceBox instance directly since it's already a valid Pydantic model
    return state.resources

# Helper function to update the resource information.
def update_resource(state: ConversationState, new_resource: dict) -> None:
    from src.chatbot.studio.models import ResourceBox
    """
    Merge new resource data into the state's resources.
    Fields from new_resource that are explicitly provided will overwrite the existing ones,
    including empty values (empty lists, empty strings).
    """
    logger = logging.getLogger(__name__)
    
    try:
        if state.resources is None:
            logger.info("No existing resources found, initializing default ResourceBox")
            state.resources = default_resource_box()
        
        new_resource_dict = {}
        # Convert to dictionary for easier manipulation
        try:
            if "parsed_query" in new_resource:
                logger.debug(f"Processing parsed_query: {new_resource['parsed_query']}")
                new_resource_dict["parsed_query"] = populate_parsed_query(new_resource["parsed_query"])
            elif "sample_metadata" in new_resource:
                logger.debug(f"Processing sample_metadata")
                if isinstance(new_resource["sample_metadata"], dict):
                    new_resource_dict["sample_metadata"] = populate_sample_metadata(new_resource["sample_metadata"])
                elif isinstance(new_resource["sample_metadata"], list):
                    new_resource_dict["sample_metadata"] = [populate_sample_metadata(i) for i in new_resource["sample_metadata"]]
            elif "db_schema" in new_resource:
                logger.debug(f"Processing db_schema")
                new_resource_dict["db_schema"] = populate_db_schema(new_resource["db_schema"])
            elif "st_attributes" in new_resource:
                logger.debug(f"Processing st_attributes")
                new_resource_dict["st_attributes"] = populate_sample_type_attributes(new_resource["st_attributes"])
            elif "update_info" in new_resource:
                logger.debug(f"Processing update_info")
                new_resource_dict["update_info"] = populate_update_info(new_resource["update_info"])
            else:
                logger.debug(f"Using raw new_resource: {list(new_resource.keys())}")
                new_resource_dict = new_resource
        except Exception as e:
            logger.error(f"Error populating resource data: {e}", exc_info=True)
            raise ValueError(f"Failed to process resource data: {str(e)}")
        
        # Get current resources as dictionary that we can update
        try:
            current_resources = state.resources.model_dump()
            
            # Update only fields that exist in the model
            for key, value in new_resource_dict.items():
                if key in current_resources:
                    logger.debug(f"Updating resource field: {key}")
                    current_resources[key] = value
                else:
                    logger.warning(f"Ignoring unknown resource field: {key}")
            
            # Create updated ResourceBox from the modified dictionary
            state.resources = ResourceBox.model_validate(current_resources)
            logger.info("Successfully updated resources")
        except Exception as e:
            logger.error(f"Error updating resource object: {e}", exc_info=True)
            raise ValueError(f"Failed to update resources: {str(e)}")
            
    except Exception as e:
        logger.error(f"Unexpected error in update_resource: {e}", exc_info=True)
        # Re-raise the exception after logging it
        raise

def update_available_workers(state: ConversationState, new_workers: list[WorkerState] | list[dict]) -> None:
    """
    Updates the available workers in the conversation state.
    
    Args:
        state (ConversationState): The current conversation state.
        new_workers (list): A list of WorkerState objects or dictionaries.
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Check if the list contains dictionaries by examining the first item
        if new_workers and isinstance(new_workers[0], dict):
            logger.debug(f"Converting worker dictionaries to WorkerState objects")
            new_workers = [WorkerState.model_validate(worker) for worker in new_workers]
        
        state.available_workers = new_workers
        logger.debug(f"Updated available workers: {[w.agent for w in state.available_workers] if state.available_workers else 'None'}")
    except Exception as e:
        logger.error(f"Error updating available workers: {str(e)}")
        # Keep existing workers if there's an error
        logger.debug(f"Keeping existing workers: {[w.agent for w in state.available_workers] if state.available_workers else 'None'}")


def get_available_workers(state: ConversationState) -> list[WorkerState]:
    # get available workers from the state
    if not state.available_workers:
        return None
    else:
        return state.available_workers

# Helper function to retrieve the current resources.

def get_messages(state: ConversationState) -> list[BaseMessage]:
    return state.messages

def update_messages(state: ConversationState, new_messages: list[BaseMessage]) -> None:
    if state.messages[0].name == "system" and len(state.messages) == 1:
        state.messages.append(new_messages)
    else:
        new = [SystemMessage(content=state.messages[0].content, name="system")] + new_messages
        state.messages.append(new)

def default_tool_response() -> ToolResponse:
    return ToolResponse(result=default_resource_box(), justification=None, explanation=None, response=None, agent=None)

########################################################
# Helper functions for tool calling with BAML client
########################################################

# Handles calls to BAML Navigator which chooses the next tool and provides the tool arguments
# It provides a faster alternative to LangChain and LangGraph's tool calling functions

@timer_wrap
async def async_navigator_handler(
    agent: WorkerState,
    state: ConversationState
):
    # from src.chatbot.studio.models import WorkerState, ConversationState
    from src.chatbot.baml_client.async_client import b
    from src.chatbot.baml_client import b as baml
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
        if state.resources is None:
            state.resources = default_resource_box()
        logger.info(f"State messages: {state.messages}")
        
        # print(f" State messages: {state.messages}")

        logger.info("Creating payload...")

        messages = state.messages

        payload = {
        "system_message": SYSTEM_MESSAGE,
        "user_query": messages[1].content,
        "aggregatedMessages": [msg.content for msg in messages],
        "resource": state.resources if state.resources else default_resource_box()
        }
        logger.info("Payload created.")
        logger.info(f"Payload: {payload}")
        # logger.info(f" Payload messages: {payload['aggregatedMessages']}")
        # Call the BAML Navigate function asynchronously.
        # start_time = time.time()
        logger.info("Calling BAML Navigator function...")
        
        # try:
            # Try the current method first
        nav_stream = b.stream.Navigate(agent, payload)
        nav_response = await nav_stream.get_final_response()
        # except AttributeError as e:
        #     if "Collector" in str(e):
        #         # Try alternative method if Collector is missing
        #         logger.info("Using alternative method due to missing Collector")
        #         nav_response = baml.Navigate(agent, payload)
        #     else:
        #         # Re-raise if it's a different attribute error
        #         raise
        
        if nav_response:
            # Extract the tool choice and its argument.
            next_tool = nav_response.next_tool
            # print(f"Next tool: {next_tool}\n Justification: {nav_response.justification}")
            tool_args = nav_response.tool_args
            logger.info(f"Navigation completed.") #in {time.time() - start_time:.2f} seconds.")
            return next_tool, tool_args, nav_response.justification, nav_response.explanation
        else:
            logger.error("No navigation response received")
            raise ValueError("No navigation response received")
    except Exception as e:
        # Log the exception or handle it as needed
        logger.error(f"An error occurred during navigation: {e}")
        raise


# Helper function to create a worker for tool calling
# @timer_wrap
async def create_worker(tools, func):
    """
    Creates a LangGraph worker for tool calling functionality.
    
    This function builds a state graph that manages the interaction between 
    an agent and available tools. The graph enables tool selection, execution, 
    and response handling in a structured workflow.
    
    Parameters:
        tools (list): A list of tools to be made available to the worker.
        func (callable): An async function that processes the conversation state
                         and returns a response.
                         
    Returns:
        compiled_graph: A compiled LangGraph that can be executed to process inputs.
        
    Raises:
        ValueError: If there are issues with the tools or function parameters.
        Exception: If graph creation or compilation fails.
    """
    try:
        from src.chatbot.studio.models import ConversationState
        from langchain_core.messages import HumanMessage
        from langgraph.graph import StateGraph
        from langgraph.prebuilt import tools_condition, ToolNode

        async def chatbot(state: ConversationState):
            """
            Inner function that processes the conversation state using the provided function.
            
            This function executes the main processing logic, handles the response,
            and formats it appropriately for the graph workflow.
            
            Parameters:
                state (ConversationState): The current conversation state.
                
            Returns:
                dict: Updated state with new messages and possibly updated resources.
                
            Raises:
                Exception: If function execution or response handling fails.
            """
            logger.info(f"Calling {func.__name__}...")
            try:
                response = await func(state)
                logger.info(f"{func.__name__} completed.")
                
                if response is None:
                    logger.error("Function returned None response")
                    return {"messages": [HumanMessage(content="An error occurred: No response was generated.")]}
                
                if response.result:
                    logger.info(f"Creating messages...")
                    try:
                        messages = f"{response.response or ''}\n{response.justification or ''}\n{response.explanation or ''}"
                        messages = messages.strip()  # Remove leading/trailing whitespace
                        logger.info(f"Messages created: {messages}")
                        return {
                            "messages": [HumanMessage(content=messages)],
                            'resources': response.result
                        }
                    except Exception as e:
                        logger.error(f"Error creating message content: {e}", exc_info=True)
                        return {"messages": [HumanMessage(content=f"Error formatting response: {str(e)}")]}
                else:
                    logger.debug(f"No result in response")
                    error_message = response.response or "Error retrieving data."
                    return {"messages": [HumanMessage(content=error_message)]}
            except Exception as e:
                logger.error(f"Error executing {func.__name__}: {e}", exc_info=True)
                return {"messages": [HumanMessage(content=f"An error occurred while processing: {str(e)}")]}

        # Create and configure the graph
        if not tools:
            raise ValueError("No tools provided for worker creation")
        
        if not callable(func):
            raise ValueError("Function parameter must be callable")
            
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
    except ImportError as e:
        logger.error(f"Missing required dependency: {e}", exc_info=True)
        raise ValueError(f"Failed to create worker due to missing dependency: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to create worker: {e}", exc_info=True)
        raise ValueError(f"Worker creation failed: {str(e)}")

async def create_tool_call_node(state: ConversationState,tools: list[callable], func: callable, agent: str) -> Command[Literal["supervisor", "validator"]]:
    try:
        agent = agent
        messages = state.messages
        start_time = time.time()
        logger.info("Creating worker...")
        worker = await create_worker(tools,func)
        logger.info(f"Worker created in {time.time() - start_time:.2f} seconds.")

        start_time = time.time()
        logger.info(f"Invoking {agent}...")
        res = await worker.ainvoke(state)
        logger.info(f"Invocation completed in {time.time() - start_time:.2f} seconds.")
        logger.info(f"Result: {res}")

        logger.info("Adding new messages to state...")
        messages.append(res["messages"][-1])
        logger.info(f"Updated messages: {messages}")
        # Check if resources were updated
        # logger.info(f"Updating Resources...")   
        # if state.resources == res["resources"]:
        #     logger.info(f"State resources: {state.resources}")
        # elif state.resources != res["resources"]:
        #     update_resource(state, )
        #     logger.info(f"Updated resources: {state.resources}")
        # elif not state.resources and not res["resources"]:
        #     logger.warning("No resources to update")
        state.version += 1
        state.timestamp = datetime.now(timezone.utc)
        logger.info(f"{agent} work completed. Returning command to supervisor...")
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": state.resources if state.resources else default_resource_box()
            },
            goto="supervisor",
        )
    except Exception as e:
        error_msg = f"An error occurred at {agent} node: {e}"
        messages.append(HumanMessage(content=error_msg, name=agent))
        logger.error(f"{error_msg}\n{messages}")
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": state.resources if state.resources else default_resource_box()
            },
            goto="validator",
        )


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