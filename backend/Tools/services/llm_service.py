from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
import sys
import os
import dotenv

dotenv.load_dotenv()

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.services.sample_service import retrieve_sample_info, fetchAllMetadata


class SummarizedOutput(BaseModel):
    summary: str
    # metadata: Dict[str, Any]

def summarize_sample_info(sample_uid: str) -> SummarizedOutput:
   """LLM call to summarize sample information

   Args:
      sample_uid (str): sample UID that will be used to retrieve sample information from the database

   Returns:
      (SummarizedOutput): summary of sample information
   """
   try:
       llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
       sample_metadata = retrieve_sample_info(sample_uid)
       if not sample_metadata:
           raise ValueError("No sample metadata found.")
       prompt = (
           "Please provide a concise and clear summary in a few sentences based solely on the data provided "
           f"in the following dictionary: {sample_metadata}. Avoid repeating the data verbatim and do not "
           "introduce additional information. If any information is unclear, feel free to ask the user for "
           "clarification. If the requested information cannot be retrieved, respond with: "
           "'I'm sorry, I couldn't find the information you're looking for.'"
           "Your output should be in the following format: "
           "Summary: [summary of sample information]"
           f"Metadata: {sample_metadata}"
       )
       messages = [{"role": "user", "content": prompt}]
       result = llm.with_structured_output(SummarizedOutput).invoke(messages)
       return result
   except Exception as e:
       return f"An error occurred while summarizing sample information: {str(e)}"

def summarize_all_metadata_info(sample_uid: str, filter: List[str] = None) -> SummarizedOutput:
   """LLM call to summarize metadata information for all descendants of a sample

   Args:
      sample_uid (str): sample UID that will be used to retrieve metadata information from the database for all descendants of the sample
      filter (List[str], optional): list of uid patterns to filter the metadata information by to retrieve only the metadata information for the descendants that match the patterns
   
   Returns:
      (SummarizedOutput): summary of metadata information
   """
   try:
       llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
       all_metadata = fetchAllMetadata(sample_uid, filter)
       if not all_metadata:
           raise ValueError("No metadata found for the given sample UID.")
       prompt = (
           "Please provide a concise and clear summary in a few sentences based solely on the data provided "
           f"in the following dictionary: {all_metadata}. Avoid repeating the data verbatim and do not "
           "introduce additional information. If any information is unclear, feel free to ask the user for "
           "clarification. If the requested information cannot be retrieved, respond with: "
           "'I'm sorry, I couldn't find the information you're looking for.'"
           "Your output should be in the following format: "
           "Summary: [summary of metadata]"
           f"Metadata: {all_metadata}"
       )
       messages = [{"role": "user", "content": prompt}]
       result = llm.with_structured_output(SummarizedOutput).invoke(messages)
       return result
   except Exception as e:
       return f"An error occurred while summarizing metadata information: {str(e)}"

def main():
    # Test the summarize_sample_info function
    sample_uid = 'NHP-220630FLY-15' # Replace with a valid sample UID
    # try:
    #     result = summarize_sample_info(sample_uid)
    #     print("Summarize Sample Info Result:")
    #     print(result)
    # except Exception as e:
    #     print(f"Error in summarize_sample_info: {e}")

    # Test the summarize_all_metadata_info function
    try:
        result = summarize_all_metadata_info(sample_uid, filter=["pattern1", "pattern2"])  # Replace with valid patterns
        print("\nSummarize All Metadata Info Result:")
        print(result)
    except Exception as e:
        print(f"Error in summarize_all_metadata_info: {e}")

if __name__ == "__main__":
    main()

