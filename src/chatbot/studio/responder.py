from langchain_core.messages import HumanMessage, AIMessage
import sys
import os
import time
import logging
import traceback

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from typing_extensions import Literal
from langgraph.types import Command
from src.chatbot.baml_client import b as baml
from src.chatbot.studio.models import ConversationState, ResourceBox, Metadata, ParsedQuery, SampleTypeAttributes
from src.chatbot.studio.helpers import get_resource, get_available_workers, update_available_workers, get_last_worker

from src.chatbot.studio.prompts import (
    WORK_GROUP_B, 
    INITIAL_STATE
)
from datetime import datetime, timezone

# Configure logging
logger = logging.getLogger(__name__)

def responder_node(state: ConversationState = INITIAL_STATE) -> Command[Literal["data_summarizer", "response_formatter", "validator"]]:
    """
    Processes the current conversation state to determine the next worker and update the conversation flow.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["data_summarizer", "response_formatter"]]: A command object with updated messages, resources, and available workers, directing the flow to the next worker.

    Raises:
        Exception: If any error occurs during the response processing.
    """
    start_time = time.time()
    state.available_workers = None
    messages = state.messages
    last_worker = get_last_worker(state)
    try:
        logger.info("Processing conversation in responder node")
        # messages = state.messages
        
        try:
            logger.debug("Creating payload for BAML Respond")
            payload = {
                "system_message": messages[0].content,
                "user_query": messages[1].content,
                "aggregatedMessages": [msg.content for msg in messages],
                "resource": get_resource(state),
                "last_worker": last_worker
            }
            logger.debug("Payload created successfully")
        except IndexError as e:
            logger.error(f"Failed to create payload - message index error: {str(e)}")
            raise

        # Determine which worker group to use
        # if messages[-1].name == "supervisor" or messages[-1].name == "FINISH":
        #     logger.debug("Worker adjustment based on supervisor or FINISH message")
        #     state.available_workers = WORK_GROUP_B  

        # Ensure available workers are set
        if not state.available_workers or state.available_workers == None:
            state.available_workers = WORK_GROUP_B
        available_workers = get_available_workers(state)
        logger.info(f"Available Workers: {[w.agent for w in available_workers] if available_workers is not None else 'None'}")

        # Call BAML API
        try:
            logger.info("Calling BAML Respond")
            response = baml.Respond(payload, available_workers)
            goto = response.Next_worker.agent
            logger.info(f"Next Worker: {goto}")
            logger.debug(f"Justification: {response.justification}")
        except Exception as e:
            logger.error(f"BAML Respond call failed: {str(e)}")
            raise

        # Update available workers
        try:
            logger.debug("Updating available workers")
            available_workers = [i for i in available_workers if i.agent != goto]
            update_available_workers(state, available_workers)
            # logger.debug(f"Remaining Available Workers: {[w.agent for w in state.available_workers] if state.available_workers else 'None'}")
        except Exception as e:
            logger.error(f"Failed to update available workers: {str(e)}")
            # Continue with operation even if worker update fails

        # Append responder message
        try:
            logger.debug("Appending responder message")
            messages.append(AIMessage(content=f"{response.justification}\n{messages[-1].content}", name="responder"))
        except Exception as e:
            logger.error(f"Failed to append message: {str(e)}")
            raise

        # Update state metadata
        state.version += 1
        state.timestamp = datetime.now(timezone.utc)
        elapsed_time = time.time() - start_time
        logger.info(f"Responder function executed in {elapsed_time:.2f} seconds")
        
        return Command(
            update={
                "messages": messages,
                "available_workers": get_available_workers(state),
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": get_resource(state),
                "last_worker": last_worker
            },
            goto=goto
        )
    except Exception as e:
        elapsed_time = time.time() - start_time
        error_details = traceback.format_exc()
        logger.error(f"Error in responder_node: {str(e)}\n{error_details}")
        logger.info(f"Responder function failed after {elapsed_time:.2f} seconds")
        
        try:
            error_message = f"I am sorry, I am unable to retrieve the information because of the following error: {e}. Please try again later. You can visit the NExtSEEK website (nextseek.mit.edu) for more information."
            messages.append(AIMessage(content=error_message, name="responder"))
            
            # Ensure version and timestamp are updated even in error cases
            if not hasattr(state, 'version'):
                state.version = 0
            state.version += 1
            
            state.timestamp = datetime.now(timezone.utc)
        except Exception as nested_e:
            logger.critical(f"Failed to append error message: {str(nested_e)}")
        
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": get_resource(state),
                "last_worker": last_worker
            },
            goto="validator"
        )


