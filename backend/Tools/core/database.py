# backend/Tools/core/database.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect
import pandas as pd
import logging
from dotenv import load_dotenv
import json
load_dotenv()

def get_db_connection(database_name: str = 'DB_NAME'):
    """
    Establish a connection to the MySQL database using SQLAlchemy.

    Returns:
        session: A SQLAlchemy session object for interacting with the database.

    Raises:
        Exception: If there is an error connecting to the database.
    """
    try:
        # Get the database credentials from the environment variables
        HOST = os.getenv('DB_HOST')
        USER = os.getenv('DB_USER')
        DBNAME = os.getenv(database_name)
        PASSWORD = os.getenv('DB_PASSWORD')
    
        # Create the database URL
        DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DBNAME}"
        
        # Create an engine
        engine = create_engine(DATABASE_URL)
        
        return engine
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise

def get_json_keys(table: str, json_column: str, database_name: str = 'DB_NAME', sample_size: int = 20):
    """
    Query a sample of rows from a JSON column and return the union of keys.
    """
    query = text(f"SELECT {json_column} FROM {table} WHERE {json_column} IS NOT NULL LIMIT {sample_size};")
    try:
        results = execute_query(query, database_name)
        keys = set()
        for row in results:
            value = row.get(json_column)
            if value:
                try:
                    json_data = json.loads(value)
                    if isinstance(json_data, dict):
                        keys.update(json_data.keys())
                except Exception as e:
                    logging.error(f"Error parsing JSON from {table}.{json_column}: {e}")
        return list(keys)
    except Exception as e:
        logging.error(f"Error extracting JSON keys from {json_column} in {table}: {e}")
    return []

def get_database_schema(database_name: str = 'DB_NAME'):
    """
    Connect to the database and dynamically retrieve the schema.
    Args:
        database_name (str): The name of the database to connect to.
    Returns:
        dict: A dictionary mapping each table to its list of columns.
    """
    engine = get_db_connection(database_name)
    inspector = inspect(engine)
    # Retrieve the actual database name from the connection URL
    db_name = engine.url.database
    
    schema = {"database": db_name, "tables": []}
    for table in inspector.get_table_names():
        table_info = {"name": f"{db_name}.{table}", "columns": []}
        for col in inspector.get_columns(table):
            # Collect useful details for each column
            col_details = {
                "name": col.get("name"),
                "type": str(col.get("type")),
                "nullable": col.get("nullable"),
                "default": col.get("default")
            }
            # If the column appears to be a JSON type (by name or type hint), try to extract keys
            # For columns that look like JSON, attempt to extract keys.
            if col_details["name"] == "json_metadata" or "JSON" in col_details["type"].upper():
                json_keys = get_json_keys(table, col_details["name"], database_name)
                col_details["json_keys"] = json_keys
            table_info["columns"].append(col_details)
        schema["tables"].append(table_info)
    engine.dispose()
    return schema

def execute_query(query, database_name: str = 'DB_NAME'):
    """
    Execute a SQL query using SQLAlchemy and return the results.

    Args:
        query (str): The SQL query to execute.

    Returns:
        list[dict]: A list of dictionaries representing the query results.

    Raises:
        SQLAlchemyError: If there is an error executing the query.
    """
    engine = None
    try:
        # Get a database session
        engine = get_db_connection(database_name)
        
        # Execute the query
        result = pd.read_sql(query, engine)
        formatted_result = result.to_dict(orient='records')
        
        return formatted_result
    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        raise
    finally:
        if engine:
            engine.dispose()

from cachetools import TTLCache, cached

# Create a cache that holds 1 schema and expires after 1800 seconds (30 minutes)
schema_cache = TTLCache(maxsize=1, ttl=1800)

@cached(cache=schema_cache)
def get_cached_database_schema(database_name: str = 'DB_NAME'):
    """
    Retrieve the database schema using caching.
    This will query the database only if the cache has expired.
    """
    return get_database_schema(database_name)
