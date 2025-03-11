# chatbot_interface.py
import streamlit as st
# from studio.sample_retriever import sampleRetrieverGraph
from langchain_core.messages import HumanMessage
# from studio.helpers import update_messages, get_messages
# from studio.prompts import INITIAL_STATE
# from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
# checkpoint
# import aiosqlite
# from dotenv import load_dotenv
# from langgraph.graph import MessagesState
import asyncio
import sys,os
# import time
from datetime import datetime, timezone
# from copy import deepcopy
import aiohttp  # Add this import for async HTTP requests
import uuid


# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

# from src.chatbot.studio.models import ConversationState

# load_dotenv()
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
output_dir = os.path.join(project_root, "src/chatbot/assets/")



def setup_ui():
    st.title("💬 NExtSEEK-Chat")
    st.caption("🚀 Interact with the NExtSEEK AI assistant to answer questions about your data.")

        # Initialize session state for conversation
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display existing conversation
    for speaker, message in st.session_state.conversation:
        st.chat_message(speaker.lower()).write(message)

    # File uploader widget for CSV files
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv", key="csv_upload")
    if uploaded_file is not None:
        # Save the uploaded file as "input.csv" in the current directory
        with open(os.path.join(output_dir, "input.csv"), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("File uploaded and saved as input.csv")

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    user_input = st.chat_input(placeholder="e.g., Tell me more about sample NHP-220630FLY-15?")
    return user_input, st.session_state.session_id

async def run_agent_chatbot(user_input: str, session_id: str):
    user_message = HumanMessage(content=user_input, name="User")
    delta = {
        "session_id": session_id,
        "new_message": user_message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    backend_url = "http://127.0.0.1:8000/sampleretriever/invoke"
    async with aiohttp.ClientSession() as session:
        async with session.post(backend_url, json=delta) as response:
            if response.status == 200:
                result = await response.json()
                return result
            else:
                st.error(f"Backend error: {response.status}")
                return {}

def display_user_input(user_input):
    # Add user input to the conversation state
    st.chat_message("user").write(user_input)
    return st.session_state.conversation.append(("User", user_input))

def display_ai_response(result):      
    # Extract and display AI response
    if "messages" in result:
        ai_message = result["messages"][-1].content
        st.session_state.conversation.append(("SLAQ", ai_message))
        return st.chat_message("assistant").write(ai_message)
    else:
        error_message = "Error: No valid response received."
        st.session_state.conversation.append(("SLAQ", error_message))
        return st.chat_message("assistant").write(error_message)

async def run_all():
    user_input, session_id = setup_ui()
    if user_input and session_id:
        display_user_input(user_input)
        result = await run_agent_chatbot(user_input, session_id)
    if result:
        display_ai_response(result)        

if __name__ == "__main__":
    asyncio.run(run_all())
