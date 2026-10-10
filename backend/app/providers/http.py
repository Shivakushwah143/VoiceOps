import aiohttp
from .base import ProviderError

def check(status):
    if status<400:return
    kind='credentials' if status==401 else 'authorization' if status==403 else 'rate_limit' if status==429 else 'unavailable' if status>=500 else 'request'
    raise ProviderError(kind)

async def json_request(method,url,payload=None,headers=None,timeout=20):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.request(method,url,json=payload,headers=headers) as response:
                check(response.status)
                return await response.json()
    except aiohttp.ClientConnectionError as e: raise ProviderError('network') from e
    except (ValueError,aiohttp.ContentTypeError) as e: raise ProviderError('schema') from e
