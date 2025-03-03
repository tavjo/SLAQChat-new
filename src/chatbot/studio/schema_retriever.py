from langchain_core.messages import HumanMessage
import sys
import os
import time

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from typing_extensions import Literal
from langgraph.types import Command
# from src.chatbot.baml_client import b as baml
from src.chatbot.studio.models import ConversationState, SchemaMapperState
from src.chatbot.studio.helpers import update_messages, update_resource
from backend.Tools.services.schema_service import extract_relevant_schema
from langchain_openai import ChatOpenAI
# from langgraph.prebuilt import create_react_agent
import asyncio

from src.chatbot.studio.prompts import (
    INITIAL_STATE
)



# def schema_retriever_node(state: ConversationState = INITIAL_STATE) -> Command[Literal["supervisor", "FINISH"]]:
#     """
#     Validates the current conversation state and updates the conversation flow.

#     Args:
#         state (ConversationState): The current state of the conversation.

#     Returns:
#         Command[Literal["supervisor"]]: A command object with updated messages, directing the flow to the supervisor.

#     Raises:
#         Exception: If any error occurs during the validation process.
#     """
#     try:
#         start_time = time.time()
#         print("Extracting schema...")
#         schema = extract_relevant_schema()
#         new_resource = {
#             "db_schema": schema
#         }
#         update_resource(state, new_resource)
#         print("Updated state resource with schema.")
#         print(f"Schema extraction completed in {time.time() - start_time:.2f} seconds.")
#         payload = {
#             "system_message": state["messages"][0].content,
#             "user_query": state["messages"][1].content,
#             "aggregatedMessages": [msg.content for msg in state["messages"]],
#             "resource": get_resource(state)
#         }
#         print("Mapping query to schema...")
#         start_time = time.time()
#         input_schema = {
#             "tables": payload["resource"]["db_schema"]
#         }
#         response = baml.RetrieveSchema(payload["user_query"], input_schema)
#         # print(f"Agent: {response.name}\nJustification: {response.justification}")
#         # print(f"Proposed query: {response.pseudo_query}")
#         goto = "supervisor"
#         if response.schema_map:
#             new_resource = {
#                 "db_schema": response.schema_map
#             }
#             update_resource(state, new_resource)
#             print(state["resources"])
#             new_aggregate = f"Proposed database query based on user query: {response.pseudo_query}\nJustification: {response.justification}"
#         else:
#             new_aggregate = response.justification
#         # print(new_aggregate)

#         updated_messages = state["messages"] + [HumanMessage(content=new_aggregate, name="schema_mapper")]
#         print(f"Mapping completed in {time.time() - start_time:.2f} seconds.")
#         return Command(
#             update={
#                 "messages": updated_messages
#             },
#             goto=goto,
#         )
#     except Exception as e:
#         print(f"An error occurred while mapping query to schema: {e}")
#         return Command(
#             update={
#                 "messages": state["messages"] + [HumanMessage(content=f"An error occurred while mapping query to schema: {e}", name="schema_mapper")]
#             },
#             goto="FINISH",
#         )

async def schema_retriever_node(state: ConversationState = INITIAL_STATE) -> Command[Literal["multi_sample_info_retriever", "validator"]]:
    """
    Validates the current conversation state and updates the conversation flow.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["multi_sample_info_retriever", "validator"]]: A command object with updated messages, directing the flow to the next agent.

    Raises:
        Exception: If any error occurs during the schema retrieval process.
    """
    try:
        start_time = time.time()
        print("Creating schema retriever...")
        print(len(state["messages"]))
        print(state["messages"][1].content)
        user_query = state["messages"][1].content
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        db_schema = await extract_relevant_schema()
        # schema_retriever = create_react_agent(
        #     model=llm,
        #     tools = [extract_relevant_schema],
        prompt=(
        f"Map the user query: \n{user_query} \nto the database schema: \n{ db_schema}."
        "The relevant database table is `seek_production.samples` which contains a JSON column 'json_metadata' with sample-specific metadata. "
        "Extract only the keys that are actually present in the schema and are also relevant to the user query. "
        "Do not invent any keys; if a key is not in the schema, omit it. "
        "For example, if the user asks for 'samples of genotype X', return the closest matching keys from the schema such as 'UID' and 'Genotype'. "
        "If the user query is not related to the database, return 'No relevant information found in the database.' "
        # "\nImportant: When invoking extract_relevant_schema, do not pass any explicit value for 'database_name' or 'table_names'. "
        "\nImportant: Only return the relevant keys from the json_metadata column of the schema, the database schema as a json object, and your justification. Do not return any other information such as speculated keys or proposed queries."
        )
        # )
        messages = [HumanMessage(content=prompt)]
        update_messages(state, messages)
        print("Schema retriever created in {time.time() - start_time:.2f} seconds.")
        print("Invoking schema retriever...")
        start_time = time.time()
        result = llm.with_structured_output(SchemaMapperState).invoke(messages)
        print(f"Invocation completed in {time.time() - start_time:.2f} seconds.")
        if result and result is not None:
            print(result)
            new_resource = {
                "db_schema": result.schema_map
            }
            update_resource(state, new_resource)
            updated_messages = [HumanMessage(content=user_query, name="user")] + [HumanMessage(content= "The relevant database keys are: " + "\n".join(result.relevant_keys), name="schema_mapper")]
            update_messages(state, updated_messages)
            print(state["messages"])
        goto = "multi_sample_info_retriever"
        print(f"Mapping completed in {time.time() - start_time:.2f} seconds.")
        print(state["resources"])
        return Command(
            update={
                "messages": updated_messages
            },
            goto=goto
        )
    except Exception as e:
        print(f"An error occurred while mapping query to schema: {e}")
        return Command(
            update={
                "messages": state["messages"] + [HumanMessage(content=f"An error occurred while mapping query to schema: {e}", name="schema_mapper")]
            },
            goto="validator"
        )

# Example usage:
if __name__ == "__main__":
    initial_state: ConversationState = {
        "messages": [
            # HumanMessage(content="Retrieve UIDs of all samples of this genotype: 'RaDR+/+; GPT+/+; Aag -/-'", name = "user")
            HumanMessage(content="Can you please list all the samples associated with the following scientist: 'Patricia Grace'?", name = "user")
        ]
    }
    update_messages(INITIAL_STATE, initial_state["messages"])
    asyncio.run(schema_retriever_node())