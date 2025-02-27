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

def conversationalist_node(state: ConversationState) -> Command[Literal["schema_retriever", "validator", "FINISH"]]:
    """
    Either responds directly to the user or directs the flow to the schema_retriever.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["FINISH", "schema_retriever"]]: A command object with updated messages, directing the flow to FINISH or the schema_retriever.

    Raises:
        Exception: If any error occurs during the validation process.
    """
    try:
        payload = {
            "system_message": state["messages"][0].content,
            "user_query": state["messages"][-1].content,
            "aggregatedMessages": [msg.content for msg in state["messages"]],
            "resource": default_resource_box()
        }

        start_time = time.time()
        print("Obtaining response...")
        response = baml.Conversationalist(payload["user_query"])
        print(f"Response obtained in {time.time() - start_time:.2f} seconds.")

        print(f"Agent: {response.name}\nJustification: {response.justification}")
        if response.retrieve_info:
            goto = "schema_retriever"
            new_aggregate = response.user_query
            updated_messages = [HumanMessage(content=new_aggregate, name=response.name)]
        else:
            goto = "FINISH"
            new_aggregate = response.response
            updated_messages = state["messages"] + [HumanMessage(content=new_aggregate, name=response.name)]
        update_messages(state, updated_messages)
        return Command(
            update={
                "messages": updated_messages
            },
            goto=goto
        )
    except Exception as e:
        print(f"An error occurred in conversationalist_node: {e}")
        return Command(
            update={
                "messages": state["messages"]
            },
            goto="validator",
        )

# Example usage:
if __name__ == "__main__":
    user_message = [HumanMessage(content = "Hi! Which country has the best food?")]
    update_messages(INITIAL_STATE, user_message)
    conversationalist_node(INITIAL_STATE)