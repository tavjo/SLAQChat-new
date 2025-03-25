# backend/app/services/nhp_service.py

import json
import logging
from pydantic import ValidationError
from typing import List, Union
from sqlalchemy import text, bindparam
import os, sys
# import pandas as pd
# import asyncio
from backend.Tools.services.helpers import async_wrap, timer_wrap
# from backend.Tools.schemas import ALLOWED_KEYS
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.core.database import execute_query

logger = logging.getLogger(__name__)


@async_wrap
@timer_wrap
def multi_sample_info_retrieval(uids: List[str], metadata: List[dict]) -> List[dict] | None:
    """
    Retrieves the metadata for multiple samples in the database.

    Args:
        uids (List[str]): The UIDs of the samples.
        metadata (List[dict]): The metadata for the samples.

    Returns:
        List[dict] | None: A list containing the metadata dictionary for the sample or None if an error occurred.
    """

    if not metadata:
        logger.error("No metadata found.")
        return None
    for entry in metadata:
        # if name in entry["json_metadata"]["Name"]:
        entry['parsed_metadata'] = json.loads(entry['json_metadata'])

    processed_data = []

    try:
        uuids = [entry['uuid'] for entry in metadata]
        metadata_dict = {}
        for uid in uids:
            idx = uuids.index(uid)
            metadata_dict[uid] = metadata[idx]['parsed_metadata']
        logger.info(f"Metadata retrieved for UIDs: {uids}")
    except json.JSONDecodeError as jde:
        logger.error(f"Error decoding JSON: {jde}")
        metadata_dict = {}
    except ValueError as ve:
        logger.error(f"UID not found in metadata: {ve}")
        metadata_dict = {}
    except Exception as e:
        logger.error(f"Unexpected error during metadata retrieval: {e}")
        metadata_dict = {}

    try:
        processed_data.append(metadata_dict)
    except ValidationError as ve:
        logger.error(f"Validation error: {ve}")
    except Exception as e:
        logger.error(f"Unexpected error while processing data: {e}")

    logger.info(f"Processed data: {processed_data}")
    # Export data to JSON
    try:
        return processed_data
    except Exception as e:
        logger.error(f"Error saving NHP information to JSON: {e}")
        return None


@timer_wrap
async def get_metadata_by_uids(uids: List[str]) -> List[dict]:
    """
    Get all metadata for a given list of UIDs.
    args:
        uids (List[str]): The UIDs of the metadata to get.
    returns:
        List[dict]: A list of metadata dictionaries for the given UIDs.
    """
    try:
        query = text(
            """
            SELECT uuid, json_metadata
            FROM seek_production.samples
            WHERE uuid IN :uids;
            """
        )
        query_text = query.bindparams(bindparam("uids", expanding=True))
        metadata = execute_query(query_text.params(uids=uids), 'DB_NAME')
        if not metadata:
            logger.warning(f"No metadata found for UIDs: {uids}")
            return []
        results = await multi_sample_info_retrieval(uids, metadata)
        return results
    except Exception as e:
        logger.error(f"Error in get_metadata_by_uids: {e}")
        return []


@async_wrap
@timer_wrap
def get_uids_by_terms_and_field(cols: Union[str, List[str]], terms: List[str]) -> List[str]:
    """
    Get all UIDs for a given list of terms and for specific column(s) in a table.
    If multiple columns are provided, the number of terms must match the number of columns.
    Args:
        cols (str | List[str]): The json_keys of the attributes to search.
        terms (List[str]): The terms to search for. If cols is a list, terms should have the same length and match the order of the columns.
    Returns:
        List[str]: A list of UIDs for the given terms.
    """
    try:
        # Normalize cols: if a single column is provided, convert it to a list.
        if isinstance(cols, str):
            cols = [cols]
        
        # Format columns by capitalizing and prepending '$.'
        formatted_cols = [f"$.{c.capitalize()}" for c in cols]
        
        # Check if terms are provided
        if not terms:
            logger.warning(f"No terms provided for columns '{formatted_cols}'")
            return []

        ## # allow all columns because ALLOWED_KEYS is not complete and should vary depending on the sample type. However, if we are retrieving UIDs, we cannot know the sample type beforehand.

        # Validate that the number of columns matches the number of terms
        if len(formatted_cols) != len(terms):
            logger.error(f"Number of columns {formatted_cols} and terms {terms} do not match.")
            return []
        
        # Build dynamic WHERE clause and bind parameters.
        conditions = []
        bind_params = {}
        for idx, (col_value, term_value) in enumerate(zip(formatted_cols, terms)):
            conditions.append(f"JSON_EXTRACT(json_metadata, :col{idx}) = :term{idx}")
            bind_params[f"col{idx}"] = col_value
            bind_params[f"term{idx}"] = term_value

        where_clause = " AND ".join(conditions)
        query_str = f"""
            SELECT uuid, json_metadata
            FROM seek_production.samples
            WHERE {where_clause};
        """
        query = text(query_str)

        # Execute query and extract UIDs.
        results = execute_query(query.bindparams(**bind_params), 'DB_NAME')
        uids = [result['uuid'] for result in results]

        if not uids:
            logger.warning(f"No UIDs found for columns '{formatted_cols}' with terms: {terms}")
        else:
            logger.info(f"Retrieved UIDs: {uids}")

        return uids
    except Exception as e:
        logger.error(f"Error in get_uids_by_terms_and_fields: {e}")
        return []