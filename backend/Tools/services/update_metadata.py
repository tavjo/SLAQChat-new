import pandas as pd
import json
import time
import logging
from sqlalchemy import text, bindparam
from sqlalchemy.exc import SQLAlchemyError
import os, base64 
from io import StringIO
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Set, Optional, Any, Union

import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

from backend.Tools.core.database import execute_query, execute_update_query
from backend.Tools.services.helpers import async_wrap, timer_wrap
from src.chatbot.studio.models import SampleTypeAttributes, InputCSV
import asyncio
from backend.Tools.schemas import UpdatePipelineMetadata
import logging.handlers

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@async_wrap
@timer_wrap
def get_st_attributes(
    output_format: str = 'object',
    filter_by: Optional[List[str]] = None
) -> Union[pd.DataFrame, List[SampleTypeAttributes]]:
    """
    Retrieves sample type title, description and associated attributes from the database.
    
    Args:
        output_format (str): Format of the output. 'object' returns a list of SampleTypeAttributes, 
                             'df' returns a pd.DataFrame.
        filter_by (Optional[List[str]]): A list of sample type titles to filter the results by.
    
    Returns:
        Union[pd.DataFrame, List[SampleTypeAttributes]]:
            - If 'df': DataFrame containing attribute titles and their corresponding sample type titles.
            - If 'object': List of SampleTypeAttributes objects.
    """
    # Execute the query with JOIN
    query = text("""
        SELECT 
            sa.title AS attribute_title, 
            st.title AS sample_type_title, 
            st.description AS sample_type_description
        FROM seek_production.sample_attributes sa
        JOIN seek_production.sample_types st 
            ON sa.sample_type_id = st.id;
    """)
    df = execute_query(query, database_name='DB_NAME', output_format='df')
    
    # Apply filtering if provided
    if filter_by:
        logging.info(f"Filtering results by sample types: {filter_by}")
        df = df[df['sample_type_title'].isin(filter_by)]
    
    if output_format == 'object':
        logging.info("Returning attributes as list of SampleTypeAttributes")
        # Group attributes by sample type title and description, aggregating the attribute titles into a list
        grouped_df = df.groupby(
            ['sample_type_title', 'sample_type_description'], as_index=False
        )['attribute_title'].agg(list)
        
        # Build a list of SampleTypeAttributes objects from the grouped data
        results = []
        for _, row in grouped_df.iterrows():
            sta = SampleTypeAttributes(
                sampletype=row['sample_type_title'],
                st_description=row['sample_type_description'],
                attributes=row['attribute_title']
            )
            results.append(sta)
        return results
    else:
        logging.info("Returning attributes as DataFrame")
        # Return DataFrame without the description column if not needed
        return df.drop(columns=['sample_type_description'])


@async_wrap
@timer_wrap
def get_input_data(file_data: InputCSV) -> pd.DataFrame:
    """
    Reads and processes the input CSV file containing sample data to update.
    
    Args:
        file_data (InputCSV): InputCSV instance containing file data and metadata
        
    Returns:
        pd.DataFrame: Processed input data with extracted SampleType from UID.
        
    Raises:
        FileNotFoundError: If input.csv does not exist.
    """
    # Decode the base64 content
    decoded_content = base64.b64decode(file_data.content).decode('utf-8')
    # Convert the decoded content to a pandas DataFrame
    input = pd.read_csv(StringIO(decoded_content))
    input["SampleType"] = input["UID"].str.split("-").str[0]
    cols = ["UID", "SampleType"] + [col for col in input.columns if col not in ["UID", "SampleType"]]
    # Reorder DataFrame
    input = input[cols]
    return input


