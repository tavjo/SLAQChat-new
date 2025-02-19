# backend/app/services/nhp_service.py

import json
import logging
from pydantic import ValidationError
from typing import List
from sqlalchemy import text, bindparam
import os
import sys
import pandas as pd
import asyncio
from backend.Tools.services.helpers import async_wrap
from backend.Tools.services.multiSample_metadata_service import multi_sample_info_retrieval

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.core.database import execute_query

logger = logging.getLogger(__name__)

@async_wrap
def fetchChildrenMetadata(term: str) -> List[dict]:
    """
    Fetch the children metadata for a given term from the database.

    Args:
        term (str): The UUID of the sample to search for in the database.

    Returns:
        List[dict]: A list of dictionaries containing the children metadata.
                    Returns an empty list if an error occurs during the query.
    """
    try:
        query = text("""
        SELECT uuid, full 
        FROM dmac.seek_sample_tree
        WHERE uuid = :term;
        """)
        children_metadata = execute_query(query.bindparams(term=term), 'DB_NAME1')
        return children_metadata
    except Exception as e:
        logger.error(f"Error fetching NHP metadata: {e}")
        return []

async def fetch_all_descendants(term: str) -> List[str]:
    """
    Fetch all descendants of a given sample.

    Args:
        term (str): The UUID of the sample to search for in the database.

    Returns:
        List[str]: A list of all descendant UUIDs. Returns an empty list if an error occurs.
    """
    try:
        # Fetch the children metadata
        children_metadata = await fetchChildrenMetadata(term)
        if not children_metadata:
            return []

        # Parse the 'full' JSON structure
        full_structure = json.loads(children_metadata[0]['full'])

        # Recursive function to collect all descendants
        def collect_descendants(node):
            descendants = []
            if 'children' in node:
                for child in node['children']:
                    descendants.append(child['id'])
                    descendants.extend(collect_descendants(child))
            return descendants

        # Start collecting from the root node
        all_descendants = collect_descendants(full_structure[0])
        # print(all_descendants)
        return all_descendants

    except Exception as e:
        logger.error(f"Error fetching all descendants: {e}")
        return []


async def fetchDescendantMetadata(term: str, filter: List[str] = None) -> List[dict]:
    """
    Fetch all metadata for a given term and its descendants. For the argument filter, choose one of the following (not exhaustive but most common):
            - 'PAV' = patient visit
            - 'D.IMG' = imaging (i.e. CT, X-ray, etc.)
            - 'TIS' = tissue collection (i.e. blood draw, bone marrow, etc.)
            - 'BAC' = bacteria 
            - 'D.SEQ' = raw sequencing data
            - 'A.SEQ' = analyzed sequencing data

    Args:
        term (str): The UUID of the sample to search for in the database.
        filter (List[str], optional): A list of strings to filter the UUIDs. 

    Returns:
        List[dict]: A list of metadata dictionaries for the term and its descendants.
                    Returns an empty list if an error occurs.
    """
    try:
        # Fetch all descendant UUIDs
        descendants_uuids = await fetch_all_descendants(term)
        if filter:
            # Apply filter to the descendant UUIDs
            descendants_uuids = [child for child in descendants_uuids if any(f in child for f in filter)]
        
        # Add the original term to the list of UUIDs
        descendants_uuids.append(term)
        
        if not descendants_uuids:
            logger.warning("No descendants found for the given term.")
            return []

        # Prepare the SQL query with placeholders
        # placeholders = ",".join([f":uuid_{i}" for i in range(len(descendants_uuids))])
        # query = text(f"""
        # SELECT uuid, json_metadata
        # FROM seek_production.samples
        # WHERE uuid IN ({placeholders});
        # """)
        query = text(
            """
            SELECT uuid, json_metadata
            FROM seek_production.samples
            WHERE uuid IN :uids;
            """
        )
        query_text = query.bindparams(bindparam("uids", expanding=True))
        all_metadata = execute_query(query_text.params(uids=descendants_uuids), 'DB_NAME')
        
        # Create a dictionary for bind parameters
        # bind_params = {f"uuid_{i}": uuid for i, uuid in enumerate(descendants_uuids)}
        
        # Execute the query
        # all_metadata = execute_query(query.bindparams(**bind_params), 'DB_NAME')
        logger.info(f"Fetched metadata for {len(all_metadata)} entries.")
        results = multi_sample_info_retrieval(descendants_uuids, all_metadata)
        return results

    except Exception as e:
        logger.error(f"Error fetching metadata for term {term}: {e}")
        return []