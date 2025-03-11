import sys
import os
import asyncio

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(project_root)

# from backend.Tools.services.sample_service import fetchAllMetadata, fetchChildren
from backend.Tools.services.multiSample_metadata_service import get_uids_by_terms_and_field, get_metadata_by_uids
from backend.Tools.services.module_to_json import functions_to_json

def run_test():
    # name = retrieve_nhp_name('NHP-220630FLY-15')
    # info = retrieve_nhp_info('NHP-220630FLY-15')
    # samples = get_nhp_samples('NHP-220630FLY-15')
    # return fetchChildren('NHP-220630FLY-15')
    # res = asyncio.run(get_uids_by_terms_and_field('Genotype', ['RaDR+/+; GPT+/+; Aag -/-']))
    # res = asyncio.run(get_uids_by_terms_and_field('Study', ['CD8 Depletion']))
    res = functions_to_json([get_uids_by_terms_and_field, get_metadata_by_uids])
    print(res)
    return res
    # return print(f"NHP Name: {name}"), print(f"NHP Info:\n {info}"), print(f"NHP Samples:\n {samples}")

if __name__ == "__main__":
    run_test()