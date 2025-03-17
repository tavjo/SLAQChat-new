from langchain_core.messages import HumanMessage, AIMessage
import sys
import os
import time
import logging
import traceback

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from typing_extensions import Literal
from langgraph.types import Command
from src.chatbot.baml_client import b as baml
from src.chatbot.studio.models import ConversationState
from src.chatbot.studio.helpers import get_resource, update_resource

from src.chatbot.studio.prompts import (
    INITIAL_STATE
)
from datetime import datetime, timezone

# Configure logger
logger = logging.getLogger(__name__)

def conversationalist_node(state: ConversationState) -> Command[Literal["supervisor", "validator", "FINISH"]]:
    """
    Either responds directly to the user or directs the flow to the supervisor.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["validator","FINISH","supervisor"]]: A command object with updated messages, directing the flow to the next agent.

    Raises:
        Exception: If any error occurs during the conversation.
    """
    goto = "validator"
    messages = state.messages
    try:
        payload = {
            "system_message": messages[0].content,
            "user_query": messages[1].content,
            "aggregatedMessages": [msg.content for msg in messages],
            "resource": get_resource(state)
        }

        # parsed_query = payload["resource"].parsed_query
        
        start_time = time.time()
        logger.info("Obtaining response from Conversationalist...")
        
        try:
            response = baml.Conversationalist(payload)
            logger.info(f"Response obtained in {time.time() - start_time:.2f} seconds.")
        except Exception as baml_error:
            logger.error(f"Error calling BAML Conversationalist: {baml_error}", exc_info=True)
            raise RuntimeError(f"Failed to get response from BAML: {str(baml_error)}")

        logger.debug(f"Agent: {response.name}\nJustification: {response.justification}")
        
        if response.retrieve_info:
            goto = "supervisor"
            new_aggregate = response.user_query
            messages.append(HumanMessage(content=new_aggregate, name="user"))
            logger.info("Routing to supervisor for information retrieval")
        else:
            goto = "FINISH"
            new_aggregate = response.response
            messages.append(AIMessage(content=new_aggregate, name=response.name))
            logger.info("Conversation complete, finishing flow") 
        
        logger.debug(f"Next step: {goto}")
        state.version += 1
        state.timestamp = datetime.now(timezone.utc)
        
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": get_resource(state)
            },
            goto=goto
        )
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"An error occurred in conversationalist_node: {e}\n{error_trace}")
        
        # Ensure we have a valid goto even in case of error
        if not goto:
            goto = "validator"
            
        error_message = f"An error occurred in conversationalist_node: {str(e)}"
        
        try:
            messages.append(AIMessage(content=error_message))
        except Exception as msg_error:
            logger.error(f"Failed to append error message to state: {msg_error}")
            # If we can't append to messages, create a new list
            messages = messages if hasattr(state, 'messages') else []
            messages.append(AIMessage(content=error_message))
            
        return Command(
            update={
                "messages": messages,
                "version": state.version + 1 if hasattr(state, 'version') else 1,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "resources": get_resource(state)
            },
            goto=goto,
        )

# Example usage:
if __name__ == "__main__":
    # Set up logging for when module is run directly
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    user_message = [HumanMessage(content = "What is the genotype for the mice with these UIDs: 'MUS-220124FOR-1' and 'MUS-220124FOR-73'?"),
    HumanMessage(content="Parsed User Query: ```json{'uid': ['MUS-220124FOR-1', 'MUS-220124FOR-73'], 'sampletype': 'mouse', 'assay': None, 'attribute': 'genotype', 'terms': None}```Justification: The query explicitly mentions UIDs, which are identifiers for specific samples, in this case, mice. The user is interested in the 'genotype' attribute of these samples, as indicated by the phrase 'What is the genotype'. The sample type is inferred to be 'mouse' based on the context of the UIDs and the mention of 'mice'. Explanation: The user query is asking for the genotype of specific mice identified by their UIDs. The UIDs provided are 'MUS-220124FOR-1' and 'MUS-220124FOR-73'. The query is focused on the 'genotype' attribute of these mice.", name = "query_parser")]
    parsed_query = {'uid': ['MUS-220124FOR-1', 'MUS-220124FOR-73'], 'sampletype': 'mouse', 'assay': None, 'attribute': 'genotype', 'terms': None}
    INITIAL_STATE.messages.extend(user_message)
    update_resource(INITIAL_STATE, {"parsed_query": parsed_query})
    conversationalist_node(INITIAL_STATE)