from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import START, StateGraph, MessagesState, END
from langgraph.prebuilt import tools_condition, ToolNode, tool, create_react_agent
from typing import List, Callable
from pydantic import BaseModel
from langgraph.checkpoint.sqlite import SqliteSaver
import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.services.sample_service import get_sample_name, fetch_protocol, retrieve_sample_info, fetchChildren, fetch_all_descendants, fetchAllMetadata, add_links

# import env variables
from dotenv import load_dotenv
load_dotenv()

# checkpoint
memory = SqliteSaver.from_conn_string(":memory:")

class MultiAgentState(BaseModel, MessagesState):
   messages: MessagesState # contains the messages from the previous agents including the original user query
   agent_name: str # name of current agent
   status: str # status of current agent
   next_agent: str # name of next agent



########################################################
# Tools
########################################################

# defining a tool with `content_and_artifact` return
@tool(parse_docstring=True, response_format="content_and_artifact")
def redirect_tool(
    agent_name: str, 
) -> dict:
    """A tool that redirects to a specific agent.
    
    Args:
        agent_name: Name of the agent to redirect to.
    """
    # Returning a text response and updated value for the state
    return f"You will be redirected to {agent_name}", {'current_route': agent_name}

def summarize_sample_info(sample_uid: str) -> dict:
   """LLM call to summarize sample information

   Args:
      sample_uid (str): sample UID that will be used to retrieve sample information from the database

   Returns:
      (dict): summary of sample information
   """
   try:
       llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
       sample_metadata = retrieve_sample_info(sample_uid)
       if not sample_metadata:
           raise ValueError("No sample metadata found.")
       prompt = (
           "Please provide a concise and clear summary in a few sentences based solely on the data provided "
           f"in the following dictionary: {sample_metadata[0]}. Avoid repeating the data verbatim and do not "
           "introduce additional information. If any information is unclear, feel free to ask the user for "
           "clarification. If the requested information cannot be retrieved, respond with: "
           "'I'm sorry, I couldn't find the information you're looking for.'"
       )
       message = HumanMessage(content=prompt)
       result = llm.invoke(message)
       formatted_result = result.content
       return AIMessage(content=formatted_result)
   except Exception as e:
       return f"An error occurred while summarizing sample information: {str(e)}"

def summarize_all_metadata_info(sample_uid: str, filter: List[str] = None) -> str:
   """LLM call to summarize metadata information for all descendants of a sample

   Args:
      sample_uid (str): sample UID that will be used to retrieve metadata information from the database for all descendants of the sample
      filter (List[str], optional): list of uid patterns to filter the metadata information by to retrieve only the metadata information for the descendants that match the patterns
   
   Returns:
      (str): summary of metadata information
   """
   try:
       llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
       all_metadata = fetchAllMetadata(sample_uid, filter)
       if not all_metadata:
           raise ValueError("No metadata found for the given sample UID.")
       prompt = (
           "Please provide a concise and clear summary in a few sentences based solely on the data provided "
           f"in the following dictionary: {all_metadata}. Avoid repeating the data verbatim and do not "
           "introduce additional information. If any information is unclear, feel free to ask the user for "
           "clarification. If the requested information cannot be retrieved, respond with: "
           "'I'm sorry, I couldn't find the information you're looking for.'"
       )
       message = HumanMessage(content=prompt)
       result = llm.invoke(message)
       formatted_result = result.content
       return AIMessage(content=formatted_result)
   except Exception as e:
       return f"An error occurred while summarizing metadata information: {str(e)}"


toolset1 = [get_sample_name, retrieve_sample_info]

toolset2 = [fetchChildren, fetch_all_descendants, fetchAllMetadata]

toolset3 = [summarize_sample_info, summarize_all_metadata_info]
# toolset3 = [summarize_all_metadata_info]
# toolset3 = [summarize_sample_info]

toolset4 = [add_links, fetch_protocol]

########################################################
# LLMs with bound tools
########################################################

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

