# src/chatbot/studio/helpers.py
# import asyncio
from src.chatbot.baml_client.async_client import b
from typing import Optional

async def async_navigator_handler(
    agent: str,
    toolbox: list[str],
    tools_description: dict[str, str],
    user_query: str,
    summedMessages: Optional[list[str]]
):
    """
    Asynchronously handles navigation using the BAML client.

    Parameters:
    - agent (str): The agent identifier.
    - toolbox (list[str]): A list of tool names available for navigation.
    - tools_description (dict[str, str]): A dictionary mapping tool names to their descriptions.
    - user_query (str): The user's query to be processed.
    - summedMessages (Optional[list[str]]): A list of previous messages to be considered.

    Returns:
    - tuple: A tuple containing the next tool to use and its arguments.

    Raises:
    - Exception: If an error occurs during the navigation process.
    """
    try:
        # Call the BAML Navigate function asynchronously.
        nav_stream = b.stream.Navigate(agent, toolbox, tools_description, user_query, summedMessages)
        
        # Await the final, fully parsed response.
        nav_response = await nav_stream.get_final_response()
        
        # Extract the tool choice and its argument.
        next_tool = nav_response.next_tool
        tool_args = nav_response.tool_args
        return next_tool, tool_args
    except Exception as e:
        # Log the exception or handle it as needed
        print(f"An error occurred during navigation: {e}")
        raise


# Example usage:
# (Make sure to run this inside an async event loop)
# result = await async_navigator_handler(
#     agent="AgentX",
#     toolbox=["fetch_any_sample", "another_tool"],
#     tools_description={"fetch_any_sample": "Fetch sample metadata", "another_tool": "Another tool description"},
#     user_query="Get sample with UID 1234",
#     summedMessages=["Previous message 1", "Previous message 2"]
# )
# print(result)