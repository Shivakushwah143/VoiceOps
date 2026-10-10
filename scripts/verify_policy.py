"""Executable deterministic fault-injection verification; not a live AI evaluation."""
import asyncio,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.providers.base import ProviderManager,ProviderError,Route
from app.policy import valid_phone,explicit_optout,TOOL_SCHEMAS
async def main():
    results=[]
    class Provider:
        def __init__(self,kind=None):self.kind=kind;self.calls=0
        async def call(self):
            self.calls+=1
            if self.kind:raise ProviderError(self.kind)
            return 'ok'
    for kind,expected in [('network',1),('timeout',1),('unavailable',1),('credentials',0),('authorization',0),('schema',0),('request',0),('rate_limit',0)]:
        primary,fallback=Provider(kind),Provider();events=[]
        async def audit(k,d):events.append(k)
        manager=ProviderManager({'llm':Route(primary,fallback)},audit,hybrid=True)
        try:await manager.run('llm',lambda p:p.call())
        except ProviderError:pass
        assert fallback.calls==expected,(kind,fallback.calls)
        if expected:
            await manager.run('llm',lambda p:p.call());assert primary.calls==2 and fallback.calls==2
        results.append({'case':kind,'status':'VERIFIED','fixture':'injected provider failure, no live model'})
    assert explicit_optout("Don't call me again")
    try:valid_phone('123');raise AssertionError('phone accepted')
    except ValueError:pass
    try:TOOL_SCHEMAS['schedule_demo'].model_validate({});raise AssertionError('invalid tool accepted')
    except ValueError:pass
    output={'kind':'deterministic policy checks','results':results,'live_ai':'BLOCKED; no configured model service'}
    path=Path(__file__).resolve().parents[1]/'evals/policy-results.json';path.write_text(json.dumps(output,indent=2));print(json.dumps(output))
asyncio.run(main())
