# chatbot_interface.py
import streamlit as st
from studio.sample_retriever import sampleRetrieverGraph
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
# checkpoint
import sqlite3
from dotenv import load_dotenv
# from langgraph.graph import MessagesState
import asyncio
import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from src.chatbot.studio.models import ConversationState

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


# In memory
conn = sqlite3.connect(":memory:", check_same_thread = False)
memory = SqliteSaver(conn)


async def run_agent_chatbot():
    st.title("💬 NExtSEEK Chatbot")
    st.caption("🚀 Interact with the NExtSEEK AI assistant powered by LangGraph and OpenAI.")
    
    # Sidebar with documentation link
    with st.sidebar:
        st.sidebar.markdown("[Review NExtSEEK documentation](https://koch-institute-mit.gitbook.io/mit-data-management-analysis-core)")

    # Initialize session state for conversation
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display existing conversation
    for speaker, message in st.session_state.conversation:
        st.chat_message(speaker.lower()).write(message)

    # Input for user query
    user_input = st.chat_input(placeholder="e.g., Which NHP has this UID: NHP-220630FLY-15?")

    if user_input:
        messages = [HumanMessage(content=user_input)]
        initial_state: ConversationState = {"messages": messages}
        # Add user input to the conversation state
        st.session_state.conversation.append(("User", user_input))
        st.chat_message("user").write(user_input)

        # Create a HumanMessage and invoke the graph
        # config={"configurable":  {"thread_id": "1"}}
        # result = graph.invoke({"messages": messages}, config)
        graph = sampleRetrieverGraph(state = initial_state)
        result = await graph.ainvoke({"messages": messages})

        # Extract and display AI response
        if "messages" in result and len(result["messages"]) > 1:
            ai_message = result["messages"][-1]
            st.session_state.conversation.append(("SLAQ", ai_message.content))
            st.chat_message("assistant").write(ai_message.content)
        else:
            error_message = "Error: No response received."
            st.session_state.conversation.append(("SLAQ", error_message))
            st.chat_message("assistant").write(error_message)

if __name__ == "__main__":
    asyncio.run(run_agent_chatbot())
