from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
from typing_extensions import Annotated, TypedDict, Sequence, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState
from langgraph.types import Command
import sys
import os
import dotenv

dotenv.load_dotenv()

# # Add the project root directory to the Python path
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
# sys.path.append(project_root)

# from backend.Tools.services.sample_service import retrieve_sample_info, fetchAllMetadata


class SummarizedOutput(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    # metadata: Dict[str, Any]

def summarize_sample_info(state: SummarizedOutput) -> Command[Literal["update_state"]]:
   """LLM call to summarize sample information

   Args:
      state (SummarizedOutput): messages from the previous workers

   Returns:
      (Command): command to update the state with the summary of sample information
   """
   try:
       llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
       sample_metadata = state["messages"]
       prompt = (
           "Please provide a concise and clear summary in a few sentences based solely on the data provided "
           f"in the following: {sample_metadata}. Avoid repeating the data verbatim and do not "
           "introduce additional information. If any information is unclear, feel free to ask the user for "
           "clarification. If the requested information cannot be retrieved, respond with: "
           "'I'm sorry, I couldn't find the information you're looking for.'"
           "Your output should be in the following format: "
           "Summary: [summary of sample information]"
       )
       messages = [{"role": "user", "content": prompt}]
       result = llm.invoke(messages)
       return Command(
           update={"messages": result, "name": "summarize_sample_info"}
       )
   except Exception as e:
       return f"An error occurred while summarizing sample information: {str(e)}"


def main():
    # Test the summarize_sample_info function
    # generate test sample metadata
    sample_metadata = {
        "patient_id": "P123456",
        "first_name": "John",
        "last_name": "Doe",
        "age": 45,
        "gender": "Male",
        "address": "123 Main St, Anytown, USA",
        "phone_number": "+1-555-1234",
        "email": "john.doe@example.com",
        "date_of_birth": "1978-05-15",
        "blood_type": "O+",
        "allergies": ["Peanuts", "Penicillin"],
        "current_medications": ["Aspirin", "Lisinopril"],
        "medical_history": ["Hypertension", "Diabetes"],
        "emergency_contact": {
            "name": "Jane Doe",
            "relationship": "Spouse",
            "phone_number": "+1-555-5678"
        },
        "insurance_provider": "HealthCare Inc.",
        "insurance_id": "HC123456789",
        "primary_physician": "Dr. Smith",
        "last_visit_date": "2023-09-01",
        "diagnosis": "Type 2 Diabetes",
        "treatment_plan": "Diet control and Metformin"
    }
    prompt = (
        f"Please provide a concise and clear summary in a few sentences based solely on the data provided: {sample_metadata}"
    )
    state = SummarizedOutput(messages=[HumanMessage(content=prompt)])
    try:
        result = summarize_sample_info(state)
        print("Summarize Sample Info Result:")
        print(result)
        print(result["messages"])
    except Exception as e:
        print(f"Error in summarize_sample_info: {e}")

if __name__ == "__main__":
    main()