# Example usage:
if __name__ == "__main__":
    initial_state: ConversationState = {
        "messages": [HumanMessage(content="Can you tell me more about the sample with UID PAV-220630FLY-1031?", name = "user"), AIMessage(content="The user is asking for more information about a specific sample with a UID, which requires retrieving metadata related to that sample. The 'basic_sample_info_retriever' is equipped with the necessary tools to fetch the required sample information.", name = "supervisor"), AIMessage(content="The user is requesting more information about a specific sample identified by its UID (PAV-220630FLY-1031). The most appropriate tool to address this request is 'retrieve_sample_info', as it is designed to retrieve detailed information for a given sample UID.", name = "basic_sample_info_retriever")],

        "resources": {
            "sample_metadata" : Metadata.model_validate({'UID': 'PAV-220630FLY-1031', 'Name': '29518-190327', 'Scientist': 'JoAnne Flynn', 'RecordDate': '', 'Protocol': 'P.FLY-231011-V1_Patient-Visit-CD8.docx', 'Type': 'Scan', 'Procedure': '', 'CollectionTime': '', 'Parent': 'NHP-220630FLY-2', 'VisitFacility': 'Flynn Lab', 'VisitLocation': '', 'Notes': 'P0099', 'Publish_uri': 'https://fairdomhub.org/samples/23142', 'TestType': '', 'TestResult': '', 'TestResultFile': '', 'Coscientist': '', 'ProcedureDuration': '', 'DurationUnits': '', 'SampleCreationDate': '2019-03-27 00:00:00', 'BALInstilledVolume': '', 'BALCollectedVolume': '', 'VolumeUnits': '', 'Treatment1': '', 'Treatment1Type': '', 'Treatment1Route': '', 'Treatment1Dose': '', 'Treatment1DoseUnits': '', 'Treatment2': '', 'Treatment2Type': '', 'Treatment2Route': '', 'Treatment2Dose': '', 'Treatment2DoseUnits': '', 'Treatment3': '', 'Treatment3Type': '', 'Treatment3Route': '', 'Treatment3Dose': '', 'Treatment3DoseUnits': '', 'Treatment4': '', 'Treatment4Type': '', 'Treatment4Route': '', 'Treatment4Dose': '', 'Treatment4DoseUnits': '', 'Treatment5': '', 'Treatment5Type': '', 'Treatment5Route': '', 'Treatment5Dose': '', 'Treatment5DoseUnits': '', 'TestType2': '', 'TestResult2': '', 'TestResultFile2': '', 'TestType3': '', 'TestResult3': '', 'TestResultFile3': '', 'Protocol_Classification': '', 'Classification': '', 'ExperimentalTimepoint': '', 'Treatment1Parent': '', 'Treatment2Parent': '', 'Treatment3Parent': '', 'Treatment4Parent': '', 'Treatment5Parent': '', 'NumInjections': ''}),
            "protocolURL": None,
            "sampleURL": None,
            "UIDs": None,
            "db_schema": None,
            "parsed_query": ParsedQuery(uid=[], sampletype=[], assay=[], attribute=[], terms=[]),
            "st_attributes": [SampleTypeAttributes(sampletype="", st_description="", attributes=[])]
        }
    }

    INITIAL_STATE.messages.extend(initial_state["messages"])
    INITIAL_STATE.resources = ResourceBox.model_validate(initial_state["resources"])
    responder_node()