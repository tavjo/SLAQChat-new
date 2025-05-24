import logging
import sys
import os
import time
import traceback

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from typing_extensions import Literal
from langgraph.types import Command
from src.chatbot.baml_client import b as baml
from src.chatbot.studio.models import ConversationState
from src.chatbot.studio.helpers import get_resource, update_resource, get_last_worker, convert_messages
from datetime import datetime, timezone
from langchain_core.messages import HumanMessage, AIMessage

from src.chatbot.studio.prompts import (
    INITIAL_STATE
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def query_parser_node(state: ConversationState = INITIAL_STATE) -> Command[Literal["conversationalist", "validator"]]:
    """
    Receives a user query and breaks it down into a list of queries.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["conversationalist", "validator"]]: A command object with updated messages, directing the flow to the next worker.

    Raises:
        Exception: If any error occurs during the parsing process.
    """
    goto = "validator"
    messages = state.messages
    last_worker = get_last_worker(state)
    try:
        logger.info("Creating payload for query parsing")

        # Find the most recent HumanMessage (user query) instead of assuming it's messages[0]
        most_recent_user_query = None
        most_recent_user_message = None
        most_recent_user_index = None
        
        for i, message in enumerate(reversed(messages)):  # Iterate from most recent to oldest
            if isinstance(message, HumanMessage):
                most_recent_user_query = message.content
                most_recent_user_message = message
                most_recent_user_index = len(messages) - 1 - i  # Convert back to original index
                break
        
        if most_recent_user_query is None:
            logger.error("No user query found in messages")
            raise ValueError("No HumanMessage found in conversation state")

        logger.info(f"Found most recent user query: {most_recent_user_query}")

        # Restructure messages list so that the most recent user query is at index 0
        if most_recent_user_index != 0:
            # Remove the most recent user message from its current position
            messages_copy = messages.copy()
            most_recent_message = messages_copy.pop(most_recent_user_index)
            # Insert it at the beginning
            restructured_messages = [most_recent_message] + messages_copy
            logger.info(f"Restructured messages list: moved user query from index {most_recent_user_index} to index 0")
        else:
            # Already at index 0, no restructuring needed
            restructured_messages = messages
            logger.info("Most recent user query already at index 0, no restructuring needed")
        
        # Update the state with restructured messages
        messages = restructured_messages

        payload = {
            # "system_message": messages[0].content,
            "user_query": messages[0].content,  # Now guaranteed to be the most recent user query
            "aggregatedMessages": convert_messages(messages),
            "resource": get_resource(state),
            "last_worker": last_worker
        }
        logger.debug("Payload created: %s", payload)
        
        logger.info("Parsing query...")
        start_time = time.time()
        try:
            response = baml.ParseQuery(context=payload)
            elapsed_time = time.time() - start_time
            logger.info(f"Query parsing completed in {elapsed_time:.2f} seconds")
        except Exception as parse_error:
            logger.error(f"Error during BAML query parsing: {str(parse_error)}")
            logger.debug(f"Parse error details: {traceback.format_exc()}")
            raise

        try:
            parsed_query = response.parsed_query.model_dump()
            logger.info(f"Parsed Query: {parsed_query}")
            logger.debug(f"Justification: {response.justification}")
            logger.debug(f"Explanation: {response.explanation}")
        except AttributeError as ae:
            logger.error(f"Invalid response format from BAML: {str(ae)}")
            logger.debug(f"Response structure: {response}")
            raise

        parsed_query_string = f"Parsed User Query: ```json\n{parsed_query}\n```\nJustification: {response.justification}\nExplanation: {response.explanation}"

        logger.info("Updating resources with parsed query")
        try:
            update_resource(state, {"parsed_query": parsed_query})
            logger.debug(f"Updated resources: {get_resource(state)}")
        except Exception as resource_error:
            logger.error(f"Error updating resources: {str(resource_error)}")
            logger.debug(f"Resource error details: {traceback.format_exc()}")
            raise

        # Merge the new message with the existing ones
        messages.append(AIMessage(content=parsed_query_string, name="query_parser"))
        state.version += 1
        state.timestamp = datetime.now(timezone.utc)
        goto = "conversationalist"
        logger.info(f"Query parsed successfully, proceeding to: {goto}")
        
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
        error_details = traceback.format_exc()
        logger.error(f"Error in query_parser_node: {str(e)}")
        logger.debug(f"Error details: {error_details}")
        
        # Create a user-friendly error message
        user_message = "I am sorry, I am unable to process your query at this time. Please try again later."
        # Add more specific information for common errors
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            user_message = "I'm having trouble connecting to the database. Please try again in a few moments."
        elif "invalid" in str(e).lower() or "format" in str(e).lower():
            user_message = "I had trouble understanding your query format. Could you please rephrase it?"
        
        messages.append(AIMessage(content=user_message, name="query_parser"))
        logger.info(f"Redirecting to {goto} due to error")
        
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
    # messages = [HumanMessage(content="Can you tell me more about the sample with UID PAV-220630FLY-1031?", name = "user")]
    messages = [HumanMessage(content = "Please list all samples with genotype 'RaDR+/+; GPT+/+' that are in cohort 'Water Study'.", name = "user")]
    # messages = [HumanMessage(content="What is the genotype for the mice with these UIDs: 'MUS-220124FOR-1' and 'MUS-220124FOR-73'?", name = "user")]
    # update_messages(INITIAL_STATE, messages[0])
    INITIAL_STATE.messages.extend(messages)
    query_parser_node()
