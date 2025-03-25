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
from src.chatbot.baml_client.async_client import b as baml
from src.chatbot.studio.models import ConversationState
from src.chatbot.studio.helpers import get_resource, update_resource, convert_messages
import asyncio
from datetime import datetime, timezone

from src.chatbot.studio.prompts import (
    INITIAL_STATE
)

# Set up logger
logger = logging.getLogger(__name__)

async def data_summarizer_node(state: ConversationState = INITIAL_STATE) -> Command[Literal["response_formatter", "validator"]]:
    """
    Summarizes data based on the current conversation state and updates the conversation flow.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["responder", "validator"]]: A command object with updated messages,
        directing the flow to the responder or validator.

    Raises:
        Exception: If any error occurs during the data summarization process.
    """
    messages = state.messages
    goto = "validator"
    try:
        payload = {
            # "system_message": messages[0].content,
            "user_query": messages[0].content,
            "aggregatedMessages": convert_messages(messages),
            "resource": get_resource(state),
            "last_worker": state.last_worker
        }

        start_time = time.time()
        logger.info("Summarizing data...")
        
        try:
            summarize_stream = baml.stream.SummarizeData(payload)
            result = await summarize_stream.get_final_response()
            logger.info(f"Summary generated: {result.summary}")
            name = "data_summarizer"
            logger.info(f"Agent: {name} | Justification: {result.justification}")
            goto = "response_formatter"
            messages.append(AIMessage(content=result.summary, name=name))
            logger.info(f"Data summarized in {time.time() - start_time:.2f} seconds.")
        except Exception as baml_error:
            logger.error(f"BAML summarization failed: {baml_error}", exc_info=True)
            raise
            
        state.version += 1
        state.timestamp = datetime.now(timezone.utc)
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": get_resource(state)
            },
            goto=goto,
        )
    except Exception as e:
        logger.exception(f"Error in data_summarizer_node: {e}")
        
        # Still update the state even on failure
        state.version += 1
        state.timestamp = datetime.now(timezone.utc)
        
        return Command(
            update={
                "messages": messages,
                "version": state.version,
                "timestamp": state.timestamp.isoformat(),
                "resources": get_resource(state)
            },
            goto=goto,
        )


# Example usage:
if __name__ == "__main__":
    # Configure logging when running the file directly
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    initial_state: ConversationState = {
        "messages": [
            HumanMessage(content="Can you tell me more about the sample with UID PAV-220630FLY-1031?", name = "user"), 
            AIMessage(content="The user is asking for more information about a specific sample with a UID, which requires retrieving metadata related to that sample. The 'basic_sample_info_retriever' is equipped with the necessary tools to fetch the required sample information.", name = "supervisor"), 
            AIMessage(content="The user is requesting more information about a specific sample identified by its UID (PAV-220630FLY-1031). The most appropriate tool to address this request is 'retrieve_sample_info', as it is designed to retrieve detailed information for a given sample UID.", name = "basic_sample_info_retriever"), 
            AIMessage(content="The conversation has progressed to the point where the necessary information about the sample has likely been retrieved. The next step is to summarize this information for the user to ensure clarity and readability.", name="responder")
            ],
        "resources": {'sample_metadata': [{'UID': 'PAV-220630FLY-1031', 'Name': '29518-190327', 'Scientist': 'JoAnne Flynn', 'RecordDate': '', 'Protocol': 'P.FLY-231011-V1_Patient-Visit-CD8.docx', 'Type': 'Scan', 'Procedure': '', 'CollectionTime': '', 'Parent': 'NHP-220630FLY-2', 'VisitFacility': 'Flynn Lab', 'VisitLocation': '', 'Notes': 'P0099', 'Publish_uri': 'https://fairdomhub.org/samples/23142', 'TestType': '', 'TestResult': '', 'TestResultFile': '', 'Coscientist': '', 'ProcedureDuration': '', 'DurationUnits': '', 'SampleCreationDate': '2019-03-27 00:00:00', 'BALInstilledVolume': '', 'BALCollectedVolume': '', 'VolumeUnits': '', 'Treatment1': '', 'Treatment1Type': '', 'Treatment1Route': '', 'Treatment1Dose': '', 'Treatment1DoseUnits': '', 'Treatment2': '', 'Treatment2Type': '', 'Treatment2Route': '', 'Treatment2Dose': '', 'Treatment2DoseUnits': '', 'Treatment3': '', 'Treatment3Type': '', 'Treatment3Route': '', 'Treatment3Dose': '', 'Treatment3DoseUnits': '', 'Treatment4': '', 'Treatment4Type': '', 'Treatment4Route': '', 'Treatment4Dose': '', 'Treatment4DoseUnits': '', 'Treatment5': '', 'Treatment5Type': '', 'Treatment5Route': '', 'Treatment5Dose': '', 'Treatment5DoseUnits': '', 'TestType2': '', 'TestResult2': '', 'TestResultFile2': '', 'TestType3': '', 'TestResult3': '', 'TestResultFile3': '', 'Protocol_Classification': '', 'Classification': '', 'ExperimentalTimepoint': '', 'Treatment1Parent': '', 'Treatment2Parent': '', 'Treatment3Parent': '', 'Treatment4Parent': '', 'Treatment5Parent': '', 'NumInjections': ''}]}
    }
    INITIAL_STATE.messages.extend(initial_state["messages"])
    # INITIAL_STATE.resources = ResourceBox.model_validate(initial_state["resources"])
    update_resource(INITIAL_STATE, initial_state["resources"])
    asyncio.run(data_summarizer_node())