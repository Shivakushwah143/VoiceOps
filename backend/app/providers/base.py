import asyncio
import time
from typing import Protocol, AsyncIterator, Callable, Awaitable
from dataclasses import dataclass

class ProviderError(Exception):
    def __init__(self, kind, message='Provider operation failed'):
        self.kind = kind
        super().__init__(message)

class STTProvider(Protocol):
    async def transcribe(self, audio: AsyncIterator[bytes], event: Callable) -> str: ...
class LLMProvider(Protocol):
    async def complete(self, messages: list, schema: dict) -> dict: ...
class TTSProvider(Protocol):
    def stream(self, text: str) -> AsyncIterator[bytes]: ...
class EmbeddingProvider(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...
class TelephonyProvider(Protocol):
    async def dial(self, number: str, call_id: str) -> str: ...
    async def hangup(self, provider_id: str) -> None: ...

@dataclass
class Route:
    primary: object
    fallback: object | None = None

class ProviderManager:
    """One deadline, one primary retry, one fallback; sticky per call and family."""
    def __init__(self, routes, audit, hybrid=False, rate_fallback=False, deadline=30):
        self.routes, self.audit, self.hybrid = routes, audit, hybrid
        self.rate_fallback, self.deadline, self.sticky = rate_fallback, deadline, {}

    def eligible(self, error):
        return isinstance(error,ProviderError) and (error.kind in {'timeout','network','unavailable'} or (error.kind=='rate_limit' and self.rate_fallback))

    async def run(self, family, operation, deadline=None):
        route = self.routes[family]
        primary = self.sticky.get(family, route.primary)
        candidates = [primary]
        if family not in self.sticky:
            candidates.append(primary)
            if self.hybrid and route.fallback is not None:
                candidates.append(route.fallback)
        start=time.monotonic()
        try:
            async with asyncio.timeout(deadline or self.deadline):
                for index, provider in enumerate(candidates):
                    name=type(provider).__name__
                    try:
                        result=await operation(provider)
                        if provider is route.fallback:
                            self.sticky[family]=provider
                        await self.audit('provider.success',{'family':family,'provider':name,'attempt':index+1,'elapsed_ms':(time.monotonic()-start)*1000})
                        return result
                    except asyncio.CancelledError:
                        raise
                    except (TimeoutError,ConnectionError) as e:
                        error=ProviderError('timeout' if isinstance(e,TimeoutError) else 'network')
                    except ProviderError as e:
                        error=e
                    # Unclassified/programming errors propagate; never fall back.
                    await self.audit('provider.failure',{'family':family,'provider':name,'kind':error.kind,'attempt':index+1})
                    if not self.eligible(error) or index==len(candidates)-1:
                        raise error
                    await self.audit('provider.retry' if candidates[index+1] is provider else 'provider.switch',{'family':family,'from':name,'to':type(candidates[index+1]).__name__})
        except TimeoutError as e:
            await self.audit('provider.failure',{'family':family,'kind':'deadline'})
            raise ProviderError('timeout') from e

    async def stream(self, text):
        async def first(provider):
            stream=provider.stream(text)
            try:
                chunk=await anext(stream)
                return stream,chunk
            except BaseException:
                await stream.aclose()
                raise
        stream,chunk=await self.run('tts',first)
        try:
            yield chunk
            async with asyncio.timeout(self.deadline):
                async for chunk in stream:
                    yield chunk
        finally:
            await stream.aclose()
