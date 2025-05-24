# src/chatbot/studio/helpers.py
# import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.chatbot.studio.models import ResourceBox, WorkerState, ConversationState, ParsedQuery, DBSchema, Metadata, SampleTypeAttributes, Table, Column, ToolMetadata, ToolResponse, Message
from langchain_core.messages import BaseMessage, SystemMessage
import time
from backend.Tools.services.module_to_json import functions_to_json
from backend.Tools.services.helpers import timer_wrap
import logging
from langgraph.types import Command
from typing_extensions import Literal
from datetime import datetime, timezone
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from backend.Tools.schemas import UpdatePipelineMetadata
# from copy import deepcopy
import uuid
from typing import Optional, Union
from datetime import datetime, timezone

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
# sys.path.append(project_root)

# Ensure the logs directory exists before setting up FileHandler
logs_dir_path = os.path.join(project_root, 'logs')
os.makedirs(logs_dir_path, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(logs_dir_path, 'helpers.log'), 'a')
    ]
)
logger = logging.getLogger(__name__)

########################################################
# Helper functions for state management
########################################################

def convert_messages(messages: list[BaseMessage]) -> list[Message]:
    return [
        Message(
            name=m.name if m.name else "user",
            message=m.content,
            role=m.type if m.type else "user"
        )
        for m in messages
    ]

def get_last_worker(state: ConversationState) -> str:
    messages = state.messages
    # version = state.version
    last_worker = f"{messages[-1].name}"
    state.last_worker = last_worker
    return state.last_worker

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

