import inspect
import json
import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(project_root)

import backend.Tools.services.sample_service
# from backend.Tools.services.sample_service import *

# Provide a list of functions to this function

def functions_to_json(func_list):
    functions_info = {}
    for func in func_list:
        functions_info[func.__name__] = {
            "doc": inspect.getdoc(func),
            "signature": str(inspect.signature(func))
        }
    # return json.dumps(functions_info, indent=4)
    return functions_info

def module_to_json(module):
    """
    Convert all functions defined in the provided module into a JSON object.
    
    For each function, this includes:
      - The function's docstring.
      - The function's signature.
      - Any custom metadata provided via a __metadata__ attribute.
      
    Imported functions (i.e. those not defined in the module) are skipped.
    Any errors encountered during inspection are caught and recorded.
    
    Args:
        module: The Python module to introspect.
    
    Returns:
        A JSON-formatted string representing the functions and their details.
    """
    functions = {}
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        # Skip functions that are not defined in this module.
        if obj.__module__ != module.__name__:
            continue
        
        try:
            func_info = {
                "doc": inspect.getdoc(obj),
                "signature": str(inspect.signature(obj))
            }
            # Include metadata if present
            if hasattr(obj, "__metadata__"):
                func_info["metadata"] = getattr(obj, "__metadata__")
            functions[name] = func_info
        except Exception as e:
            # Record any errors encountered while processing the function.
            functions[name] = {"error": str(e)}
    
    return functions

if __name__ == "__main__":
    # print(functions_to_json([get_sample_name, retrieve_sample_info, fetch_protocol, fetchChildren, fetch_all_descendants, add_links]))
    print(module_to_json(backend.Tools.services.sample_service))
