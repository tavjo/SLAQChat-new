# backend/app/services/nhp_service.py

import json
import logging
from pydantic import ValidationError
from typing import List
from sqlalchemy import text
import os
import sys
import pandas as pd

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.core.database import execute_query

logger = logging.getLogger(__name__)

def get_sample_name(sample_metadata: List[dict]) -> str | None:
    """
    Extract the sample Name from the fetched metadata.

    Args:
        sample_metadata (List[dict]): The metadata of the sample.

    Returns:
        str | None: The name of the sample or None if an error occurred.
    """
    if sample_metadata:
        json_metadata = sample_metadata[0].get('json_metadata', {})
        metadata_dict = json.loads(json_metadata)
        extracted_name = metadata_dict.get('Name') if metadata_dict.get('Name') else metadata_dict.get('File_PrimaryData')
        if extracted_name:
            return str(extracted_name).strip()
        else:
            print("Error: 'Name' or 'File_PrimaryData' not found in JSON metadata.")
            return None
    else:
        print("Error: Sample name not found.")
        return None

    
def fetch_any_sample(uid: str) -> List[dict] | None:
    """
    Fetches the metadata for a given sample UID in the database.

    Args:
        uid (str): The UID of the sample.

    Returns:
        List[dict] | None: The metadata for the sample or None if not found.
    """
    query = text("""
    SELECT uuid, json_metadata
    FROM seek_production.samples
    WHERE uuid = :uid;
    """)
    sample_metadata = execute_query(query.bindparams(uid=uid))
    return sample_metadata

def retrieve_sample_info(uid: str) -> List[dict] | None:
    """
    Retrieves the metadata for a given sample UID in the database.

    Args:
        uid (str): The UID of the sample.

    Returns:
        List[dict] | None: A list containing the metadata dictionary for the sample or None if an error occurred.
    """

    sample_metadata = fetch_any_sample(uid)
    if not sample_metadata:
        logger.error("No metadata found.")
        return None
    for entry in sample_metadata:
        # if name in entry["json_metadata"]["Name"]:
        entry['parsed_metadata'] = json.loads(entry['json_metadata'])

    processed_data = []

    try:
        uuids = [entry['uuid'] for entry in sample_metadata]
        idx = uuids.index(uid)
        metadata_dict = sample_metadata[idx]['parsed_metadata']
        logger.info(metadata_dict)
    except json.JSONDecodeError:
        print("Error decoding JSON")
        metadata_dict = {}
        # Process each record and convert to NHPInfo
    try:
        processed_data.append(metadata_dict)
    except ValidationError as ve:
        # Log the validation error and skip the record
        logger.error(f"Validation error: {ve}")

    logger.info(processed_data)
    # Export data to JSON
    try:
        return processed_data
    except Exception as e:
        logger.error(f"Error saving NHP information to JSON: {e}")
        return None

def fetchChildren(term: str) -> List[dict]:
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

def fetch_all_descendants(term: str) -> List[str]:
    """
    Fetch all descendants of a given sample.

    Args:
        term (str): The UUID of the sample to search for in the database.

    Returns:
        List[str]: A list of all descendant UUIDs. Returns an empty list if an error occurs.
    """
    try:
        # Fetch the children metadata
        children_metadata = fetchChildren(term)
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


def fetchAllMetadata(term: str, filter: List[str] = None) -> List[dict]:
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
        descendants_uuids = fetch_all_descendants(term)
        if filter:
            # Apply filter to the descendant UUIDs
            descendants_uuids = [child for child in descendants_uuids if any(f in child for f in filter)]
        
        # Add the original term to the list of UUIDs
        descendants_uuids.append(term)
        
        if not descendants_uuids:
            logger.warning("No descendants found for the given term.")
            return []

        # Prepare the SQL query with placeholders
        placeholders = ",".join([f":uuid_{i}" for i in range(len(descendants_uuids))])
        query = text(f"""
        SELECT uuid, json_metadata
        FROM seek_production.samples
        WHERE uuid IN ({placeholders});
        """)
        
        # Create a dictionary for bind parameters
        bind_params = {f"uuid_{i}": uuid for i, uuid in enumerate(descendants_uuids)}
        
        # Execute the query
        all_metadata = execute_query(query.bindparams(**bind_params), 'DB_NAME')
        logger.info(f"Fetched metadata for {len(all_metadata)} entries.")
        print(all_metadata)
        return all_metadata

    except Exception as e:
        logger.error(f"Error fetching metadata for term {term}: {e}")
        return []

def add_links(sample_uid: str) -> str:
    """
    Constructs a link to the sample's page on the NExtSEEK website or constructs a link to download a protocol associated with a sample.

    Args:
        sample_uid (str): Sample UID that will be used to construct the link.

    Returns:
        str: Link to the sample's page on the NExtSEEK website.
    """
    if sample_uid and not sample_uid.startswith("P."):
        sample_uid = str(sample_uid).strip()
        return f"https://nextseek.mit.edu/seek/sampletree/uid={sample_uid}/"
    elif sample_uid and sample_uid.startswith("P."):
        sample_uid = str(sample_uid).strip()
        return f"https://nextseek.mit.edu/seek/sop/uid={sample_uid}/"
    else:
        print("No valid sample UID provided. Returning default link to NExtSEEK website.")
        return f"https://nextseek.mit.edu/"

def fetch_protocol(uid: str) -> str | None:
    """
    Fetch the protocol for a given sample UID if it exists.

    Args:
        uid (str): The UID of the sample.

    Returns:
        str | None: The protocol link for the sample or None if no protocol is found.
    """
    metadata = retrieve_sample_info(uid)
    protocol_uid = metadata[0]["Protocol"] if metadata[0]["Protocol"] else None
    if protocol_uid:
        return add_links(protocol_uid)
    else:
        return None