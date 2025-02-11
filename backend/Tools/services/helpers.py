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




