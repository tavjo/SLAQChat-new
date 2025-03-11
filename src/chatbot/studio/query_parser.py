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
from src.chatbot.studio.helpers import get_resource, update_messages, update_resource, default_resource_box, ResourceBox, ParsedQuery
import backend.Tools.services.basic_sample_service
from backend.Tools.services.module_to_json import module_to_json
from datetime import datetime, timezone

from src.chatbot.studio.prompts import (
    INITIAL_STATE
)

def query_parser_node(state: ConversationState = INITIAL_STATE) -> Command[Literal["supervisor", "validator"]]:
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
        print("Creating payload...")
        goto = "supervisor"
        messages = state.messages

        payload = {
            "system_message": messages[0].content,
            "user_query": messages[-1].content,
            "aggregatedMessages": [msg.content for msg in messages],
            "resource": state.resources if state.resources else default_resource_box()
        }
        print("Payload created...")
        
        print("Parsing query...")
        start_time = time.time()
        response = baml.ParseQuery(context = payload)
        print(f"Query parsing completed in {time.time() - start_time:.2f} seconds.")

        parsed_query = response.parsed_query.model_dump()#{"parsed_query": response.parsed_query}
        print(f"Parsed Query: {parsed_query}\nJustification: {response.justification}\nExplanation: {response.explanation}")

        parsed_query_string = f"Parsed User Query: ```json\n{parsed_query}\n```\nJustification: {response.justification}\nExplanation: {response.explanation}"

        print(parsed_query_string)
        print("Updating resources...")
        # update_resource(state, parsed_query)
        state.resources = ResourceBox(parsed_query=ParsedQuery.model_validate(parsed_query))
        print("Resources updated...")
        print(state.resources)
        # Merge the new message with the existing ones
        messages.append(HumanMessage(content=parsed_query_string, name="query_parser"))
        state.version += 1
        state.timestamp = datetime.now(timezone.utc)
        print(f"goto: {goto}")
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": state.resources if state.resources else default_resource_box()
            },
            goto=goto
        )
    except Exception as e:
        messages.append(HumanMessage(content=f"I am sorry, I am unable to retrieve the information. Please try again later. You can visit the website for more information.", name = "query_parser"))
        print(f"Redirecting to validator because an error occurred while parsing the query: {e}")
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": state.resources if state.resources else default_resource_box()
            },
            goto="validator"
        )


# Example usage:
if __name__ == "__main__":
    messages = [HumanMessage(content="Can you tell me more about the sample with UID PAV-220630FLY-1031?", name = "user")]
    # messages = [HumanMessage(content="What is the genotype for the mice with these UIDs: 'MUS-220124FOR-1' and 'MUS-220124FOR-73'?", name = "user")]
    # update_messages(INITIAL_STATE, messages[0])
    INITIAL_STATE.messages.extend(messages)
    query_parser_node()
