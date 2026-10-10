import asyncio,json,os,sys,time
from pathlib import Path
import aiohttp
from .base import ProviderError
from .http import check,json_request
from ..config import settings as s

class Ollama:
    async def complete(self,messages,schema):
        parts=[];first=None;start=time.monotonic();usage={}
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=25)) as session:
                async with session.post(s.ollama_url+'/api/chat',json={'model':s.ollama_model,'messages':messages,'format':schema,'stream':True,'options':{'temperature':0.1,'num_predict':700}}) as r:
                    check(r.status)
                    async for line in r.content:
                        obj=json.loads(line)
                        if 'error' in obj:raise ProviderError('configuration')
                        text=obj.get('message',{}).get('content','')
                        if text:
                            if first is None:first=time.monotonic()-start
                            parts.append(text)
                        if obj.get('done'):usage={k:obj[k] for k in ('prompt_eval_count','eval_count') if k in obj}
            return {'text':''.join(parts),'usage':usage,'ttft_ms':None if first is None else first*1000}
        except aiohttp.ClientConnectionError as e:raise ProviderError('network') from e

class OllamaEmbedding:
    async def embed(self,texts):
        result=await json_request('POST',s.ollama_url+'/api/embed',{'model':s.embedding_model,'input':texts})
        vectors=result.get('embeddings',[])
        if len(vectors)!=len(texts) or any(len(v)!=768 for v in vectors):raise ProviderError('configuration','Expected 768-dimensional embeddings')
        return vectors

async def worker(kind,path,data):
    if not Path(path).is_dir():raise ProviderError('configuration','Local model assets missing')
    env={**os.environ,'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','PYTHONPATH':'/models/python:'+os.environ.get('PYTHONPATH','')}
    proc=await asyncio.create_subprocess_exec(sys.executable,'-m','app.providers.worker',kind,path,stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.DEVNULL,env=env)
    try:
        output,_=await proc.communicate(data)
        if proc.returncode:raise ProviderError('configuration','Local model execution failed; check assets and compute')
        return output
    finally:
        if proc.returncode is None:
            proc.kill();await proc.wait()

class FasterWhisper:
    async def transcribe(self,audio,event):
        chunks=[];size=0
        async for chunk in audio:
            size+=len(chunk)
            if size>960000:raise ProviderError('request','Utterance exceeds 30 seconds')
            chunks.append(chunk)
        text=(await worker('stt',s.whisper_dir,b''.join(chunks))).decode()
        await event('transcript.final',{'text':text})
        return text

class Kokoro:
    async def stream(self,text):
        data=await worker('tts',s.kokoro_dir,text.encode())
        if not data or len(data)%2:raise ProviderError('schema')
        for offset in range(0,len(data),6400):yield data[offset:offset+6400]
