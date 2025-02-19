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
from src.chatbot.studio.helpers import get_resource, update_resource
from backend.Tools.services.schema_service import extract_relevant_schema

from src.chatbot.studio.prompts import (
    SYSTEM_MESSAGE
)

def schema_retriever_node(state: ConversationState) -> Command[Literal["supervisor", "FINISH"]]:
    """
    Validates the current conversation state and updates the conversation flow.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["supervisor"]]: A command object with updated messages, directing the flow to the supervisor.

    Raises:
        Exception: If any error occurs during the validation process.
    """
    try:
        start_time = time.time()
        print("Extracting schema...")
        schema = extract_relevant_schema('DB_NAME')
        new_resource = {
            "db_schema": schema
        }
        update_resource(state, new_resource)
        print("Updated state resource with schema.")
        payload = {
            "system_message": SYSTEM_MESSAGE,
            "user_query": state["messages"][0].content,
            "aggregatedMessages": [msg.content for msg in state["messages"]],
            "resource": get_resource(state)
        }
        print("Mapping query to schema...")
        input_schema = {
            "tables": payload["resource"]["db_schema"]
        }
        response = baml.RetrieveSchema(payload["user_query"], input_schema)
        # print(f"Agent: {response.name}\nJustification: {response.justification}")
        # print(f"Proposed query: {response.pseudo_query}")
        goto = "supervisor"
        if response.schema_map:
            new_resource = {
                "db_schema": response.schema_map
            }
            update_resource(state, new_resource)
            new_aggregate = f"Proposed database query based on user query: {response.pseudo_query}\nJustification: {response.justification}"
        else:
            new_aggregate = response.justification
        # print(new_aggregate)

        updated_messages = state["messages"] + [HumanMessage(content=new_aggregate, name="schema_mapper")]
        print(f"Mapping completed in {time.time() - start_time:.2f} seconds.")
        return Command(
            update={
                "messages": updated_messages
            },
            goto=goto,
        )
    except Exception as e:
        print(f"An error occurred while mapping query to schema: {e}")
        return Command(
            update={
                "messages": state["messages"] + [HumanMessage(content=f"An error occurred while mapping query to schema: {e}", name="schema_mapper")]
            },
            goto="FINISH",
        )


# Example usage:
if __name__ == "__main__":
    initial_state: ConversationState = {
        "messages": [
            # HumanMessage(content="Retrieve UIDs of all samples of this genotype: 'RaDR+/+; GPT+/+; Aag -/-'", name = "user")
            HumanMessage(content="Please find the UIDs of all samples that are part of the 'CD8 Depletion' study.", name = "user")
        ]
    }
    schema_retriever_node(initial_state)