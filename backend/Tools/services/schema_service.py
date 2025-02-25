# backend/Tools/services/schema_service.py
import os
import dotenv

dotenv.load_dotenv()

import json
import openai
import sys
import time
import logging
import asyncio

logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.core.database import get_cached_database_schema


async def extract_relevant_schema(database_name: str = 'DB_NAME', table_names: list[str] = ['samples']):
    """
    Extracts the relevant schema for a given database.

    This function retrieves the cached database schema, processes it to extract
    relevant tables, and logs the time taken for the operation.

    Args:
        database_name (str): The name of the database to extract the schema from. Defaults to 'DB_NAME'.
        table_names (list[str]): The names of the tables to extract the schema from. Defaults to ['samples'].
    Returns:
        list: A list of relevant tables with associated columns from the database schema.

    Raises:
        Exception: If there is an error in retrieving or processing the schema.
    """
    try:
        logger.info(f"Retrieving schema for database '{database_name}'")
        start_time = time.time()
        # Retrieve up-to-date schema (cached)
        schema = get_cached_database_schema()
        schema_json = json.dumps(schema, indent=2)
        # save schema to file
        with open('db_schema.json', 'w') as f:
            f.write(schema_json)
        schema = json.loads(schema_json)
        schema = schema["tables"]

    except Exception as e:
        logger.error(f"Error extracting schema for database '{database_name}': {e}")
        raise
    finally:
        end_time = time.time()
        logger.info(f"Retrived schema in : {end_time - start_time} seconds")
    return schema

# Example usage
if __name__ == "__main__":
    # user_query = "Retrieve UIDs of all samples of this genotype: 'RaDR+/+; GPT+/+; Aag -/-'"
    result = asyncio.run(extract_relevant_schema())
    print("Extracted Schema Mapping:", result)


