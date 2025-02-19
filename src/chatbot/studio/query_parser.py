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
from src.chatbot.studio.helpers import create_agent, get_resource, default_resource_box
import backend.Tools.services.basic_sample_service
from backend.Tools.services.module_to_json import functions_to_json, module_to_json

from src.chatbot.studio.prompts import (
    SYSTEM_MESSAGE
)

def query_parser_node(state: ConversationState) -> Command[Literal["schema_mapper", "FINISH"]]:
    """
    Receives a user query and breaks it down into a list of queries.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["supervisor"]]: A command object with updated messages, directing the flow to the next worker.

    Raises:
        Exception: If any error occurs during the parsing process.
    """
    try:

        payload = {
            "system_message": SYSTEM_MESSAGE,
            "user_query": state["messages"][0].content,
            "aggregatedMessages": [msg.content for msg in state["messages"]],
            "resource": default_resource_box()
        }

        start_time = time.time()
        print("Parsing query...")
        response = baml.ParseQuery(payload["user_query"],context = payload,tools = module_to_json(backend.Tools.services.basic_sample_service))
        print(f"Query parsing completed in {time.time() - start_time:.2f} seconds.")

        parsed_query = response.parsed_query
        print(f"Parsed Query: {parsed_query}\nJustification: {response.justification}")

        # Merge the new message with the existing ones
        updated_messages = state["messages"] + [HumanMessage(content=response.parsed_query, name="query_parser")] + [HumanMessage(content="\n".join(response.tasks), name="query_parser")]
        return Command(
            update={
                "messages": updated_messages
            },
            goto="supervisor"
        )
    except Exception as e:
        updated_messages = state["messages"] + [HumanMessage(content=f"I am sorry, I am unable to retrieve the information. Please try again later. You can visit the website for more information.", name = "query_parser")]
        print(f"An error occurred while parsing the query: {e}")
        return Command(
            update={
                "messages": updated_messages
            },
            goto="FINISH"
        )


# Example usage:
if __name__ == "__main__":
    initial_state: ConversationState = {
        "messages": [HumanMessage(content="Can you tell me more about the sample with UID PAV-220630FLY-1031?")]
    }
    query_parser_node(initial_state)
