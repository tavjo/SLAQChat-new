from langchain_core.messages import HumanMessage, AIMessage
import sys
import os
import time
import logging

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from typing_extensions import Literal
from langgraph.types import Command
from src.chatbot.baml_client import b as baml
from src.chatbot.studio.models import ConversationState, ResourceBox, Metadata
from src.chatbot.studio.helpers import get_resource

from src.chatbot.studio.prompts import (
    INITIAL_STATE
)

from datetime import datetime, timezone

# Configure logger for this module
logger = logging.getLogger(__name__)

def response_formatter_node(state: ConversationState = INITIAL_STATE) -> Command[Literal["validator"]]:
    """
    Formats the response based on the current conversation state and updates the conversation flow.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["responder"]]: A command object with updated messages, directing the flow to the responder.

    Raises:
        Exception: If any error occurs during the response formatting process.
    """
    messages = state.messages
    name = "response_formatter"
    
    try:
        payload = {
            "system_message": messages[0].content,
            "user_query": messages[1].content,
            "aggregatedMessages": [msg.content for msg in messages if msg.name in ["query_parser", "responder"]],
            "resource": get_resource(state)
        }

        start_time = time.time()
        logger.info("Starting response formatting process")
        
        try:
            result = baml.FormatResponse(payload)
            execution_time = time.time() - start_time
            logger.info(f"Response formatted successfully in {execution_time:.2f} seconds")
            logger.debug(f"Result: {result}")
            logger.info(f"Agent: {result.name} | Justification: {result.justification}")
        except Exception as baml_error:
            logger.error(f"Error in BAML FormatResponse: {str(baml_error)}", exc_info=True)
            raise RuntimeError(f"Failed to format response: {str(baml_error)}") from baml_error

        goto = "validator"
        messages.append(AIMessage(content=result.formattedResponse, name=name))
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
        logger.error(f"Error in response_formatter_node: {str(e)}", exc_info=True)
        # Add the error message to the conversation
        messages.append(AIMessage(
            content=f"An error occurred while formatting the response: {str(e)}",
            name=name
        ))
        state.version += 1
        state.timestamp = datetime.now(timezone.utc)
        
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": get_resource(state)
            },
            goto="validator",
        )


# Example usage:
if __name__ == "__main__":
    initial_state: ConversationState = {
        "messages": [HumanMessage(content="Can you tell me more about the sample with UID PAV-220630FLY-1031?", name = "user"), AIMessage(content="The user is asking for more information about a specific sample with a UID, which requires retrieving metadata related to that sample. The 'basic_sample_info_retriever' is equipped with the necessary tools to fetch the required sample information.", name = "supervisor"), AIMessage(content="The user is requesting more information about a specific sample identified by its UID (PAV-220630FLY-1031). The most appropriate tool to address this request is 'retrieve_sample_info', as it is designed to retrieve detailed information for a given sample UID.", name = "basic_sample_info_retriever"), AIMessage(content="The conversation has progressed to the point where the necessary information about the sample has likely been retrieved. The next step is to format this information for the user to ensure clarity and readability.", name="responder")],
        
        "resources": {
            'sample_metadata': [{'UID': 'PAV-220630FLY-1031', 'Name': '29518-190327', 'Scientist': 'JoAnne Flynn', 'RecordDate': '', 'Protocol': 'P.FLY-231011-V1_Patient-Visit-CD8.docx', 'Type': 'Scan', 'Procedure': '', 'CollectionTime': '', 'Parent': 'NHP-220630FLY-2', 'VisitFacility': 'Flynn Lab', 'VisitLocation': '', 'Notes': 'P0099', 'Publish_uri': 'https://fairdomhub.org/samples/23142', 'TestType': '', 'TestResult': '', 'TestResultFile': '', 'Coscientist': '', 'ProcedureDuration': '', 'DurationUnits': '', 'SampleCreationDate': '2019-03-27 00:00:00', 'BALInstilledVolume': '', 'BALCollectedVolume': '', 'VolumeUnits': '', 'Treatment1': '', 'Treatment1Type': '', 'Treatment1Route': '', 'Treatment1Dose': '', 'Treatment1DoseUnits': '', 'Treatment2': '', 'Treatment2Type': '', 'Treatment2Route': '', 'Treatment2Dose': '', 'Treatment2DoseUnits': '', 'Treatment3': '', 'Treatment3Type': '', 'Treatment3Route': '', 'Treatment3Dose': '', 'Treatment3DoseUnits': '', 'Treatment4': '', 'Treatment4Type': '', 'Treatment4Route': '', 'Treatment4Dose': '', 'Treatment4DoseUnits': '', 'Treatment5': '', 'Treatment5Type': '', 'Treatment5Route': '', 'Treatment5Dose': '', 'Treatment5DoseUnits': '', 'TestType2': '', 'TestResult2': '', 'TestResultFile2': '', 'TestType3': '', 'TestResult3': '', 'TestResultFile3': '', 'Protocol_Classification': '', 'Classification': '', 'ExperimentalTimepoint': '', 'Treatment1Parent': '', 'Treatment2Parent': '', 'Treatment3Parent': '', 'Treatment4Parent': '', 'Treatment5Parent': '', 'NumInjections': ''}]}}
    INITIAL_STATE.messages.extend(initial_state["messages"])
    INITIAL_STATE.resources = ResourceBox(
        sample_metadata = Metadata.model_validate(initial_state["resources"]["sample_metadata"][0]),
    )
    response_formatter_node()