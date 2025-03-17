# chatbot_interface.py
import streamlit as st
# from studio.sample_retriever import GRAPH
# from langchain_core.messages import HumanMessage
# from studio.helpers import handle_user_queries
from studio.prompts import INITIAL_STATE
# from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
# checkpoint
# import aiosqlite
from dotenv import load_dotenv
# from langgraph.graph import MessagesState
import asyncio
import sys,os
# import time
from datetime import datetime, timezone
# from copy import deepcopy
import aiohttp  # Add this import for async HTTP requests
import uuid
import pandas as pd

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

from src.chatbot.studio.models import DeltaMessage, ConversationState

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
output_dir = os.path.join(project_root, "src/chatbot/assets/")

def check_uploaded_file():
    if os.path.exists(os.path.join(output_dir, "input.csv")):
        # make sure first column is UID
        df = pd.read_csv(os.path.join(output_dir, "input.csv"))
        if df.columns[0] != "UID":
            st.error("First column must be UID")
            return False
        return True
    else:
        st.error("No file uploaded")
        return False


def setup_ui(state: ConversationState = INITIAL_STATE):
    st.title("💬 NExtSEEK-Chat")
    st.caption("🚀 Interact with the NExtSEEK AI assistant to answer questions about your data.")

    # File uploader widget for CSV files
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv", key="csv_upload")
    if uploaded_file is not None:
        # Save the uploaded file as "input.csv" in the current directory
        with open(os.path.join(output_dir, "input.csv"), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("File uploaded and saved as input.csv")
    
    # Initialize session state for conversation
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display existing conversation
    for speaker, message in st.session_state.conversation:
        st.chat_message(speaker.lower()).write(message)

    # if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

    user_input = st.chat_input(placeholder="e.g., Tell me more about sample NHP-220630FLY-15?")
        # if "version" not in st.session_state:
    st.session_state.version = state.version
    return user_input, st.session_state.session_id, st.session_state.version

async def run_agent_chatbot(user_input: str, session_id: str, version: int):
    # user_message = HumanMessage(content=user_input, name="User")
    delta = DeltaMessage(
        session_id=session_id,
        new_message=user_input,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=version)
    print("Sending delta as dict:", delta.model_dump())
    backend_url = "http://127.0.0.1:8000/sampleretriever/invoke/"
    async with aiohttp.ClientSession() as session:
        async with session.post(backend_url, json=delta.model_dump()) as response:
            if response.status == 200:
                result = await response.json()
                print("Received result:", result)
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
    if result:
        # ai_message = result["messages"][-1].content
        ai_message = result[-1]["content"]
        st.session_state.conversation.append(("SLAQ", ai_message))
        clear_assets()
        return st.chat_message("assistant").write(ai_message)
    else:
        error_message = "Error: No valid response received."
        st.session_state.conversation.append(("SLAQ", error_message))
        clear_assets()
        return st.chat_message("assistant").write(error_message)
    
# clear assets folder once conversation is complete
def clear_assets():
    if os.path.exists(os.path.join(output_dir, "input.csv")):
        os.remove(os.path.join(output_dir, "input.csv"))

async def run_all():
    user_input, session_id, version = setup_ui()
    result = None
    if user_input and session_id:
        # new_session_id = str(uuid.uuid4())
        # st.session_state.session_id = new_session_id  # update session_state with new id
        display_user_input(user_input)
        result = await run_agent_chatbot(user_input, session_id, version)
    if result:
        display_ai_response(result)
    clear_assets()


if __name__ == "__main__":
    asyncio.run(run_all())
