import sys
import os

from backend.Tools.services.sample_service import fetchAllMetadata, fetchChildren

def run_test():
    # name = retrieve_nhp_name('NHP-220630FLY-15')
    # info = retrieve_nhp_info('NHP-220630FLY-15')
    # samples = get_nhp_samples('NHP-220630FLY-15')
    return fetchChildren('NHP-220630FLY-15')
    # return print(f"NHP Name: {name}"), print(f"NHP Info:\n {info}"), print(f"NHP Samples:\n {samples}")

if __name__ == "__main__":
    run_test()