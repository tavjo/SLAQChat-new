# src/chatbot/studio/advanced_sample_retriever.py

import sys
import os
import time

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

# from backend.Tools.services.sample_service import *
from backend.Tools.services.module_to_json import functions_to_json

from src.chatbot.studio.helpers import update_resource, default_resource_box, update_messages, async_navigator_handler
import asyncio
from langchain_core.messages import HumanMessage, SystemMessage
from src.chatbot.studio.models import ConversationState, ToolResponse, ResourceBox, DBSchema, Table, Column, ParsedQuery
from src.chatbot.studio.helpers import create_worker, create_tool_call_node #, create_agent
from langgraph.types import Command
from typing_extensions import Literal
# from langchain_openai import ChatOpenAI
# from langgraph.prebuilt import create_react_agent
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from src.chatbot.studio.prompts import TOOLSET2, INITIAL_STATE
TOOL_DISPATCH = {
    attr.__name__: attr for attr in TOOLSET2
}

async def multi_sample_info(state: ConversationState = INITIAL_STATE)->ToolResponse:
    """
    Main function to handle the asynchronous navigation and tool execution.

    This function uses the async navigator handler to determine the next tool
    to execute based on a user query. It then calls the appropriate tool function
    asynchronously and returns the result.

    Returns:
        result (dict): A dictionary containing the result from the executed tool function, the agent, the toolbox, and the tools_description.
    """

    agent = "multi_sample_info_retriever"

    AGENT = {
        "agent": agent,
        "role": "retrieves information for multiple samples from the database",
        "toolbox": functions_to_json(TOOLSET2)
    }
    try:
        # Call the async navigator handler
        next_tool, tool_args, justification, explanation = await async_navigator_handler(AGENT, state)
        print(f"Justification: {justification}\nExplanation: {explanation}")
        if tool_args:
            print(f"Tool args: {tool_args}")
        if next_tool ==  "get_metadata_by_uids":
            resource_type = "sample_metadata"
            tool_args = (tool_args.uid)
            print(f"Executing {next_tool} with args: {tool_args}")
            result = await TOOL_DISPATCH[next_tool](tool_args)
        elif next_tool == "get_uids_by_terms_and_field":
            resource_type = "UIDs"
            tool_args = (tool_args.key_string, tool_args.terms)
            print(f"Executing {next_tool} with args: {tool_args}")
            result = await TOOL_DISPATCH[next_tool](*tool_args)
        elif next_tool == "" and len(tool_args) == 0:
            response = ToolResponse(
                result=state.resources if state.resources else default_resource_box(),
                response="No tool was selected. Invalid query.",
                agent=agent,
                justification=justification,
                explanation=explanation
            )
            return response
                
        if result and result is not None:
            new_resource = {
                resource_type: result,
            }
            update_resource(state, new_resource)
            print(f"Updated resource: {state.resources}")

            response = ToolResponse(
                result=state.resources if state.resources else default_resource_box(),
                response=f"The {next_tool} tool has been executed successfully. The result is: ```json\n{result}\n```",
                agent=agent,
                justification=justification,
                explanation=explanation)
            # msg = [HumanMessage(content = response["result"] + "\n" + response["justification"] + "\n" + response["explanation"], name = "multi_sample_info_retriever")]
            # update_messages(state, msg)
            # print(list(response.keys()))
            return response
        else:
            print(f"No result from {next_tool}")
            return ToolResponse(
            result=state.resources if state.resources else default_resource_box(),
            response=f"No result was returned from {next_tool}",
            agent=agent,
            justification=justification,
            explanation=explanation
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        return ToolResponse(
            result=state.resources if state.resources else default_resource_box(),
            response=f"An error occurred: {e}",
            agent=agent,
            justification=justification,
            explanation=explanation
        )

async def multi_sample_info_retriever_node(state: ConversationState = INITIAL_STATE, tools = TOOLSET2, func = multi_sample_info)-> Command[Literal["supervisor", "validator"]]:
    """
    Asynchronously retrieves sample information using a specified function and updates the conversation state.

    Args:
        state (ConversationState): The current state of the conversation.
        tools (list): A list of tools to be used by the worker.
        func (callable): The function to be executed by the worker.

    Returns:
        Command[Literal["supervisor"]]: A command object with updated messages and resources, directing the flow to the supervisor.

    Raises:
        Exception: If any error occurs during the execution of the worker or invocation.
    """
    return await create_tool_call_node(state,tools,func,"multi_sample_info_retriever")
    # try:
    #     start_time = time.time()
    #     print("Creating worker...")
    #     multi_sample_info_retriever = await create_worker(tools,func)
    #     print(f"Worker created in {time.time() - start_time:.2f} seconds.")

    #     start_time = time.time()
    #     print("Invoking multi_sample_info_retriever...")
    #     result = await multi_sample_info_retriever.ainvoke(state)
    #     print(f"Invocation completed in {time.time() - start_time:.2f} seconds.")
    #     print(result)
    #     updated_messages = state.messages.append(HumanMessage(content=result["messages"][0].content, name="multi_sample_info_retriever"))
    #     # Update resources if the result contains a new_resource key
    #     if 'resources' in result:
    #         update_resource(state, result['resources'])
        
    #     print(f"Updated resources: {state.resources}")
    #     state.version += 1
    #     state.timestamp = datetime.now(timezone.utc)
    #     return Command(
    #         update={
    #             "messages": updated_messages,
    #             "version": state.version,
    #             "timestamp": state.timestamp.isoformat()
    #         },
    #         goto="supervisor",
    #     )
    # except Exception as e:
    #     error_msg = f"An error occurred while retrieving sample information: {e}"
    #     updated_messages = state.messages.append(HumanMessage(content=error_msg, name="multi_sample_info_retriever"))
    #     print(error_msg)
    #     return Command(
    #         update={
    #             "messages": updated_messages,
    #             "version": state.version,
    #             "timestamp": state.timestamp.isoformat()
    #         },
    #         goto="validator",
    #     )
    

if __name__ == "__main__":
    # asyncio.run(basic_sample_info())
    initial_state: ConversationState = {
        "messages": [
        # HumanMessage(content="Can you please list all the samples associated with the following scientist: 'Patricia Grace'?", name='user'),
        HumanMessage(content="What is the genotype for the mice with these UIDs: 'MUS-220124FOR-1' and 'MUS-220124FOR-73'?", name = 'user'),
        HumanMessage(content="Parsed User Query: ```json{'uid': ['MUS-220124FOR-1', 'MUS-220124FOR-73'], 'sampletype': 'mouse', 'assay': None, 'attribute': 'genotype', 'terms': None}```Justification: The query explicitly mentions UIDs, which are identifiers for specific samples, in this case, mice. The user is interested in the 'genotype' attribute of these samples, as indicated by the phrase 'What is the genotype'. The sample type is inferred to be 'mouse' based on the context of the UIDs and the mention of 'mice'. Explanation: The user query is asking for the genotype of specific mice identified by their UIDs. The UIDs provided are 'MUS-220124FOR-1' and 'MUS-220124FOR-73'. The query is focused on the 'genotype' attribute of these mice.", name = "query_parser")
        ],
        "resources": ResourceBox(
            sample_metadata=None, 
            db_schema=DBSchema(tables=[Table(name='seek_production.samples', columns=[Column(name='id', type='INTEGER', nullable=False, default=None, json_keys=None), Column(name='title', type='VARCHAR(255)', nullable=True, default=None, json_keys=None), Column(name='sample_type_id', type='INTEGER', nullable=True, default=None, json_keys=None), Column(name='json_metadata', type='TEXT', nullable=True, default=None, json_keys=['Concentration', 'Substrain', 'CellLineage', 'Notes', 'QC', 'ReagenCatalogNum', 'Reference', 'Type', 'Genotype', 'ValidationMethod', 'Publish_uri', 'TreatmentTime', 'Catalog#', 'RepositoryID', 'TotalProteinUnits', 'VolumeUnits', 'OrganDetail', 'Media', 'AntibodyParent', 'InstrumentUser', 'CollectionTime', 'Timepoint', 'Protocol_Stimulation', 'TreatmentTimeUnits', 'Checksum_PrimaryType', 'FlowAmountUnits', 'TreatmentDoseUnits', 'Treatment1Reference', 'StorageLocation', 'File_PrimaryData', 'Qtag', 'StorageSite', 'StorageTemperatureUnits', 'TreatmentDose', 'ReagentManufacturer', 'ValidationQuality', 'Protocol_Treatment', 'Treatment1Dose', 'Treatment2Reference', 'ODFrozen', 'Stain', 'Protocol', 'FMO', 'QC_notes', 'TotalProtein', 'Scientist', 'Treatment2DoseUnits', 'Treatment', 'UID', 'Note', 'TaxonomyID', 'Link_PrimaryData', 'Vendor', 'ConcentrationUnits', 'Checksum_PrimaryData', 'GramStaining', 'NumAliquot', 'Link_Sequence', 'BiosafetyLevel', 'Instrument', 'SampleCreationDate', 'Fixative', 'Lab', 'ODWavelength', 'PassageNum', 'TreatmentRoute', 'CellCount', 'TreatmentDoseTime', 'Repository', 'Reagent', 'BioSampleAccession', 'Name', 'Fixation', 'Species', 'Treatment2Dose', 'SourceFacility', 'StorageTemperature', 'Treatment1', 'SEEKSubmissionDate', 'Software', 'StorageType', 'CellLine', 'CollectionTimeUnits', 'Volume', 'Source', 'Organ', 'Morphology', 'InoculumPrep', 'Strain', 'TreatmentType', 'Treatment2', 'Phenotype', 'CompensationFCSParent', 'SubstrainReference', 'Path_PrimaryData', 'ReagentBrand', 'Culture', 'Treatment1DoseUnits', 'Parent', 'Stimulation', 'Barcode', 'FlowAmount']), Column(name='uuid', type='VARCHAR(255)', nullable=True, default=None, json_keys=None), Column(name='contributor_id', type='INTEGER', nullable=True, default=None, json_keys=None), Column(name='policy_id', type='INTEGER', nullable=True, default=None, json_keys=None), Column(name='created_at', type='DATETIME', nullable=False, default=None, json_keys=None), Column(name='updated_at', type='DATETIME', nullable=False, default=None, json_keys=None), Column(name='first_letter', type='VARCHAR(1)', nullable=True, default=None, json_keys=None), Column(name='other_creators', type='TEXT', nullable=True, default=None, json_keys=None), Column(name='originating_data_file_id', type='INTEGER', nullable=True, default=None, json_keys=None), Column(name='deleted_contributor', type='VARCHAR(255)', nullable=True, default=None, json_keys=None)])]), 
            parsed_query=ParsedQuery(uid=['MUS-220124FOR-1', 'MUS-220124FOR-73'], sampletype='mouse', assay=None, attribute='genotype', terms=None), st_attributes=None, 
            update_info=None,
            protocolURL=None, 
            sampleURL=None, 
            UIDs=None
        )
        # HumanMessage(content='Scientist', name='schema_mapper')],
    }
    # update_messages(INITIAL_STATE, initial_state["messages"])
    # update_resource(INITIAL_STATE, initial_state["resources"])
    INITIAL_STATE.messages.extend(initial_state["messages"])
    INITIAL_STATE.resources = initial_state["resources"]

    results = asyncio.run(multi_sample_info_retriever_node())
    # print(results)
