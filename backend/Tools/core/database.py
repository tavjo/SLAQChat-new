# backend/Tools/core/database.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect
import pandas as pd
import logging
from dotenv import load_dotenv
import json
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)
from backend.Tools.schemas import ALLOWED_KEYS
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
        print("Creating database url")
        # Create the database URL
        DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DBNAME}"
        
        # Create an engine
        engine = create_engine(DATABASE_URL)
        print(f"Connected to {DBNAME} on {HOST}")
        return engine
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise

def get_json_keys(table: str, json_column: str, database_name: str = 'DB_NAME', sample_size: int = len(ALLOWED_KEYS)):
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

def get_database_schema(database_name: str = 'DB_NAME', table_names: list[str] = ['samples']):
    """
    Connect to the database and dynamically retrieve the schema.
    Args:
        database_name (str): The name of the database to connect to. Default is 'DB_NAME'.
        table_names (list[str]): The names of the tables to connect to. Default is ['samples'].
    Returns:
        dict: A dictionary mapping each table to its list of columns.
    """
    engine = get_db_connection(database_name)
    inspector = inspect(engine)
    # Retrieve the actual database name from the connection URL
    db_name = engine.url.database
    
    schema = {"database": db_name, "tables": []}
    # Check if table names provided are in the database:
    tbl_list = [tbl for tbl in table_names if tbl in inspector.get_table_names()]
    for table in tbl_list:
        # filter table_info to only include the table_name
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

def execute_query(query, database_name: str = 'DB_NAME', output_format: str = 'dict'):
    """
    Execute a SQL query using SQLAlchemy and return the results.

    Args:
        query (str): The SQL query to execute.
        output_format (str): The format of the output. Default is 'dict'.
        database_name (str): The name of the database to connect to. Default is 'DB_NAME'.
    Returns:
        list[dict]: A list of dictionaries representing the query results.

    Raises:
        SQLAlchemyError: If there is an error executing the query.
    """
    engine = None
    try:
        # Get a database session
        print("Getting database connection")
        engine = get_db_connection(database_name)
        
        # Execute the query
        if engine is not None:
            print("Executing query")
            result = pd.read_sql(query, engine)
            if output_format == 'dict':
                formatted_result = result.to_dict(orient='records')
            elif output_format == 'df':
                formatted_result = result
            else:
                raise ValueError(f"Invalid output format: {output_format}")
            print("Query executed successfully")
        else:
            print("No engine found")
            formatted_result = []
        
        return formatted_result
    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        raise
    finally:
        if engine:
            engine.dispose()

from cachetools import TTLCache, cached

# Create a cache that holds 1 schema and expires after 1800 seconds (30 minutes)
schema_cache = TTLCache(maxsize=1, ttl=300)

@cached(cache=schema_cache)
def get_cached_database_schema(database_name: str = 'DB_NAME', table_names: list[str] = ['samples']):
    """
    Retrieve the database schema using caching.
    This will query the database only if the cache has expired.
    """
    return get_database_schema()

def execute_update_query(query, params=None, database_name: str = 'DB_NAME', batch_mode: bool = False):
    """
    Execute a SQL update/insert/delete query using SQLAlchemy.

    Args:
        query (sqlalchemy.sql.elements.TextClause): The SQLAlchemy text query to execute.
        params (dict, list[dict], or None): Parameters for the query. Can be:
            - None: No parameters
            - dict: Single set of parameters for one query execution
            - list[dict]: Multiple sets of parameters for batch execution
        database_name (str): The name of the database to connect to. Default is 'DB_NAME'.
        batch_mode (bool): Whether to execute as a batch operation. Default is False.

    Returns:
        int: Number of rows affected by the query.

    Raises:
        SQLAlchemyError: If there is an error executing the query.
    """
    engine = None
    try:
        # Get a database connection
        print("Getting database connection")
        engine = get_db_connection(database_name)
        
        # Execute the query
        if engine is not None:
            print("Executing update query")
            connection = engine.connect()
            
            with connection.begin():
                if batch_mode and isinstance(params, list):
                    # Execute batch update
                    total_affected = 0
                    for param_set in params:
                        result = connection.execute(query, param_set)
                        total_affected += result.rowcount
                    affected_rows = total_affected
                elif params is not None:
                    # Execute single update with parameters
                    result = connection.execute(query, params)
                    affected_rows = result.rowcount
                else:
                    # Execute update without parameters
                    result = connection.execute(query)
                    affected_rows = result.rowcount
            
            connection.close()
            print(f"Update query executed successfully. Rows affected: {affected_rows}")
            return affected_rows
        else:
            print("No engine found")
            return 0
    except SQLAlchemyError as e:
        logging.error(f"Database update error: {e}")
        raise
    finally:
        if engine:
            engine.dispose()
