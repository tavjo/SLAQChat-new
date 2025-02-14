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
from src.chatbot.studio.helpers import get_resource, get_available_workers, update_available_workers

from src.chatbot.studio.prompts import (
    SYSTEM_MESSAGE,
    WORK_GROUP_B
)

def responder_node(state: ConversationState) -> Command[Literal["data_summarizer", "response_formatter", "validator", "FINISH"]]:
    """
    Processes the current conversation state to determine the next worker and update the conversation flow.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        Command[Literal["data_summarizer", "response_formatter", "validator", "FINISH"]]: A command object with updated messages, resources, and available workers, directing the flow to the next worker.

    Raises:
        Exception: If any error occurs during the response processing.
    """
    try:
        start_time = time.time()
        payload = {
            "system_message": SYSTEM_MESSAGE,
            "user_query": state["messages"][0].content,
            "aggregatedMessages": [msg.content for msg in state["messages"]],
            "resource": get_resource(state)
        }

        if state["messages"][-1].name == "supervisor":
            update_available_workers(state, WORK_GROUP_B)

        available_workers = get_available_workers(state)
        print(f"Available Workers: {available_workers}")

        response = baml.Respond(payload, available_workers)
        goto = response.Next_worker.agent
        print(f"Next Worker: {goto}\nJustification: {response.justification}")

        available_workers = [i for i in available_workers if i["agent"] != goto]
        update_available_workers(state, available_workers)
        print(f"Remaining Available Workers: {state['available_workers']}")

        if goto == "FINISH":
            print(state["messages"][-1].content)
            updated_messages = state["messages"] + [HumanMessage(content=response.justification, name="responder")] + [HumanMessage(content=state["messages"][-1].content, name="responder")]
        else:
            updated_messages = state["messages"] + [HumanMessage(content=response.justification, name="responder")]

        print(f"Function executed in {time.time() - start_time:.2f} seconds.")
        return Command(
            update={
                "messages": updated_messages,
                "resources": state["resources"],
                "available_workers": state["available_workers"]
            },
            goto=goto
        )
    except Exception as e:
        updated_messages = state["messages"] + [HumanMessage(content=f"I am sorry, I am unable to retrieve the information. Please try again later. You can visit the website for more information.", name = "responder")]
        print(f"An error occurred in responder_node: {e}")
        return Command(
            update={
                "messages": updated_messages
            },
            goto="FINISH"
        )


