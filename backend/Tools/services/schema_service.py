# backend/Tools/services/schema_service.py
import os
import dotenv

dotenv.load_dotenv()

import json
import openai
import sys
import time
import logging

logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.core.database import get_cached_database_schema


def extract_relevant_schema(database_name: str = 'DB_NAME'):
    start_time = time.time()
    # Retrieve up-to-date schema (cached)
    schema = get_cached_database_schema(database_name)
    schema_json = json.dumps(schema, indent=2)
    # save schema to file
    # with open('db_schema.json', 'w') as f:
    #     f.write(schema_json)
    # logger.info(f"Schema: {schema_json}")
    schema = json.loads(schema_json)
    schema = schema["tables"]
    print(schema[:2])
    # # Build a prompt for your LLM agent
    # system_prompt = (
    #     "You are a schema extraction agent. Below is the current database schema (in JSON format) and a user query. "
    #     "Ignore irrelevant tables. Focus on identifying the exact table and column that contain sample-specific genotype information. "
    #     "In our database, the table 'seek_production.samples' contains a JSON column 'json_metadata' that holds sample-specific data. "
    #     "From this column, extract the keys that are used for identifying a sample according to key words from the user query. "
    #     "It is better to retrieve more keys than is necessary than to retrieve too few keys. "
    #     "Return your answer in JSON format like this:\n"
    #     '{"tables": [{"name": "<fully_qualified_table>", "columns": [{"name": "<column_name>", "json_keys": ["<key1>", "<key2>"]}]}]}\n\n'
    #     "Database Schema:\n" + schema_json +
    #     "\nUser Query: " + user_query
    # )
    
    # # Call your LLM (this example uses OpenAI's ChatCompletion API)
    # response = openai.chat.completions.create(
    #     model="gpt-4o-mini",
    #     temperature=0,
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #     ]
    # )
    
    # answer = response.choices[0].message.content.strip()
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
    return schema

# Example usage
if __name__ == "__main__":
    # user_query = "Retrieve UIDs of all samples of this genotype: 'RaDR+/+; GPT+/+; Aag -/-'"
    result = extract_relevant_schema(database_name='DB_NAME')
    # print("Extracted Schema Mapping:", result)


