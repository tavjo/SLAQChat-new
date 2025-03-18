from langchain_core.messages import HumanMessage, AIMessage
import sys
import os
import time
import logging

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from typing_extensions import Literal
from langgraph.types import Command
from src.chatbot.baml_client import b as baml

from src.chatbot.studio.models import ConversationState, ResourceBox, ParsedQuery
from src.chatbot.studio.helpers import update_resource, get_resource, get_last_worker
from backend.Tools.services.schema_service import extract_relevant_schema
import asyncio
from datetime import datetime, timezone

from src.chatbot.studio.prompts import (
    INITIAL_STATE
)

# Configure logger for this module
logger = logging.getLogger(__name__)

async def schema_retriever_node(state: ConversationState = INITIAL_STATE) -> Command[Literal["multi_sample_info_retriever", "validator"]]:
    """
    Validates the current conversation state and updates the conversation flow.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["multi_sample_info_retriever", "validator"]]: A command object with updated messages, directing the flow to the next agent.

    Raises:
        Exception: If any error occurs during the schema retrieval process.
    """
    messages = state.messages
    goto = "validator"  # Default fallback in case of errors
    last_worker = get_last_worker(state)
    try:
        start_time = time.time()
        logger.info("Starting schema retrieval process")
        
        if len(messages) < 2:
            raise ValueError("Insufficient messages in conversation state")
            
        logger.debug(f"Message count: {len(messages)}")
        logger.debug(f"User query: {messages[1].content}")
        
        user_query = messages[1].content
        parsed_query = state.resources.parsed_query
        
        try:
            db_schema = await extract_relevant_schema()
            schema_extraction_time = time.time() - start_time
            logger.info(f"Schema extracted in {schema_extraction_time:.2f} seconds")
        except Exception as schema_error:
            logger.error(f"Failed to extract schema: {str(schema_error)}", exc_info=True)
            raise RuntimeError(f"Schema extraction failed: {str(schema_error)}") from schema_error
        
        logger.info("Invoking BAML schema retriever")
        baml_start_time = time.time()
        
        try:
            result = baml.RetrieveSchema(user_query, db_schema=db_schema, parsed_query=parsed_query)
            baml_execution_time = time.time() - baml_start_time
            logger.info(f"Schema retrieval completed in {baml_execution_time:.2f} seconds")
        except Exception as baml_error:
            logger.error(f"BAML schema retrieval failed: {str(baml_error)}", exc_info=True)
            raise RuntimeError(f"Schema retrieval failed: {str(baml_error)}") from baml_error
        
        if result and result is not None:
            logger.debug(f"Retrieval result: {result}")
            new_resource = {
                "db_schema": result.schema_map
            }
            update_resource(state, new_resource)
            
            relevant_keys_message = "The relevant database keys are: " + "\n".join(result.relevant_keys)
            updated_messages = [
                HumanMessage(content=user_query, name="user"), 
                AIMessage(content=relevant_keys_message, name="schema_mapper")
            ]
            messages.extend(updated_messages)
            goto = "multi_sample_info_retriever"
            
            total_time = time.time() - start_time
            logger.info(f"Schema mapping completed in {total_time:.2f} seconds")
            logger.debug(f"Updated resources: {state.resources}")
        else:
            logger.warning("Schema retriever returned empty or None result")
            messages.append(AIMessage(
                content="Could not identify relevant schema elements for this query.",
                name="schema_mapper"
            ))
        
        state.version += 1
        state.timestamp = datetime.now(timezone.utc)
        
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": get_resource(state),
                "last_worker": last_worker
            },
            goto=goto
        )
    except Exception as e:
        logger.error(f"Schema retriever node failed: {str(e)}", exc_info=True)
        error_message = f"An error occurred while mapping query to schema: {str(e)}"
        
        # Safely append the error message
        messages.append(AIMessage(content=error_message, name="schema_mapper"))
        
        state.version += 1
        state.timestamp = datetime.now(timezone.utc)
        
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": get_resource(state),
                "last_worker": last_worker
            },
            goto=goto
        )

# Example usage:
if __name__ == "__main__":
    initial_state: ConversationState = {
        "messages": [HumanMessage(content="What is the genotype for the mice with these UIDs: 'MUS-220124FOR-1' and 'MUS-220124FOR-73'?", name = "user"),
                     AIMessage(content="""Parsed User Query: ```json{'uid': ['MUS-220124FOR-1', 'MUS-220124FOR-73'], 'sampletype': 'mouse', 'assay': None, 'attribute': 'genotype', 'terms': None}```Justification: The query explicitly mentions UIDs, which are identifiers for specific samples, in this case, mice. The user is interested in the 'genotype' attribute of these samples, as indicated by the phrase 'What is the genotype'. The sample type is inferred to be 'mouse' based on the context of the UIDs and the mention of 'mice'. Explanation: The user query is asking for the genotype of specific mice identified by their UIDs. The UIDs provided are 'MUS-220124FOR-1' and 'MUS-220124FOR-73'. The query is focused on the 'genotype' attribute of these mice.""", name="query_parser")
                     
            # HumanMessage(content="Retrieve UIDs of all samples of this genotype: 'RaDR+/+; GPT+/+; Aag -/-'", name = "user")
            # HumanMessage(content="Can you please list all the samples associated with the following scientist: 'Patricia Grace'?", name = "user")
        ],
    "resources": ResourceBox(
        parsed_query= ParsedQuery.model_validate({'uid': ['MUS-220124FOR-1', 'MUS-220124FOR-73'], 'sampletype': 'mouse', 'assay': None, 'attribute': 'genotype', 'terms': None})
    )
    }
    INITIAL_STATE.messages.extend(initial_state["messages"])
    INITIAL_STATE.resources = initial_state["resources"]
    asyncio.run(schema_retriever_node())