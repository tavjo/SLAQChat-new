# core/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import logging
from dotenv import load_dotenv

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