# @async_wrap
@timer_wrap
async def check_attributes(st_attributes: pd.DataFrame, file_data: InputCSV) -> pd.DataFrame:
    """
    Verifies that attributes in the input file exist in the database for each sample type.
    
    Args:
        st_attributes (pd.DataFrame): DataFrame containing attribute titles and sample type titles.
        
    Returns:
        pd.DataFrame: Matrix showing which attributes (1=exists, 0=doesn't exist) are valid for each sample type.
    """
    ##ENSURE Attributes you want to update exist in the DB. 1 == exist, 0 == dont exist

    input = await get_input_data(file_data)

    # Step 1: Get unique SampleTypes
    unique_sample_types = input["SampleType"].unique()
    # Step 2: Extract attributes to check (all column names except UID and SampleType)
    attributes = [col for col in input.columns if col not in ["UID", "SampleType"]]
    # Step 3: Filter st_attributes to keep only relevant SampleTypes
    st_filtered = st_attributes[st_attributes["sample_type_title"].isin(unique_sample_types)]
    # Step 4: Create attributes_to_check DataFrame
    attributes_to_check = pd.DataFrame(columns=["SampleType"] + attributes)
    attributes_to_check["SampleType"] = unique_sample_types
    # Step 5: Populate attributes_to_check
    for sample_type in unique_sample_types:
        valid_attributes = set(st_filtered[st_filtered["sample_type_title"] == sample_type]["attribute_title"])
        attributes_to_check.loc[attributes_to_check["SampleType"] == sample_type, attributes] = [
            1 if attr in valid_attributes else 0 for attr in attributes
        ]

    # Print full DataFrame
    # print(attributes_to_check)
    return attributes_to_check


# @async_wrap
@timer_wrap
async def filter_attributes(attributes_to_check: pd.DataFrame, file_data: InputCSV) -> pd.DataFrame:
    """
    Filters out samples with attributes that don't exist in the database.
    
    Args:
        attributes_to_check (pd.DataFrame): Matrix showing which attributes are valid for each sample type.
        
    Returns:
        pd.DataFrame: Filtered input data containing only samples with valid attributes.
    """
    ### Removes samples from input who have 0's in the above sample.
    input = await get_input_data(file_data)
    
    # Step 1: Identify SampleTypes with a '0' in any attribute
    sample_types_to_remove = attributes_to_check[attributes_to_check.eq(0).any(axis=1)]["SampleType"]

    # Step 2: Generate removal reasons
    removal_reasons = []
    for _, row in attributes_to_check.iterrows():
        if row["SampleType"] in sample_types_to_remove.values:
            invalid_attributes = row.index[row.eq(0)].tolist()
            for attr in invalid_attributes:
                removal_reasons.append(f"Sample Type {row['SampleType']} removed because of 0 in attribute {attr}")

    # Print all removal reasons
    for reason in removal_reasons:
        print(reason)

    # Step 3: Filter input DataFrame
    input_filtered = input[~input["SampleType"].isin(sample_types_to_remove)]
    return input_filtered


