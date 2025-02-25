# backend/Tools/services/helpers.py

import asyncio
import functools

def async_wrap(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        # run the sync function in the default ThreadPoolExecutor
        return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
    return wrapper

import time


def timer_wrap(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Call the original function
        end_time = time.time()  # Record the end time
        elapsed_time = end_time - start_time  # Calculate the elapsed time
        print(f"Function {func.__name__} took {elapsed_time:.4f} seconds to complete.")
        return result  # Return the result of the original function
    return wrapper