def transform_response_to_metadata(response_data) -> list[Metadata]:
    result = []
    
    # Handle the outer list structure
    for item in response_data:
        # Each item is a dictionary with UIDs as keys
        for uid, metadata_dict in item.items():
            # Create a Metadata object from each inner dictionary
            metadata_obj = Metadata.model_validate(metadata_dict)
            result.append(metadata_obj)
    
    return result

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
    """
    Convert the database schema to a DBSchema Pydantic model.
    
    Args:
        db_schema: Dictionary or Pydantic model containing database schema information
        
    Returns:
        DBSchema: A validated Pydantic model of the database schema
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Ensure db_schema is properly formatted
        if not db_schema:
            logger.warning("Empty db_schema provided")
            return DBSchema.model_validate({"tables": []})
            
        # Handle both list and dict formats
        if isinstance(db_schema, dict) and "tables" in db_schema:
            logger.debug("Processing db_schema in dictionary format with 'tables' key")
            tables_data = db_schema["tables"]
        elif isinstance(db_schema, list):
            logger.debug("Processing db_schema as direct list of tables")
            tables_data = db_schema
        else:
            logger.debug("Converting db_schema to dict")
            tables_data = db_schema.model_dump()["tables"]
            
        if not isinstance(tables_data, list):
            logger.error(f"Expected list of tables, got {type(tables_data)}: {tables_data}")
            raise TypeError(f"Tables data must be a list, got {type(tables_data)}")
        
        tables = []
        for i, table in enumerate(tables_data):
            try:
                if not isinstance(table, dict):
                    logger.error(f"Table at index {i} is not a dict: {type(table)}")
                    raise TypeError(f"Each table must be a dict, got {type(table)}")
                
                # Ensure required keys exist
                if "name" not in table:
                    logger.error(f"Missing 'name' key in table at index {i}")
                    raise KeyError(f"Missing 'name' key in table at index {i}")
                if "columns" not in table:
                    logger.error(f"Missing 'columns' key in table {table['name']}")
                    raise KeyError(f"Missing 'columns' key in table {table['name']}")
                
                table_components = {
                    "name": table["name"],
                    "columns": [Column.model_validate(column) for column in table["columns"]]
                }
                tables.append(Table.model_validate(table_components))
            except (TypeError, KeyError) as e:
                logger.error(f"Error processing table {i}: {e}", exc_info=True)
                raise
            except Exception as e:
                logger.error(f"Unexpected error processing table {i}: {e}", exc_info=True)
                raise ValueError(f"Failed to process table at index {i}: {str(e)}")
        
        return DBSchema.model_validate({"tables": tables})
        
    except Exception as e:
        logger.error(f"Failed to populate db_schema: {e}", exc_info=True)
        raise ValueError(f"Failed to populate database schema: {str(e)}")

def populate_sample_type_attributes(sample_type_attributes: dict) -> SampleTypeAttributes:
    return SampleTypeAttributes.model_validate(sample_type_attributes)

def populate_parsed_query(parsed_query: dict|ParsedQuery) -> ParsedQuery:
    # parsedquerydict = ParsedQuery.model_dump()
    if isinstance(parsed_query, ParsedQuery):
        parsed_query_dict = parsed_query.model_dump()
    else:
        parsed_query_dict = parsed_query
    
    # Update only fields that exist in the model
    # for key, value in parsedquerydict.items():
    #     if key in parsed_query_dict:
    #         logger.debug(f"Updating resource field: {key}")
    #         parsed_query_dict[key] = value
    #     else:
    #         logger.warning(f"Ignoring unknown resource field: {key}")
    return ParsedQuery.model_validate(parsed_query_dict)

def get_resource(state: ConversationState) -> ResourceBox:    
    # If resources don't exist or are None, return default ResourceBox
    if state.resources is None:
        return default_resource_box()
    
    # Return the ResourceBox instance directly since it's already a valid Pydantic model
    return state.resources

# Helper function to update the resource information.
def update_resource(state: ConversationState, new_resource: Union[dict, list[dict]]) -> None:
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
                if isinstance(new_resource["st_attributes"], list) and len(new_resource["st_attributes"]) > 0:
                    new_resource_dict["st_attributes"] = [populate_sample_type_attributes(i.model_dump()) for i in new_resource["st_attributes"]]
                else:
                    new_resource_dict["st_attributes"] = populate_sample_type_attributes(new_resource["st_attributes"].model_dump())
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
    # from src.chatbot.studio.prompts import SYSTEM_MESSAGE

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
        last_worker = get_last_worker(state)

        payload = {
        # "system_message": messages[0].content,
        "user_query": messages[0].content,
        "aggregatedMessages": convert_messages(messages),
        "resource": get_resource(state),
        "last_worker": last_worker
        }
        logger.info("Payload created.")
        logger.info(f"Payload: {payload}")
        # logger.info(f" Payload messages: {payload['aggregatedMessages']}")
        logger.info("Calling BAML Navigator function...")
    
        nav_stream = b.stream.Navigate(agent, payload)
        nav_response = await nav_stream.get_final_response()
        
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
        from langchain_core.messages import AIMessage
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
                    return {"messages": [AIMessage(content="An error occurred: No response was generated.")]}
                
                if response.result:
                    logger.info(f"Creating messages...")
                    try:
                        messages = f"{response.response or ''}\n{response.justification or ''}\n{response.explanation or ''}"
                        messages = messages.strip()  # Remove leading/trailing whitespace
                        logger.info(f"Messages created: {messages}")
                        return {
                            "messages": [AIMessage(content=messages)],
                            'resources': response.result
                        }
                    except Exception as e:
                        logger.error(f"Error creating message content: {e}", exc_info=True)
                        return {"messages": [AIMessage(content=f"Error formatting response: {str(e)}")]}
                else:
                    logger.debug(f"No result in response")
                    error_message = response.response or "Error retrieving data."
                    return {"messages": [AIMessage(content=error_message)]}
            except Exception as e:
                logger.error(f"Error executing {func.__name__}: {e}", exc_info=True)
                return {"messages": [AIMessage(content=f"An error occurred while processing: {str(e)}")]}

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
    agent = agent
    messages = state.messages
    last_worker = get_last_worker(state)
    try:
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
        messages.append(AIMessage(content=res["messages"][-1].content, name=agent))
        logger.info(f"Updated messages: {messages}")
        state.version += 1
        state.timestamp = datetime.now(timezone.utc)
        logger.info(f"{agent} work completed. Returning command to supervisor...")
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": get_resource(state),
                "last_worker": last_worker
            },
            goto="supervisor",
        )
    except Exception as e:
        error_msg = f"An error occurred at {agent} node: {e}"
        messages.append(AIMessage(content=error_msg, name=agent))
        logger.error(f"{error_msg}\n{messages}")
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": get_resource(state),
                "last_worker": last_worker
            },
            goto="validator",
        )

########################################################
# Helper functions for memory management
########################################################

def flatten_user_queries(state: ConversationState, session_id: str, timestamp: datetime) -> ConversationState:
    """
    Flatten multiple user messages into a single message in the conversation state.
    
    Args:
        state (ConversationState): The current conversation state containing messages
        session_id (str): The unique session identifier
        timestamp (datetime): The timestamp for the new flattened message
    
    Returns:
        ConversationState: Updated state with flattened user messages
        
    Raises:
        ValueError: If state or messages are invalid
        TypeError: If timestamp is not a datetime object
    """
    try:
        logger.info(f"Flattening user queries for session {session_id}")
        
        if not state or not hasattr(state, 'messages'):
            raise ValueError("Invalid conversation state provided")
            
        # Get messages from state
        messages = state.messages
        logger.debug(f"Processing {len(messages)} messages")
        
        # Create dict of user messages with id as key
        user_messages = {msg.id: msg for msg in messages if msg.name.lower() == "user"}
        logger.debug(f"Found {len(user_messages)} user messages to flatten")
        
        if not user_messages:
            logger.warning("No user messages found to flatten")
            return state
            
        # Sort user messages by timestamp
        try:
            sorted_user_messages = sorted(user_messages.values(), 
                                          key=lambda x: datetime.fromisoformat(x.id.split("_")[0]))
        except Exception as e:
            logger.error(f"Error sorting messages: {str(e)}")
            # Fall back to unsorted messages if sorting fails
            sorted_user_messages = list(user_messages.values())
        
        # Concatenate content of sorted user messages
        flattened_user_query = "; ".join([f"{msg.content} (id: {msg.id})" for msg in sorted_user_messages])
        logger.debug(f"Created flattened query: {flattened_user_query[:100]}...")
        
        # Remove old user messages from state except for most recent one
        for msgid, msg in user_messages.items():
            if msgid != sorted_user_messages[-1].id:
                messages.remove(msg)
        
        # Add new user message to state
        new_msg_id = f"{timestamp.isoformat()}_{session_id}"
        messages.append(HumanMessage(content=flattened_user_query, name="user", id=new_msg_id))
        logger.info(f"Successfully flattened {len(sorted_user_messages)} messages into one with ID {new_msg_id}")
        logger.info(f"Updated messages: {messages}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in flatten_user_queries: {str(e)}", exc_info=True)
        # Return original state in case of error to prevent data loss
        return state

def handle_user_queries(user_query: str, state: ConversationState) -> Optional[ConversationState]:
    """
    Process a new user query and integrate it into the conversation state.
    
    This function creates a new session ID, timestamps the query, adds it to the state,
    and flattens multiple queries if needed.
    
    Args:
        user_query (str): The text of the user's message
        state (ConversationState): The current conversation state
        
    Returns:
        ConversationState: A new conversation state with the user query integrated
        
    Raises:
        ValueError: If empty query is provided
        TypeError: If state is not a valid ConversationState
    """
    try:
        if not user_query or not user_query.strip():
            logger.warning("Empty user query received")
            raise ValueError("User query cannot be empty")
            
        logger.info("Processing new user query")
        logger.debug(f"Query content: {user_query[:10]}...")
        
        # Create a deep copy to avoid modifying the original state
        # fresh_state = deepcopy(state)
        
        # Generate a unique session ID and get current timestamp
        session_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        logger.debug(f"Created session ID: {session_id}")
        fresh_state = ConversationState(
            messages = state.messages,
            version = 1,
            timestamp = timestamp,
            session_id = session_id,
            last_worker = "system"
        )
        logger.info("Fresh state created.")
        # Create and add the user message
        msg_id = f"{timestamp.isoformat()}_{session_id}"
        user_message = HumanMessage(content=user_query, name="user", id=msg_id)
        fresh_state.messages.append(user_message)
        
        # Check if we need to flatten multiple user messages
        user_message_count = len([i for i in fresh_state.messages if i.name.lower() == "user"])
        logger.debug(f"Total user messages after adding new one: {user_message_count}")
        
        if user_message_count > 1:
            logger.info("Multiple user messages detected, flattening")
            fresh_state = flatten_user_queries(fresh_state, session_id, timestamp)
        
        # Update session metadata
        # fresh_state.session_id = session_id
        # fresh_state.timestamp = timestamp
        logger.info(f"Successfully processed user query with session ID {session_id}")
        
        return fresh_state
        
    except Exception as e:
        logger.error(f"Error in handle_user_queries: {str(e)}", exc_info=True)
        # Return None to indicate error, caller should handle this case
        return None

def initialize_logging(log_file: str, project_root: str = project_root):
    # Configure logging
    os.makedirs(os.path.join(project_root, 'logs'), exist_ok=True)

    # Set up logging configuration
    log_filename = log_file.split(".")[0]
    log_file = os.path.join(project_root, 'logs', f"{log_filename}.log")
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized for {log_file}")
    return logger


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