llm_with_toolset1 = llm.bind_tools(toolset1)
llm_with_toolset2 = llm.bind_tools(toolset2)
llm_with_toolset3 = llm.bind_tools(toolset3)
llm_with_toolset4 = llm.bind_tools(toolset4)


# System messages
sys_msg = SystemMessage(content=f"You are a helpful assistant tasked with retrieving and summarizing information about samples from a database that stores metadata about research samples and data according to FAIR data principles and NIH standards. You will be given a sample UID and you will use the tools provided to consolidate the relevant information and summarize it for the user. If you are not sure about the information, you can ask the user for clarification. You are responsible for juggling the agents provided as the means by which to retrieve the answer to the user's query. Be sure to parse the responses from each agent thoroughly and carefully in order to craft the appropriate response. If you are asked for specific information about a sample, use only the tools necessary to answer the question. For instance, if you are asked for the name of a sample use 'agent1' and 'agent4' toolsets only. If you are asked for information about a sample, use 'agent1', 'agent3', and 'agent4' only. You should always use 'agent4' to generate the link to the sample page on the NExtSEEK website so that it can be included in your response unless an invalid query is made. An invalid query can include asking for information about a sample that does not exist in the database or not providing a sample UID at all. In this case, you should direct them to the NExtSEEK website (https://nextseek.mit.edu/) to get more information. Lastly, if you are unable to retrieve the requested information, please say: 'I'm sorry, I couldn't find the information you're looking for.")

# Toolset 1: Retrieve sample name and information
# sys_msg for toolset 1
msg1 = f"You are a helpful assistant tasked with retrieving and summarizing information about samples from a database that stores metadata about research samples and data according to FAIR data principles and NIH standards. You will be given a sample UID and you will use the tools provided to retrieve the relevant information. Depending on the user query, you will choose to either retrieve the sample name or the sample information. If you are asked for the sample name, use the retrieve_sample_name tool. If you are asked for information about a sample, use the retrieve_sample_info tool. You should use the answer given by the tools utilized unless the query returns an error or empty list. For instance, when asked for the name of a sample, you should provide the name given by the database after running the appropriate query unless the query returns an error or empty list.  Your output should match the expected output of the tool used. That means if you use the retrieve_sample_name tool, your output should be a string containing the sample name. If you use the retrieve_sample_info tool, your output should be a dictionary containing the sample information. Lastly, if you are unable to retrieve the requested information, return an empty dictionary."

agent1 = create_react_agent(llm_with_toolset1, state_modifier=msg1, checkpointer=memory)

# def agent1(state: MessagesState) -> str | dict:
#     """Invoke the LLM with toolset1 to retrieve and summarize sample information.

#     This function uses a language model with a specific toolset to process messages
#     related to retrieving and summarizing information about samples from a database.
#     The database stores metadata about research samples and data according to FAIR
#     data principles and NIH standards.

#     Args:
#         state (MessagesState): The current state containing messages to be processed.

#     Returns:
#         str | dict: A string containing the sample name or a dictionary containing the sample information.

#     The function decides whether to retrieve the sample name or the sample information
#     based on the user query. It uses the `retrieve_sample_name` tool for sample names
#     and the `retrieve_sample_info` tool for sample information. The function provides
#     the answer given by the database unless the query returns an error or an empty list.
#     If the requested information cannot be retrieved, it returns an empty dictionary.'
#     """
#     result = llm_with_toolset1.invoke([msg1] + state["messages"])
#    #  formatted_result = result.content
#     return result

# Toolset 2: Retrieve children, descendants, and sample metadata for all or a subset of descendants