@async_wrap
@timer_wrap
def fetch_relevant_metadata(input_filtered: pd.DataFrame) -> Tuple[Dict[str, Dict[str, Any]], int]:
    """
    Fetches metadata for samples in batches from the database.
    
    Args:
        input_filtered (pd.DataFrame): Filtered input data containing only samples with valid attributes.
        
    Returns:
        Tuple[Dict[str, Dict[str, Any]], int]: A tuple containing:
            - Dictionary mapping UIDs to their JSON metadata
            - Batch size used for fetching
    """
    # Configure logging
    logging.basicConfig(filename="update_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

    # Start timer
    # start_time = time.time()
    logging.info("Update process started.")
    print("Starting update process...")

    # conn = mysql.connector.connect(**db_config)
    # cursor = conn.cursor(dictionary=True)

    # Step 1: Fetch json_metadata in Batches (Fixes Fetch Limit Issue)
    uids = list(input_filtered["UID"])  # Convert to list for batching
    batch_size = 250  # Reduce from 1000 to 250 to avoid locks
    metadata_dict = {}

    # fetch_start = time.time()
    missing_uids = []

    for i in range(0, len(uids), batch_size):
        batch = tuple(uids[i:i+batch_size])
        query = text(
        """
        SELECT uuid, json_metadata
        FROM seek_production.samples
        WHERE uuid IN :batch;
        """)
        query_text = query.bindparams(bindparam("batch", expanding=True))
        # query = text(f"SELECT uuid, json_metadata FROM seek_production.samples WHERE uuid IN ({','.join(['%s'] * len(batch))})")
        # cursor.execute(query, batch)

        
        # results = cursor.fetchall()
        results = execute_query(query_text.params(batch=batch), 'DB_NAME')
        if results:
            metadata_dict.update({row["uuid"]: json.loads(row["json_metadata"]) for row in results if row["json_metadata"]})
        
        # Track missing UIDs
        fetched_titles = set(row["uuid"] for row in results)
        missing_in_batch = set(batch) - fetched_titles
        missing_uids.extend(missing_in_batch)
        total_batches = (len(uids) + batch_size - 1) // batch_size

        logging.info(f"Fetched batch {i // batch_size + 1}/{total_batches} with {len(results)} records.")

    # fetch_end = time.time()
    # logging.info(f"Fetched {len(metadata_dict)} records in {fetch_end - fetch_start:.2f} seconds.")
    logging.info(f"Total records fetched: {len(metadata_dict)}")

    # Log missing UIDs if any
    if missing_uids:
        logging.warning(f"Missing {len(missing_uids)} UIDs from database.")
        print(f"Warning: {len(missing_uids)} UIDs not found in database.")
    
    return metadata_dict, batch_size


@async_wrap
@timer_wrap
def update_metadata(metadata_dict: Dict[str, Dict[str, Any]], input_filtered: pd.DataFrame) -> Tuple[List[Tuple[str, str]], List[str]]:
    """
    Updates sample metadata in memory based on input data.
    
    Args:
        metadata_dict (Dict[str, Dict[str, Any]]): Dictionary mapping UIDs to their JSON metadata.
        input_filtered (pd.DataFrame): Filtered input data containing only samples with valid attributes.
        
    Returns:
        Tuple[List[Tuple[str, str]], List[str]]: A tuple containing:
            - List of tuples (json_metadata, uuid) for database update
            - List of warning messages for attributes not found
    """
    # Step 2: Update json_metadata in memory
    update_data = []
    not_found_attrs = []
    # update_start = time.time()

    logging.info("In-memory json update process started.")

    for _, row in input_filtered.iterrows():
        uid = row["UID"]
        
        if uid in metadata_dict:
            metadata = metadata_dict[uid]
            updated = False
            
            # Only update existing attributes
            for attr in row.index:
                if attr not in ["UID", "SampleType"]:  # Skip UID and SampleType
                    if attr in metadata:
                        metadata[attr] = row[attr]  # Update attribute
                        updated = True
                    else:
                        msg = f"Attribute '{attr}' doesn't exist for sample UUID '{uid}'"
                        logging.warning(msg)
                        not_found_attrs.append(msg)
            
            if updated:
                update_data.append((json.dumps(metadata), uid))

    # update_end = time.time()
    # logging.info(f"Processed {len(update_data)} updates in {update_end - update_start:.2f} seconds.")
    logging.info(f"Processed {len(update_data)} updates.")

    return update_data, not_found_attrs


@async_wrap
@timer_wrap
def update_records(update_data: List[Tuple[str, str]], batch_size: int, not_found_attrs: List[str]) -> Optional[List[str]]:
    """
    Performs batch updates to the database with the updated metadata.
    
    Args:
        update_data (List[Tuple[str, str]]): List of tuples (json_metadata, uuid) for database update.
        batch_size (int): Size of batches for database updates.
        not_found_attrs (List[str]): List of warning messages for attributes not found.
        
    Returns:
        Optional[List[str]]: List of warning messages if any, None otherwise.
    """
    # Step 3: Perform batch updates (Avoids Locking) with Debugging
    bulk_update_start = time.time()
    update_query = text("UPDATE seek_production.samples SET json_metadata = :metadata WHERE uuid = :uuid")

    for i in range(0, len(update_data), batch_size):
        batch = update_data[i:i+batch_size]
        total_batches = (len(update_data) + batch_size - 1) // batch_size

        print(f"Trying to update batch {i // batch_size + 1} with {len(batch)} records...")

        try:
            # cursor.executemany(update_query, batch)
            # conn.commit()  # Commit after every batch
            params = {"metadata": batch[0][0], "uuid": batch[0][1]}
            execute_update_query(update_query, params, 'DB_NAME')
            print(f"✅ Committed batch {i // batch_size + 1}/{total_batches} with {len(batch)} records.")
            logging.info(f"✅ Committed batch {i // batch_size + 1} with {len(batch)} records.")
            
            time.sleep(0.1)  # Add short delay to prevent locks

        except SQLAlchemyError as err:
            print(f"❌ ERROR in batch {i // batch_size + 1}: {err}")
            logging.error(f"❌ ERROR in batch {i // batch_size + 1}: {err}")
            break  # Stop further updates if we hit an error

    bulk_update_end = time.time()
    logging.info(f"Updated {len(update_data)} records in {bulk_update_end - bulk_update_start:.2f} seconds.")
    print(f"Updated {len(update_data)} records.")

    # total_time = bulk_update_end - bulk_update_start

    # logging.info(f"Update process completed in {total_time:.2f} seconds.")
    # print(f"Update process completed in {total_time:.2f} seconds.")

    # Optional: Print missing attributes
    if not_found_attrs:
        print("\nMissing attributes:")
        for msg in not_found_attrs[:10]:  # Print first 10 missing attributes for preview
            print(msg)
        print(f"...and {len(not_found_attrs) - 10} more." if len(not_found_attrs) > 10 else "")
        return not_found_attrs
    else:
        return None


async def update_metadata_pipeline(file_data: InputCSV) -> UpdatePipelineMetadata:
    """
    Main function that orchestrates the entire metadata update process.
    
    This function executes the complete pipeline:
    1. Retrieves sample attributes from the database
    2. Checks if attributes in input exist in the database
    3. Filters samples with missing attributes
    4. Fetches current metadata for samples
    5. Updates metadata in memory
    6. Performs batch updates to the database

    Args:
        file_data (InputCSV): InputCSV instance containing file data and metadata
    
    Returns:
        Dict[str, Any]: Dictionary containing execution results and logs
    """
    # Set up log capture
    log_handler = logging.handlers.MemoryHandler(capacity=1024*10, 
                                              target=None)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    
    # Create results dictionary
    results = {
        "success": True,
        "logs": [],
        "errors": [],
        "stats": {
            "total_records_processed": 0,
            "records_updated": 0,
            "missing_attributes": 0,
            "execution_time": 0
        }
    }
    
    try:
        start_time = time.time()
        
        # Get sample attributes
        logger.info("Getting sample attributes")
        st_attributes = await get_st_attributes(output_format = 'df', filter_by = None)
        
        # Check if attributes you want to update exist in the DB
        logger.info("Checking if attributes exist in the DB")
        attributes_to_check = await check_attributes(st_attributes, file_data)
        
        # Removes samples from input who have 0's in the attributes_to_check
        logger.info("Filtering samples with missing attributes")
        input_filtered = await filter_attributes(attributes_to_check, file_data)
        
        # Fetch json_metadata in Batches
        logger.info("Fetching json_metadata in Batches")
        metadata_dict, batch_size = await fetch_relevant_metadata(input_filtered)
        
        # Update json_metadata in memory
        logger.info("Updating json_metadata in memory")
        update_data, not_found_attrs = await update_metadata(metadata_dict, input_filtered)
        
        # Perform batch updates
        logger.info("Performing batch updates")
        await update_records(update_data, batch_size, not_found_attrs)
        
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Total time taken: {execution_time:.2f} seconds")
        
        # Update stats
        results["stats"]["total_records_processed"] = len(input_filtered)
        results["stats"]["records_updated"] = len(update_data)
        results["stats"]["missing_attributes"] = len(not_found_attrs) if not_found_attrs else 0
        results["stats"]["execution_time"] = execution_time
        
        # Add missing attribute warnings if any
        if not_found_attrs:
            results["errors"] = not_found_attrs[:100]  # Limit to first 100
            results["missing_attributes"] = len(not_found_attrs)
            if len(not_found_attrs) > 100:
                results["errors"].append(f"...and {len(not_found_attrs) - 100} more attribute errors")
                
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        results["success"] = False
        results["errors"].append(str(e))
    
    # Get logs from handler
    for record in log_handler.buffer:
        log_message = formatter.format(record)
        results["logs"].append(log_message)
    
    # Remove the handler after capturing logs
    logger.removeHandler(log_handler)
    
    return results

if __name__ == "__main__":
    result = asyncio.run(update_metadata_pipeline())
        # Optionally print logs
    # if result["logs"]:
    #     print("\nExecution logs:")
    #     for log in result["logs"]:
    #         print(log)
    # res = asyncio.run(update_metadata_pipeline())
    # print(res)
    # print(res[:10])