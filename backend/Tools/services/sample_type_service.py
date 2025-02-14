# backend/app/services/nhp_service.py

import json
import logging
from pydantic import ValidationError
from typing import List
from sqlalchemy import text
import os
import sys
import pandas as pd
import asyncio
from backend.Tools.services.helpers import async_wrap

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.core.database import execute_query

logger = logging.getLogger(__name__)

@async_wrap
def get_uids_by_type(type: str) -> List[str]:
    """
    Get all UIDs of a given sample type.
    args:
        type (str): The sample type of the UIDs to get.
    returns:
        List[str]: A list of UIDs of the given type.
    """
    query = text(
        """
        SELECT uuid
        FROM seek_production.samples
        WHERE uuid like :type
        """
    )
    uids = execute_query(query.bindparams(type=type), 'DB_NAME')
    return uids

@async_wrap
def get_uids_by_type_and_terms(type: str, terms: List[str]) -> List[str]:
    """
    Get all UIDs of a given type with these terms in the json_metadata.
    args:
        type (str): The sample type of the UIDs to get.
        terms (List[str]): The terms to search for in the json_metadata.
    returns:
        List[str]: A list of UIDs of the given type with the terms in the json_metadata.
    """
    query = text(
        """
        SELECT uuid
        FROM seek_production.samples
        WHERE uuid like :type
        AND json_metadata like :terms
        """
    )
    uids = execute_query(query.bindparams(type=type, terms=terms), 'DB_NAME')
    return uids

@async_wrap
def get_metadata_by_uids(uids: List[str]) -> List[dict]:
    """
    Get all metadata for a given list of UIDs.
    args:
        uids (List[str]): The UIDs of the metadata to get.
    returns:
        List[dict]: A list of metadata dictionaries for the given UIDs.
    """
    query = text(
        """
        SELECT uuid, json_metadata
        FROM seek_production.samples
        WHERE uuid in :uids
        """
    )
    metadata = execute_query(query.bindparams(uids=uids), 'DB_NAME')
    return metadata


async def get_metadata_by_type(type: str) -> List[dict]:
    """
    Get all metadata of a given sample type.
    args:
        type (str): The sample type of the metadata to get.
    returns:
        List[dict]: A list of metadata dictionaries for the given sample type.
    """
    uids = await get_uids_by_type(type)
    metadata = await get_metadata_by_uids(uids)
    return metadata

async def get_metadata_by_type_and_terms(type: str, terms: List[str]) -> List[dict]:
    """
    Get all metadata of a given sample type with these terms in the json_metadata.
    args:
        type (str): The sample type of the metadata to get.
        terms (List[str]): The terms to search for in the json_metadata.
    returns:
        List[dict]: A list of metadata dictionaries for the given sample type with the terms in the json_metadata.
    """
    uids = await get_uids_by_type_and_terms(type, terms)
    metadata = await get_metadata_by_uids(uids)
    return metadata
