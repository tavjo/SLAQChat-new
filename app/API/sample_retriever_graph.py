# app/API/sample_retriever_graph.py

from fastapi import APIRouter, HTTPException, Request, Form, File, UploadFile
from typing import List
import logging
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
import os, sys, uuid, base64
from copy import deepcopy
from datetime import datetime, timezone

# Adjust project root directory if needed
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(project_root)

from src.chatbot.studio.helpers import handle_user_queries, initialize_logging

filename = os.path.basename(__file__)
logger = initialize_logging(log_file = filename)

# from src.chatbot.studio.sample_retriever import initialize_graph
from src.chatbot.studio.models import DeltaMessage, InputCSV
from src.chatbot.studio.prompts import INITIAL_STATE, CONFIG
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
# Global variable for the graph, accessible from your router if needed.
# GRAPH = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

def message_to_dict(message: BaseMessage) -> dict:
    """
    Convert a HumanMessage or any BaseMessage to a dictionary.
    Assumes that the message object has 'content' and 'name' attributes.
    """
    return {"content": message.content, "name": message.name}

# In-memory store for conversation states: session_id -> ConversationState
conversation_store = {}

# In-memory store for uploaded CSV files: session_id -> InputCSV
csv_store = {}

@router.post("/upload-csv/", response_model=InputCSV)
async def upload_csv(
    session_id: str = Form(...),
    file: UploadFile = File(...)
) -> InputCSV:
    """
    Receives a CSV file uploaded from the frontend.
    The file is read as bytes, encoded in base64, and stored as an InputCSV instance.
    """
    try:
        file_bytes = await file.read()
        # Encode the file bytes as a base64 string.
        encoded_content = base64.b64encode(file_bytes).decode('utf-8')
        timestamp = datetime.now(timezone.utc).isoformat()
        file_id = str(uuid.uuid4())
        input_csv = InputCSV(
            file_id=file_id,
            content=encoded_content,
            timestamp=timestamp,
            session_id=session_id
        )
        csv_store[session_id] = input_csv
        logger.info(f"Uploaded CSV stored for session {session_id} with file_id {file_id}")
        return input_csv
    except Exception as e:
        logger.error(f"Error uploading CSV: {e}")
        raise HTTPException(status_code=400, detail=f"CSV upload failed: {str(e)}")



@router.post("/invoke/", response_model=List[dict])
async def invoke_sample_retriever_graph(delta: DeltaMessage, request: Request) -> List[dict]:
    """
    Invoke the pre-compiled multi-agent graph using the provided conversation state.
    """
    logger.info(f"Received delta message: {delta}")

    # Retrieve the shared GRAPH from the app state
    graph = request.app.state.GRAPH

    config = CONFIG
    
    if graph is None:
        raise HTTPException(
            status_code=503,
            detail="Graph not initialized. Please wait for the service to complete startup."
        )
    
    try:
        # Determine the session id; if not provided, create a new one.
        session_id = delta.session_id or str(uuid.uuid4())
        logger.debug(f"Using session ID: {session_id}")
        
        # Retrieve existing conversation state or use a deepcopy of INITIAL_STATE.
        try:
            if session_id in conversation_store:
                state = conversation_store[session_id]
                logger.debug(f"Retrieved existing conversation state for session: {session_id}")
            else:
                state = deepcopy(INITIAL_STATE)
                state.session_id = session_id
                conversation_store[session_id] = state
                logger.debug(f"Created new conversation state for session: {session_id}")
        except Exception as state_error:
            logger.error(f"Error handling conversation state: {state_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to initialize or retrieve conversation state: {str(state_error)}"
            )
        
        # Append the new user input as a HumanMessage to the conversation state.
        try:
            # new_message = HumanMessage(content=delta.new_message, name="User")
            # state.messages.append(new_message)
            new_state = handle_user_queries(delta.new_message, state)
            new_state.version += 1
            new_state.timestamp = delta.timestamp
            logger.debug(f"Updated conversation state with new message")
        except Exception as message_error:
            logger.error(f"Error updating state with new message: {message_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to update conversation with new message: {str(message_error)}"
            )
        
        # If a CSV has been uploaded for this session, attach its reference.
        if session_id in csv_store:
            new_state.file_data = csv_store[session_id]
            logger.info(f"Attached CSV file (ID: {csv_store[session_id].file_id}) to conversation state for session {session_id}")
            # Optionally, remove the CSV from csv_store after attaching if you want one-time use.
            # del csv_store[session_id]

        # Save updated state back to the in-memory store.
        conversation_store[session_id] = new_state
        
        # Invoke the graph
        try:
            logger.info(f"Invoking GRAPH for session: {session_id}")
            result = await graph.ainvoke(new_state, config) # returns an instance of ConversationState
            logger.info(f"GRAPH invocation successful, received {len(result)} messages\n{result}")
        except Exception as graph_error:
            logger.error(f"Error during GRAPH invocation: {graph_error}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail=f"Graph processing failed: {str(graph_error)}"
            )
            
        # Convert each message to a dictionary for JSON serialization.
        try:
            json_serializable_messages = [message_to_dict(msg) for msg in result["messages"]]
            logger.debug(f"Successfully serialized {len(json_serializable_messages)} messages")
            logger.debug(f"Serialized messages: {json_serializable_messages}")

            # Clear the CSV file from the conversation state after response.
            if session_id in csv_store:
                del csv_store[session_id]
            new_state.file_data = None
            conversation_store[session_id] = new_state
            return json_serializable_messages
        except Exception as serialization_error:
            logger.error(f"Error serializing messages: {serialization_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to serialize response messages: {str(serialization_error)}"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        logger.error(f"Unexpected error in invoke_sample_retriever_graph: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
