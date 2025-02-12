from langchain_core.messages import HumanMessage
import sys
import os

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

def supervisor_node(state: ConversationState) -> Command[Literal["basic_sample_info_retriever","responder"]]:
    
    if "resources" not in state or state["resources"] is None:
        state["resources"] = default_resource_box()
    if "available_workers" not in state or state["available_workers"] is None:
        state["available_workers"] = WORK_GROUP_A

    payload = {
        "system_message": SYSTEM_MESSAGE,
        "user_query": state["messages"][0].content,
        "aggregatedMessages": [msg.content for msg in state["messages"]],
        "resource": get_resource(state)
    }
    available_workers = get_available_workers(state)
    response = baml.Supervise(payload, available_workers)
    goto = response.Next_worker.agent
    print(f"Next Worker: {goto}\nJustification: {response.justification}")
    available_workers = [i for i in available_workers if i["agent"] != goto]
    update_available_workers(state, available_workers)
    print(f"Remaining Available Workers: {state['available_workers']}")
    # Merge the new message with the existing ones
    updated_messages = state["messages"] + [HumanMessage(content=response.justification, name="supervisor")]
    return Command(update={"messages": updated_messages,
                           "resources": state["resources"],
                           "available_workers": state["available_workers"]},goto=goto)


# Example usage:
if __name__ == "__main__":
    initial_state: ConversationState = {
        "messages": [HumanMessage(content="Can you tell me more about the sample with UID PAV-220630FLY-1031?")]
    }