# Example usage:
if __name__ == "__main__":
    initial_state: ConversationState = {
        "messages": [HumanMessage(content="Can you tell me more about the sample with UID PAV-220630FLY-1031?", name = "user"), HumanMessage(content="The user is asking for more information about a specific sample with a UID, which requires retrieving metadata related to that sample. The 'basic_sample_info_retriever' is equipped with the necessary tools to fetch the required sample information.", name = "supervisor"), HumanMessage(content="The user is requesting more information about a specific sample identified by its UID (PAV-220630FLY-1031). The most appropriate tool to address this request is 'retrieve_sample_info', as it is designed to retrieve detailed information for a given sample UID.", name = "basic_sample_info_retriever")],
        "resources": {'sample_metadata': [{'UID': 'PAV-220630FLY-1031', 'Name': '29518-190327', 'Scientist': 'JoAnne Flynn', 'RecordDate': '', 'Protocol': 'P.FLY-231011-V1_Patient-Visit-CD8.docx', 'Type': 'Scan', 'Procedure': '', 'CollectionTime': '', 'Parent': 'NHP-220630FLY-2', 'VisitFacility': 'Flynn Lab', 'VisitLocation': '', 'Notes': 'P0099', 'Publish_uri': 'https://fairdomhub.org/samples/23142', 'TestType': '', 'TestResult': '', 'TestResultFile': '', 'Coscientist': '', 'ProcedureDuration': '', 'DurationUnits': '', 'SampleCreationDate': '2019-03-27 00:00:00', 'BALInstilledVolume': '', 'BALCollectedVolume': '', 'VolumeUnits': '', 'Treatment1': '', 'Treatment1Type': '', 'Treatment1Route': '', 'Treatment1Dose': '', 'Treatment1DoseUnits': '', 'Treatment2': '', 'Treatment2Type': '', 'Treatment2Route': '', 'Treatment2Dose': '', 'Treatment2DoseUnits': '', 'Treatment3': '', 'Treatment3Type': '', 'Treatment3Route': '', 'Treatment3Dose': '', 'Treatment3DoseUnits': '', 'Treatment4': '', 'Treatment4Type': '', 'Treatment4Route': '', 'Treatment4Dose': '', 'Treatment4DoseUnits': '', 'Treatment5': '', 'Treatment5Type': '', 'Treatment5Route': '', 'Treatment5Dose': '', 'Treatment5DoseUnits': '', 'TestType2': '', 'TestResult2': '', 'TestResultFile2': '', 'TestType3': '', 'TestResult3': '', 'TestResultFile3': '', 'Protocol_Classification': '', 'Classification': '', 'ExperimentalTimepoint': '', 'Treatment1Parent': '', 'Treatment2Parent': '', 'Treatment3Parent': '', 'Treatment4Parent': '', 'Treatment5Parent': '', 'NumInjections': ''}], 'protocolURL': '', 'sampleURL': '', 'UIDs': []},
        "available_workers": WORK_GROUP_B,
    }

    new_state: ConversationState = {
        "messages": [
            HumanMessage(content="Can you tell me more about the sample with UID PAV-220630FLY-1031?", name = "user"),
            HumanMessage(content="The user is asking for more information about a specific sample with a UID, which requires retrieving metadata related to that sample. The 'basic_sample_info_retriever' is equipped with the necessary tools to fetch the required sample information.", name = "supervisor"),
            HumanMessage(content="The user is requesting more information about a specific sample identified by its UID (PAV-220630FLY-1031). The most appropriate tool to address this request is 'retrieve_sample_info', as it is designed to retrieve detailed information for a given sample UID.", name = "basic_sample_info_retriever"),
            HumanMessage(content="The conversation has progressed to the point where the necessary information about the sample has likely been retrieved. The next step is to format this information for the user to ensure clarity and readability.", name="responder"),
            HumanMessage(content='Here is the information for the sample with UID PAV-220630FLY-1031:\n\n- **Name**: 29518-190327\n- **Notes**: P0099\n- **Scientist**: JoAnne Flynn\n- **Protocol**: P.FLY-231011-V1_Patient-Visit-CD8.docx\n- **Publish URI**: [Sample Link](https://fairdomhub.org/samples/23142)\n\n**Treatment Information**:\n- Treatment 1: Not specified\n- Treatment 2: Not specified\n- Treatment 3: Not specified', name='response_formatter')
        ],
        
        "resources": {
            'sample_metadata': [{'UID': 'PAV-220630FLY-1031', 'Name': '29518-190327', 'Scientist': 'JoAnne Flynn', 'RecordDate': '', 'Protocol': 'P.FLY-231011-V1_Patient-Visit-CD8.docx', 'Type': 'Scan', 'Procedure': '', 'CollectionTime': '', 'Parent': 'NHP-220630FLY-2', 'VisitFacility': 'Flynn Lab', 'VisitLocation': '', 'Notes': 'P0099', 'Publish_uri': 'https://fairdomhub.org/samples/23142', 'TestType': '', 'TestResult': '', 'TestResultFile': '', 'Coscientist': '', 'ProcedureDuration': '', 'DurationUnits': '', 'SampleCreationDate': '2019-03-27 00:00:00', 'BALInstilledVolume': '', 'BALCollectedVolume': '', 'VolumeUnits': '', 'Treatment1': '', 'Treatment1Type': '', 'Treatment1Route': '', 'Treatment1Dose': '', 'Treatment1DoseUnits': '', 'Treatment2': '', 'Treatment2Type': '', 'Treatment2Route': '', 'Treatment2Dose': '', 'Treatment2DoseUnits': '', 'Treatment3': '', 'Treatment3Type': '', 'Treatment3Route': '', 'Treatment3Dose': '', 'Treatment3DoseUnits': '', 'Treatment4': '', 'Treatment4Type': '', 'Treatment4Route': '', 'Treatment4Dose': '', 'Treatment4DoseUnits': '', 'Treatment5': '', 'Treatment5Type': '', 'Treatment5Route': '', 'Treatment5Dose': '', 'Treatment5DoseUnits': '', 'TestType2': '', 'TestResult2': '', 'TestResultFile2': '', 'TestType3': '', 'TestResult3': '', 'TestResultFile3': '', 'Protocol_Classification': '', 'Classification': '', 'ExperimentalTimepoint': '', 'Treatment1Parent': '', 'Treatment2Parent': '', 'Treatment3Parent': '', 'Treatment4Parent': '', 'Treatment5Parent': '', 'NumInjections': ''}], 
            'protocolURL': '', 
            'sampleURL': '', 
            'UIDs': []
        },
        
        "available_workers": [
            {'agent': 'data_summarizer', 'role': '1.(optional) Summarize conversation and data if more than 8 elements in aggregatedMessages', 'toolbox': None, 'tools_description': None}, {'agent': 'validator', 'role': '3. Validate the response', 'toolbox': None, 'tools_description': None}, {'agent': 'FINISH', 'role': '4.Finish the conversation', 'toolbox': None, 'tools_description': None}
        ]
    }
    # responder_node(initial_state)
    responder_node(new_state)