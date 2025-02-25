# chatbot_interface.py
import streamlit as st
from studio.sample_retriever import sampleRetrieverGraph
from langchain_core.messages import HumanMessage
from studio.helpers import update_messages, get_messages
from studio.prompts import INITIAL_STATE
# from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
# checkpoint
# import aiosqlite
from dotenv import load_dotenv
# from langgraph.graph import MessagesState
import asyncio
import sys
import os
import time
from copy import deepcopy

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

# from src.chatbot.studio.models import ConversationState

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

from copy import deepcopy

async def run_agent_chatbot():
    st.title("💬 NExtSEEK Chatbot")
    st.caption("🚀 Interact with the NExtSEEK AI assistant powered by LangGraph, BAML, and OpenAI.")
    
    # Sidebar with documentation link
    with st.sidebar:
        st.sidebar.markdown("[Review NExtSEEK documentation](https://koch-institute-mit.gitbook.io/mit-data-management-analysis-core)")
        st.sidebar.markdown("[Install your own instance of NExtSEEK](https://github.com/BMCBCC/NExtSEEK)")
        st.sidebar.markdown("[Visit our website for more information](https://www.nextseek.mit.edu/)")
    
    # if "memory" not in st.session_state:
    # # In memory
    #     st.session_state["conn"] = aiosqlite.connect(":memory:", check_same_thread = False)
    #     st.session_state["memory"] = AsyncSqliteSaver(st.session_state["conn"])
    
    # memory = st.session_state["memory"]

    # Initialize session state for conversation
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display existing conversation
    for speaker, message in st.session_state.conversation:
        st.chat_message(speaker.lower()).write(message)

    # Input for user query
    user_input = st.chat_input(placeholder="e.g., Tell me more about sample NHP-220630FLY-15?")

    if user_input:
        # Add user input to the conversation state
        st.session_state.conversation.append(("User", user_input))
        st.chat_message("user").write(user_input)
        
        # Create a fresh state for each query by copying the initial state
        fresh_state = deepcopy(INITIAL_STATE)
        messages = [HumanMessage(content=user_input, name="user")]
        update_messages(fresh_state, messages)
        graph = sampleRetrieverGraph()

        # Create a HumanMessage and invoke the graph
        # config={"configurable":  {"thread_id": "1"}}
        start_time = time.time()
        result = await graph.ainvoke(fresh_state)
        print(f"Total time taken: {time.time() - start_time:.2f} seconds")

            # Debug: print the result structure
        # print("Result structure:", result)
        # if "messages" in result:
        #     print("Messages in result:", result["messages"])
        #     for i, msg in enumerate(result["messages"]):
        #         print(f"Message {i}: {msg}")

        # Extract and display AI response
        if "messages" in result:
            ai_message = result["messages"][-1].content
            st.session_state.conversation.append(("SLAQ", ai_message))
            st.chat_message("assistant").write(ai_message)
        else:
            error_message = "Error: No valid response received."
            st.session_state.conversation.append(("SLAQ", error_message))
            st.chat_message("assistant").write(error_message)

if __name__ == "__main__":
    asyncio.run(run_agent_chatbot())
