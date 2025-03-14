# app/API/sample_retriever_graph.py

from fastapi import APIRouter, HTTPException
from typing import List
import logging
from langchain_core.messages import HumanMessage, BaseMessage
from dotenv import load_dotenv
import os, sys
import uuid
from copy import deepcopy

# Adjust project root directory if needed
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

from src.chatbot.studio.sample_retriever import GRAPH
from src.chatbot.studio.models import DeltaMessage
# from src.chatbot.studio.helpers import update_messages
from src.chatbot.studio.prompts import INITIAL_STATE
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

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

@router.post("/invoke", response_model=List[dict])
async def invoke_sample_retriever_graph(delta: DeltaMessage) -> List[dict]:
    """
    Invoke the pre-compiled multi-agent graph using the provided conversation state.
    """
    logger.info(f"Received delta message: {delta}")
    
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
            new_message = HumanMessage(content=delta.new_message, name="User")
            state.messages.append(new_message)
            state.version += 1
            state.timestamp = delta.timestamp
            logger.debug(f"Updated conversation state with new message")
        except Exception as message_error:
            logger.error(f"Error updating state with new message: {message_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to update conversation with new message: {str(message_error)}"
            )

        # Save updated state back to the in-memory store.
        conversation_store[session_id] = state
        
        # Invoke the graph
        try:
            logger.info(f"Invoking GRAPH for session: {session_id}")
            result = await GRAPH.ainvoke(state) # returns an instance of ConversationState
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
