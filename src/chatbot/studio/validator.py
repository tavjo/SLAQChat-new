from langchain_core.messages import HumanMessage, AIMessage
import sys
import os
import time
import logging
from datetime import datetime, timezone

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from typing_extensions import Literal
from langgraph.types import Command
from src.chatbot.baml_client import b as baml
from src.chatbot.studio.models import ConversationState, ResourceBox
from src.chatbot.studio.helpers import get_resource
from src.chatbot.studio.prompts import INITIAL_STATE

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def validator_node(state: ConversationState = INITIAL_STATE) -> Command[Literal["FINISH"]]:
    """
    Validates the current conversation state and updates the conversation flow.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["FINISH"]]: A command object with updated messages, directing the flow to FINISH.

    Raises:
        Exception: If any error occurs during the validation process.
    """
    messages = state.messages.copy()  # Create a copy to avoid direct modification
    
    try:
        payload = {
            "system_message": messages[0].content,
            "user_query": [msg.content for msg in messages if msg.name == "user"][0],
            "aggregatedMessages": [msg.content for msg in messages],
            "resource": get_resource(state)
        }

        start_time = time.time()
        logger.info("Validating response...")
        
        try:
            response = baml.ValidateResponse(payload)
            elapsed_time = time.time() - start_time
            logger.info(f"Validation completed in {elapsed_time:.2f} seconds.")
            
            logger.info(f"Agent: {response.name}")
            logger.debug(f"Justification: {response.justification}")
            
            goto = "FINISH"
            
            if response.Valid:
                new_aggregate = messages[-1].content
                logger.info("Response validated successfully")
            elif response.Clarifying_Question:
                new_aggregate = response.Clarifying_Question
                logger.info("Clarifying question generated")
            else:
                new_aggregate = response.error
                logger.warning(f"Validation failed: {response.error}")
                
            logger.debug(f"Response content: {new_aggregate}")
            messages.append(AIMessage(content=new_aggregate, name="validator"))
            
        except AttributeError as e:
            logger.error(f"Invalid response format from validation service: {e}")
            messages.append(AIMessage(
                content=f"Unable to process validation response: {str(e)}",
                name="validator"
            ))
            goto = "FINISH"
        
        state.version += 1
        state.timestamp = datetime.now(timezone.utc)
        
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat()
            },
            goto=goto
        )
            
    except KeyError as e:
        logger.error(f"Missing required key in payload or response: {e}")
        messages.append(AIMessage(
            content=f"Validation error: Missing information ({str(e)})",
            name="validator"
        ))
    except IndexError as e:
        logger.error(f"Index error during validation, possible empty message list: {e}")
        messages.append(AIMessage(
            content="Validation error: Conversation history is incomplete",
            name="validator"
        ))
    except Exception as e:
        logger.exception(f"Unexpected error in validator_node: {e}")
        messages.append(AIMessage(
            content=f"An error occurred while validating the response: {str(e)}",
            name="validator"
        ))
    
    # Handle any exception by returning a FINISH command with error information
    state.version += 1
    state.timestamp = datetime.now(timezone.utc)
    state.available_workers = None
    return Command(
        update={
            "messages": messages,
            "version": state.version,
            "timestamp": state.timestamp.isoformat(),
            "available_workers": state.available_workers
        },
        goto="FINISH"
    )


# Example usage:
if __name__ == "__main__":
    initial_state: ConversationState = {
        "messages": [
            HumanMessage(content="Can you tell me more about the sample with UID PAV-220630FLY-1031?", name = "user"),
            AIMessage(content="The user is asking for more information about a specific sample with a UID, which requires retrieving metadata related to that sample. The 'basic_sample_info_retriever' is equipped with the necessary tools to fetch the required sample information.", name = "supervisor"),
            AIMessage(content="The user is requesting more information about a specific sample identified by its UID (PAV-220630FLY-1031). The most appropriate tool to address this request is 'retrieve_sample_info', as it is designed to retrieve detailed information for a given sample UID.", name = "basic_sample_info_retriever"),
            AIMessage(content="The conversation has progressed to the point where the necessary information about the sample has likely been retrieved. The next step is to format this information for the user to ensure clarity and readability.", name="responder"),
            AIMessage(content='Here is the information for the sample with UID PAV-220630FLY-1031:\n\n- **Name**: 29518-190327\n- **Notes**: P0099\n- **Scientist**: JoAnne Flynn\n- **Protocol**: P.FLY-231011-V1_Patient-Visit-CD8.docx\n- **Publish URI**: [Sample Link](https://fairdomhub.org/samples/23142)\n\n**Treatment Information**:\n- Treatment 1: Not specified\n- Treatment 2: Not specified\n- Treatment 3: Not specified', name='response_formatter'),
            AIMessage(content="The information about the sample with UID PAV-220630FLY-1031 has been provided, and the next step is to validate this response to ensure accuracy and completeness before concluding the conversation.", name ="responder")
        ],
        "resources": {'sample_metadata': [{'UID': 'PAV-220630FLY-1031', 'Name': '29518-190327', 'Scientist': 'JoAnne Flynn', 'RecordDate': '', 'Protocol': 'P.FLY-231011-V1_Patient-Visit-CD8.docx', 'Type': 'Scan', 'Procedure': '', 'CollectionTime': '', 'Parent': 'NHP-220630FLY-2', 'VisitFacility': 'Flynn Lab', 'VisitLocation': '', 'Notes': 'P0099', 'Publish_uri': 'https://fairdomhub.org/samples/23142', 'TestType': '', 'TestResult': '', 'TestResultFile': '', 'Coscientist': '', 'ProcedureDuration': '', 'DurationUnits': '', 'SampleCreationDate': '2019-03-27 00:00:00', 'BALInstilledVolume': '', 'BALCollectedVolume': '', 'VolumeUnits': '', 'Treatment1': '', 'Treatment1Type': '', 'Treatment1Route': '', 'Treatment1Dose': '', 'Treatment1DoseUnits': '', 'Treatment2': '', 'Treatment2Type': '', 'Treatment2Route': '', 'Treatment2Dose': '', 'Treatment2DoseUnits': '', 'Treatment3': '', 'Treatment3Type': '', 'Treatment3Route': '', 'Treatment3Dose': '', 'Treatment3DoseUnits': '', 'Treatment4': '', 'Treatment4Type': '', 'Treatment4Route': '', 'Treatment4Dose': '', 'Treatment4DoseUnits': '', 'Treatment5': '', 'Treatment5Type': '', 'Treatment5Route': '', 'Treatment5Dose': '', 'Treatment5DoseUnits': '', 'TestType2': '', 'TestResult2': '', 'TestResultFile2': '', 'TestType3': '', 'TestResult3': '', 'TestResultFile3': '', 'Protocol_Classification': '', 'Classification': '', 'ExperimentalTimepoint': '', 'Treatment1Parent': '', 'Treatment2Parent': '', 'Treatment3Parent': '', 'Treatment4Parent': '', 'Treatment5Parent': '', 'NumInjections': ''}], 'protocolURL': '', 'sampleURL': '', 'UIDs': []}}
    
    INITIAL_STATE.messages.extend(initial_state["messages"])
    INITIAL_STATE.resources = ResourceBox.model_validate(initial_state["resources"])
    validator_node()