# app/API/sample_retriever_graph.py

from fastapi import APIRouter, HTTPException
from typing import List
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
import os, sys
import uuid
from copy import deepcopy

# Adjust project root directory if needed
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

from src.chatbot.studio.sample_retriever import GRAPH
from src.chatbot.studio.models import ConversationState, DeltaMessage
from src.chatbot.studio.helpers import update_messages
from src.chatbot.studio.prompts import INITIAL_STATE
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

router = APIRouter()

# In-memory store for conversation states: session_id -> ConversationState
conversation_store = {}

@router.post("/invoke", response_model=List[BaseMessage])
async def invoke_sample_retriever_graph(delta: DeltaMessage):
    """
    Invoke the pre-compiled multi-agent graph using the provided conversation state.
    """
    try:
        # Determine the session id; if not provided, create a new one.
        session_id = delta.session_id or str(uuid.uuid4())
        # Retrieve existing conversation state or use a deepcopy of INITIAL_STATE.
        if session_id in conversation_store:
            state = conversation_store[session_id]
        else:
            state = deepcopy(INITIAL_STATE)
            state.session_id = session_id
            conversation_store[session_id] = state
        # Append the new user input as a HumanMessage to the conversation state.
        new_message = delta.new_message
        state.messages.append(new_message)
        state.version += 1
        state.timestamp = delta.timestamp

        # Save updated state back to the in-memory store.
        conversation_store[session_id] = state

        result = await GRAPH.ainvoke(state)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