# sys_msg for toolset 2
msg2 = f"You are a helpful assistant tasked with summarizing information about children, descendants, and associated metadata for a given sample from a database that stores metadata about research samples and data according to FAIR data principles and NIH standards. You will be given a sample UID and you will use the tools provided to retrieve the relevant information. Depending on the user query, you will choose to either retrieve the children of that sample, all descendants of the sample, and/or metadata about the descendants of that sample. You should use the answer given by the database unless the query returns an error or empty list. Your output should match the expected output of the tool used. That means if you use the fetchChildren tool, your output should be a list of dictionaries containing the children of the sample. If you use the fetch_all_descendants tool, your output should be a list containing the descendants of the sample. If you use the fetchAllMetadata tool, your output should be a list of dictionaries containing the metadata for the descendants of the sample. Lastly, if you are unable to retrieve the requested information, return an empty dictionary."

agent2 = create_react_agent(llm_with_toolset2, state_modifier=msg2, checkpointer=memory)

# def agent2(state: MessagesState)-> dict:
#     """Invoke the LLM with toolset2 to retrieve and summarize information about children, descendants, and associated metadata.

#     This function uses a language model with a specific toolset to process messages
#     related to retrieving and summarizing information about children, descendants,
#     and associated metadata for a given sample from a database. The database stores
#     metadata about research samples and data according to FAIR data principles and
#     NIH standards.

#     Args:
#         state (MessagesState): The current state containing messages to be processed.

#     Returns:
#         dict: A dictionary containing the structured output of the tool used.

#     The function decides whether to retrieve the children of a sample, all descendants,
#     and/or metadata about the descendants based on the user query. It provides the
#     answer given by the database unless the query returns an error or an empty list.
#     If the requested information cannot be retrieved, it returns an empty dictionary.
#     """
#     result = llm_with_toolset2.invoke([msg2] + state["messages"])
#     return result


# Toolset 3: Summarize sample information and metadata for all or a subset of descendants

# sys_msg for toolset 3
msg3 = f"You are a helpful assistant tasked with summarizing information about samples and their associated metadata from a database that stores metadata about research samples and data according to FAIR data principles and NIH standards. You will be given a sample UID and you will use the tools provided to retrieve the relevant information. Depending on the user query, you will choose to either summarize the sample information or the metadata for all or a subset of descendants of that sample. For instance, if the user asks for only the tissue descendants of a sample, you should use the filter parameter in the summarize_all_metadata_info tool to retrieve only the metadata information for the descendants that match the tissue pattern. If the user only asks for the sample information, you should use the summarize_sample_info tool. You should use the answer given by the database unless the query returns an error or empty list. Your output should match the expected output of the tool used. That means if you use the summarize_all_metadata_info tool, your output should be a dictionary containing the metadata information for all descendants of the sample. If you use the summarize_sample_info tool, your output should be a string containing the sample information. Lastly, if you are unable to retrieve the requested information, please return an empty dictionary."

agent3 = create_react_agent(llm_with_toolset3, state_modifier=msg3, checkpointer=memory)

# def agent3(state: MessagesState)-> str | dict:
#     """Invoke the LLM with toolset3 to summarize sample information and metadata.

#     This function uses a language model with a specific toolset to process messages
#     related to summarizing information about samples and their associated metadata
#     from a database. The database stores metadata about research samples and data
#     according to FAIR data principles and NIH standards.

#     Args:
#         state (MessagesState): The current state containing messages to be processed.

#     Returns:
#         str | dict: A string containing the processed summary or an empty dictionary if the information cannot be retrieved.

#     The function decides whether to summarize the sample information or the metadata
#     for all or a subset of descendants based on the user query. For instance, if the
#     user asks for only the tissue descendants of a sample, it uses the filter parameter
#     in the summarize_all_metadata_info tool to retrieve only the metadata information
#     for the descendants that match the tissue pattern. If the user only asks for the
#     sample information, it uses the summarize_sample_info tool. The function provides
#     the answer given by the database unless the query returns an error or an empty list.
#     If the requested information cannot be retrieved, it returns an empty dictionary.
#     """
#     result = llm_with_toolset3.invoke([msg3] + state["messages"])
#    #  formatted_result = result.content
#     return result

# Toolset 4: Add links to sample and protocol pages

