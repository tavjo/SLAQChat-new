# chatbot_interface.py
import streamlit as st
from dotenv import load_dotenv
import asyncio
import sys, os, base64, io
# from io import StringIO
from datetime import datetime, timezone
import aiohttp  # For async HTTP requests
import uuid
import pandas as pd

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
output_dir = "assets"  # This folder is no longer used for file storage

# ---------------------------------------------------------------------------
# NEW FUNCTION: Asynchronous file uploader using form-data
#
# This function takes the in-memory uploaded file from Streamlit and sends it
# to the backend endpoint using form-data. Note that the backend must have a
# corresponding endpoint (e.g., /upload-csv/) that accepts an UploadFile.
# ---------------------------------------------------------------------------

def check_uploaded_file(uploaded_file):
    # decoded_content = base64.b64decode(uploaded_file.getvalue()).decode('utf-8')
    # Convert the decoded content to a pandas DataFrame
    df = pd.read_csv(io.BytesIO(uploaded_file.getvalue()))
    if df.columns[0] != "UID":
        st.error("First column must be UID")
        return False
    return True

async def upload_file_to_backend(uploaded_file, session_id):
    backend_url = "http://backend:8000/sampleretriever/upload-csv/"
    data = aiohttp.FormData()
    # 'file' is the field name expected by the FastAPI endpoint.
    data.add_field("session_id", session_id)
    data.add_field(
        "file",
        uploaded_file.getvalue(),  # Get the bytes of the file
        filename=uploaded_file.name,
        content_type=uploaded_file.type
    )
    async with aiohttp.ClientSession() as session:
        async with session.post(backend_url, data=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                st.success("CSV file uploaded successfully to backend.")
                return result
            else:
                error = await resp.text()
                st.error(f"Upload error: {resp.status} - {error}")
                return None

# ---------------------------------------------------------------------------
# UPDATED setup_ui():
#
# - The file uploader now only captures the CSV file in memory.
# - We removed the local save to assets directory.
# - The function now returns the uploaded file alongside user input and session info.
# ---------------------------------------------------------------------------
def setup_ui():
    st.title("💬 NExtSEEK-Chat")
    st.caption("🚀 Interact with the NExtSEEK AI assistant to answer questions about your data.")

    # File uploader widget for CSV files (the file is kept in memory)
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv", key="csv_upload")
    if uploaded_file is not None:
        st.success("CSV file selected and ready for upload.")

    # Initialize session state for conversation
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display existing conversation
    for speaker, message in st.session_state.conversation:
        st.chat_message(speaker.lower()).write(message)

    # Set a unique session ID and version for the conversation
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.version = 1

    user_input = st.chat_input(placeholder="e.g., Tell me more about sample NHP-220630FLY-15?")
    return uploaded_file, user_input, st.session_state.session_id, st.session_state.version

# ---------------------------------------------------------------------------
# Your existing function to communicate with the backend chatbot endpoint
# ---------------------------------------------------------------------------
async def run_agent_chatbot(user_input: str, session_id: str, version: int):
    delta = {
        "session_id": session_id,
        "new_message": user_input,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": version
    }
    print("Sending delta as dict:", delta)
    backend_url = "http://backend:8000/sampleretriever/invoke/"
    timeout = aiohttp.ClientTimeout(total=600)  # 10 minute timeout

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(backend_url, json=delta) as response:
                if response.status == 200:
                    result = await response.json()
                    print("Received result:", result)
                    return result
                else:
                    error_msg = await response.text()
                    st.error(f"Backend error: {response.status} - {error_msg}")
                    return {}
    except asyncio.TimeoutError:
        st.error("Request timed out. Please try again.")
        return {}
    except aiohttp.ClientError as e:
        st.error(f"Connection error: {str(e)}")
        return {}

def display_user_input(user_input):
    st.chat_message("user").write(user_input)
    st.session_state.conversation.append(("User", user_input))

def display_ai_response(result):
    if result:
        ai_message = result[-1]["content"]
        st.session_state.conversation.append(("SLAQ", ai_message))
        return st.chat_message("assistant").write(ai_message)
    else:
        error_message = "Error: No valid response received."
        st.session_state.conversation.append(("SLAQ", error_message))
        return st.chat_message("assistant").write(error_message)

# ---------------------------------------------------------------------------

def remove_uploaded_file():
    # clear the uploaded file from the session state
    st.session_state.uploaded_file = None

# ---------------------------------------------------------------------------
# run_all() now integrates the file upload functionality:
#
# 1. Calls setup_ui() to get the uploaded CSV and chat message.
# 2. If a CSV file is provided, it immediately calls upload_file_to_backend().
# 3. Proceeds with sending the chat message to the backend.
# ---------------------------------------------------------------------------
async def run_all():
    uploaded_file, user_input, session_id, version = setup_ui()
    
    # If a file is selected, upload it to the backend
    if uploaded_file is not None and check_uploaded_file(uploaded_file):
        # Await the file upload before processing chat messages
        upload_result = await upload_file_to_backend(uploaded_file, session_id)
        # Optionally, you can check 'upload_result' for further processing or error handling.
        remove_uploaded_file()
    
    # Process the chat input if provided
    if user_input and session_id:
        display_user_input(user_input)
        with st.spinner('Thinking...'):
            result = await run_agent_chatbot(user_input, session_id, version)
        display_ai_response(result)

if __name__ == "__main__":
    asyncio.run(run_all())
