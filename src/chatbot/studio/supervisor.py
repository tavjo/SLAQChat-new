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
from src.chatbot.studio.helpers import get_resource, default_resource_box, get_available_workers, update_available_workers

from src.chatbot.studio.prompts import (
    SYSTEM_MESSAGE,
    WORK_GROUP_A
)

def supervisor_node(state: ConversationState) -> Command[Literal["basic_sample_info_retriever","multi_sample_info_retriever", "responder", "FINISH"]]:
    """
    Supervises the current conversation state to determine the next worker and update the conversation flow.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["basic_sample_info_retriever", "responder"]]: A command object with updated messages, resources, and available workers, directing the flow to the next worker.

    Raises:
        Exception: If any error occurs during the supervision process.
    """
    try:
        if "resources" not in state or state["resources"] is None:
            state["resources"] = default_resource_box()
        if "available_workers" not in state or state["available_workers"] is None or state["messages"][-1].name == "query_parser":
            state["available_workers"] = WORK_GROUP_A

        payload = {
            "system_message": SYSTEM_MESSAGE,
            "user_query": state["messages"][0].content,
            "aggregatedMessages": [msg.content for msg in state["messages"]],
            "resource": get_resource(state)
        }

        available_workers = get_available_workers(state)

        start_time = time.time()
        print("Supervising...")
        response = baml.Supervise(payload, available_workers)
        print(f"Supervision completed in {time.time() - start_time:.2f} seconds.")

        goto = response.Next_worker.agent
        print(f"Next Worker: {goto}\nJustification: {response.justification}")

        available_workers = [i for i in available_workers if i["agent"] != goto]
        update_available_workers(state, available_workers)
        print(f"Remaining Available Workers: {state['available_workers']}")

        # Merge the new message with the existing ones
        updated_messages = state["messages"] + [HumanMessage(content=response.justification, name="supervisor")]
        return Command(
            update={
                "messages": updated_messages,
                "resources": state["resources"],
                "available_workers": state["available_workers"]
            },
            goto=goto
        )
    except Exception as e:
        updated_messages = state["messages"] + [HumanMessage(content=f"I am sorry, I am unable to retrieve the information. Please try again later. You can visit the website for more information.", name = "supervisor")]
        print(f"An error occurred while retrieving the information: {e}")
        return Command(
            update={
                "messages": updated_messages,
            },
            goto="FINISH"
        )


# Example usage:
if __name__ == "__main__":
    initial_state: ConversationState = {
        "messages": [HumanMessage(content="Can you tell me more about the sample with UID PAV-220630FLY-1031?")]
    }
    supervisor_node(initial_state)