msg4 = f"You are a helpful assistant tasked with adding links to sample and protocol uids from a database that stores metadata about research samples and data according to FAIR data principles and NIH standards. You will be given a sample UID and you will use the tools provided to create the links based on the user query. Depending on the user query, you will choose to either add a link that points to the sample's page on the NExtSEEK website or to the protocol associated with the sample. Whenever the user asks for a sample name or information, use 'add_links' to add a link that points to the sample's page on the NExtSEEK website. This should always be included with your response when asked about a sample. If the user asks directly for a protocol associated with a given sample, you should use 'fetch_protocol' to provide a link that allows the user to download the protocol. You should use the answer given by the database unless the query returns an error or empty list. Your output should match the expected output of the tool used. Lastly, if you are unable to retrieve the requested information, return an empty dictionary."

agent4 = create_react_agent(llm_with_toolset4, state_modifier=msg4, checkpointer=memory)

# def agent4(state: MessagesState)-> str | dict:
#     """Invoke the LLM with toolset4 to add links to sample and protocol pages.

#     This function uses a language model with a specific toolset to process messages
#     related to adding links to sample and protocol UIDs from a database. The database
#     stores metadata about research samples and data according to FAIR data principles
#     and NIH standards.

#     Args:
#         state (MessagesState): The current state containing messages to be processed.

#     Returns:
#         str | dict: A string containing the relevant link; or a dictionary of strings containing the sample link and protocol link; or an empty dictionary if the information cannot be retrieved.

#     The function decides whether to add a link to the sample's page on the NExtSEEK
#     website or to the protocol associated with the sample based on the user query.
#     Whenever the user asks for a sample name or information, it uses the 'add_links'
#     tool to add a link to the sample's page on the NExtSEEK website. If the user asks
#     directly for a protocol associated with a given sample, it uses 'fetch_protocol'
#     to provide a link for downloading the protocol. The function provides the answer
#     given by the database unless the query returns an error or an empty list. If the
#     requested information cannot be retrieved, it returns an empty dictionary.
#     """
#     result = llm_with_toolset4.invoke([msg4] + state["messages"])
#    #  formatted_result = result.content
#     return result

# master_toolset = [agent1, agent2, agent3, agent4]

# define overseer agent
overseer_agent = ChatOpenAI(model="gpt-4o", temperature=0.2)
# overseer_with_agents = overseer_agent.bind_tools(master_toolset)

def overseer(state: MultiAgentState):
   return {"messages": [overseer_agent.invoke([sys_msg] + state["messages"])]}

def agent_router(state: MultiAgentState):
    
    pass

# Build graph
builder = StateGraph(MultiAgentState)
builder.add_node("assistant", overseer)
builder.add_node("agent1", agent1)
builder.add_node("tools1", ToolNode(toolset1))
builder.add_node("agent2", agent2)
builder.add_node("tools2", ToolNode(toolset2))
builder.add_node("agent3", agent3)
builder.add_node("tools3", ToolNode(toolset3))
builder.add_node("agent4", agent4)
builder.add_node("tools4", ToolNode(toolset4))
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    "agent1",
)
builder.add_edge("agent1", "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    "agent2",
)
builder.add_edge("agent2", "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    "agent3",
)
builder.add_edge("agent3", "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    "agent4",
)
builder.add_edge("agent4", "assistant")
builder.add_conditional_edges(
    "agent1",
    tools_condition,
)
builder.add_conditional_edges(
    "agent2",
    tools_condition,
)
builder.add_conditional_edges(
    "agent3",
    tools_condition,
)
builder.add_conditional_edges(
    "agent4",
    tools_condition,
)
# builder.add_edge("tools", "assistant")
builder.add_edge("tools1", "agent1")
builder.add_edge("tools2", "agent2")
builder.add_edge("tools3", "agent3")
builder.add_edge("tools4", "agent4")
builder.add_edge("assistant", END)

# Compile graph
graph = builder.compile()
