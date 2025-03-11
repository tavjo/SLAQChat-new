from langchain_core.messages import HumanMessage
import sys
import os
import time

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from typing_extensions import Literal
from langgraph.types import Command
from src.chatbot.baml_client import b as baml
from src.chatbot.studio.models import ConversationState
from src.chatbot.studio.helpers import get_resource, update_messages, default_resource_box

from src.chatbot.studio.prompts import (
    INITIAL_STATE
)
from datetime import datetime, timezone

def conversationalist_node(state: ConversationState) -> Command[Literal["query_parser", "validator", "FINISH"]]:
    """
    Either responds directly to the user or directs the flow to the supervisor.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["validator","FINISH","query_parser"]]: A command object with updated messages, directing the flow to the next agent.

    Raises:
        Exception: If any error occurs during the conversation.
    """
    try:
        payload = {
            "system_message": state.messages[0].content,
            "user_query": state.messages[-1].content,
            "aggregatedMessages": [msg.content for msg in state.messages],
            "resource": default_resource_box()
        }

        start_time = time.time()
        print("Obtaining response...")
        response = baml.Conversationalist(payload["user_query"])
        print(f"Response obtained in {time.time() - start_time:.2f} seconds.")

        goto = None

        print(f"Agent: {response.name}\nJustification: {response.justification}")
        if response.retrieve_info:
            goto = "query_parser"
            new_aggregate = response.user_query
            updated_messages = [HumanMessage(content=new_aggregate, name="user")]
        else:
            goto = "FINISH"
            new_aggregate = response.response
            updated_messages = state.messages.append(HumanMessage(content=new_aggregate, name=response.name)) 
        
        # update_messages(state, updated_messages)
        print(goto)
        state.version += 1
        state.timestamp = datetime.now(timezone.utc)
        return Command(
            update={
                "messages": updated_messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat()
            },
            goto=goto
        )
    except Exception as e:
        print(f"An error occurred in conversationalist_node: {e}")
        return Command(
            update={
                "messages": state.messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat()
            },
            goto="validator",
        )

# Example usage:
if __name__ == "__main__":
    user_message = [HumanMessage(content = "Hi! Can you give me some information about this sample: NHP-220630FLY-2?")]
    update_messages(INITIAL_STATE, user_message)
    conversationalist_node(INITIAL_STATE)