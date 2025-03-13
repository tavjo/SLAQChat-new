import logging
from langchain_core.messages import HumanMessage, SystemMessage
import sys
import os
import time
import traceback

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from typing_extensions import Literal
from langgraph.types import Command
from src.chatbot.studio.models import ConversationState
from src.chatbot.studio.helpers import get_resource, default_resource_box, get_available_workers, update_available_workers, update_messages

from src.chatbot.studio.prompts import (
    WORK_GROUP_A,
    INITIAL_STATE
)
from datetime import datetime, timezone

# Configure logging
logger = logging.getLogger(__name__)

from src.chatbot.baml_client import b as baml

def supervisor_node(state: ConversationState = INITIAL_STATE) -> Command[Literal["basic_sample_info_retriever","archivist","schema_retriever","multi_sample_info_retriever", "responder", "validator"]]:
    """
    Supervises the current conversation state to determine the next worker and update the conversation flow.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["basic_sample_info_retriever","archivist","schema_retriever","multi_sample_info_retriever", "responder", "validator"]]: A command object with updated messages, resources, and available workers, directing the flow to the next worker.

    Raises:
        Exception: If any error occurs during the supervision process.
    """
    try:
        messages = state.messages
        # if "resources" not in state or state.resources is None:
        #     state.resources = default_resource_box()
        logger.info("Setting available workers...")
        if not state.available_workers:
            state.available_workers = WORK_GROUP_A
            logger.debug(f"Initialized available workers: {WORK_GROUP_A}")

        logger.info("Creating payload for supervision...")
        try:
            payload = {
                "system_message": messages[0].content,
                "user_query": messages[1].content,
                "aggregatedMessages": [msg.content for msg in messages],
                "resource": state.resources if state.resources else default_resource_box()
            }
            logger.debug("Payload created successfully")
        except IndexError as e:
            logger.error(f"Failed to create payload - message index error: {str(e)}")
            raise
        
        logger.info("Getting available workers...")
        available_workers = get_available_workers(state)
        logger.debug(f"Available workers: {[w.agent for w in available_workers]}")

        start_time = time.time()
        logger.info("Supervising conversation...")
        try:
            response = baml.Supervise(payload, available_workers)
            elapsed_time = time.time() - start_time
            logger.info(f"Supervision completed in {elapsed_time:.2f} seconds")
        except Exception as e:
            logger.error(f"BAML Supervision failed: {str(e)}")
            raise

        goto = response.Next_worker.agent
        logger.info(f"Next Worker: {goto}")
        logger.debug(f"Justification: {response.justification}")

        available_workers = [i for i in available_workers if i.agent != goto]
        update_available_workers(state, available_workers)
        
        if goto == "responder":
            logger.debug("Adding responder messages")
            updated_messages = [HumanMessage(content=response.justification, name="supervisor")] + [HumanMessage(content=messages[-1].content, name="supervisor")]
            messages.extend(updated_messages)
        else:
            logger.debug("Adding supervisor justification message")
            messages.append(HumanMessage(content=response.justification, name="supervisor"))
        
        if goto == "multi_sample_info_retriever":
            logger.info("Redirecting from multi_sample_info_retriever to schema_retriever")
            goto = "schema_retriever"
            
        logger.debug(f"Remaining Available Workers: {[w.agent for w in state.available_workers]}")

        # Update state metadata
        state.version += 1
        state.timestamp = datetime.now(timezone.utc)
        logger.info(f"Routing to {goto} worker with updated state (version {state.version})")
        
        return Command(
            update={
                "messages": messages,
                "available_workers": state.available_workers,
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": state.resources if state.resources else default_resource_box()
            },
            goto=goto
        )
    except Exception as e:
        error_details = traceback.format_exc()
        error_message = f"I am sorry, I am unable to retrieve the information. Please try again later. You can visit the website for more information."
        logger.error(f"Supervisor error: {str(e)}\n{error_details}")
        
        try:
            messages.append(HumanMessage(content=error_message, name="supervisor"))
            state.version += 1
            state.timestamp = datetime.now(timezone.utc)
        except Exception as nested_e:
            logger.critical(f"Failed to append error message: {str(nested_e)}")
        
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": datetime.now(timezone.utc),
                "resources": state.resources if state.resources else default_resource_box()
            },
            goto="validator"
        )


# Example usage:
if __name__ == "__main__":
    initial_state: ConversationState = {
        "messages": [
        # HumanMessage(content="Can you please list all the samples associated with the following scientist: 'Patricia Grace'?", name='user'),
        HumanMessage(content="What is the genotype for the mice with these UIDs: 'MUS-220124FOR-1' and 'MUS-220124FOR-73'?", name = 'user'),
        HumanMessage(content="Parsed User Query: ```json{'uid': ['MUS-220124FOR-1', 'MUS-220124FOR-73'], 'sampletype': 'mouse', 'assay': None, 'attribute': 'genotype', 'terms': None}```Justification: The query explicitly mentions UIDs, which are identifiers for specific samples, in this case, mice. The user is interested in the 'genotype' attribute of these samples, as indicated by the phrase 'What is the genotype'. The sample type is inferred to be 'mouse' based on the context of the UIDs and the mention of 'mice'. Explanation: The user query is asking for the genotype of specific mice identified by their UIDs. The UIDs provided are 'MUS-220124FOR-1' and 'MUS-220124FOR-73'. The query is focused on the 'genotype' attribute of these mice.", name = "query_parser")
        ],
        # HumanMessage(content='Scientist', name='schema_mapper')],
    }
    # update_messages(INITIAL_STATE, initial_state["messages"])
    # update_resource(INITIAL_STATE, initial_state["resources"])
    INITIAL_STATE.messages.extend(initial_state["messages"])
    supervisor_node()