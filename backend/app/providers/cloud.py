import asyncio,base64,json,time
from urllib.parse import urlencode
import aiohttp
import websockets
from .base import ProviderError
from .http import check
from ..config import settings as s

def websocket_error(error):
    status=getattr(getattr(error,'response',None),'status_code',None)
    if status: check(status)
    code=getattr(getattr(error,'rcvd',None),'code',None)
    return ProviderError('configuration' if code in {1003,1008,4000} else 'network')

class SarvamSTT:
    async def transcribe(self,audio,event):
        if not s.sarvam_key: raise ProviderError('credentials')
        query=urlencode({'language_code':'en-IN','model':s.sarvam_stt_model,'encoding':'linear16','sample_rate':16000,'endpointing':'manual','stream_type':'fast'})
        try:
            async with websockets.connect('wss://api.sarvam.ai/speech-to-text-realtime/ws?'+query,additional_headers={'Api-Subscription-Key':s.sarvam_key},open_timeout=8,max_size=1048576) as ws:
                await ws.send(json.dumps({'event':'speech_start'}))
                async def send():
                    async for chunk in audio: await ws.send(json.dumps({'event':'audio_input','audio':base64.b64encode(chunk).decode()}))
                    await ws.send(json.dumps({'event':'speech_end'}))
                task=asyncio.create_task(send())
                try:
                    async with asyncio.timeout(40):
                        async for raw in ws:
                            item=json.loads(raw);kind=item.get('event')
                            if kind in {'transcript.partial','transcript.final'}:
                                text=item.get('text','')
                                await event(kind,{'text':text})
                                if kind=='transcript.final': return text
                            if kind=='error' or item.get('type')=='error': raise ProviderError('request')
                    raise ProviderError('network')
                finally:
                    task.cancel();await asyncio.gather(task,return_exceptions=True)
        except (websockets.exceptions.WebSocketException,OSError) as e: raise websocket_error(e) from e

class SarvamTTS:
    async def stream(self,text):
        if not s.sarvam_key: raise ProviderError('credentials')
        query=urlencode({'model':s.sarvam_tts_model,'send_completion_event':'true'})
        try:
            async with websockets.connect('wss://api.sarvam.ai/text-to-speech/ws?'+query,additional_headers={'Api-Subscription-Key':s.sarvam_key},open_timeout=8,max_size=2097152) as ws:
                await ws.send(json.dumps({'type':'config','data':{'speaker':s.sarvam_voice,'language_code':'en-IN','speech_sample_rate':16000,'output_audio_codec':'linear16'}}))
                await ws.send(json.dumps({'type':'text','data':{'text':text}}))
                await ws.send(json.dumps({'type':'flush'}))
                async for raw in ws:
                    item=json.loads(raw)
                    if item.get('type')=='audio': yield base64.b64decode(item['data']['audio'],validate=True)
                    elif item.get('type')=='event' and item.get('data',{}).get('event_type')=='final': return
                    elif item.get('type')=='error': raise ProviderError('request')
                raise ProviderError('network')
        except (websockets.exceptions.WebSocketException,OSError) as e: raise websocket_error(e) from e

class Groq:
    async def complete(self,messages,schema):
        if not s.groq_key: raise ProviderError('credentials')
        start=time.monotonic();first=None;parts=[];usage={}
        body={'model':s.groq_model,'messages':messages+[{'role':'system','content':'Return only JSON matching this schema: '+json.dumps(schema)}],'temperature':0.1,'max_tokens':700,'stream':True,'response_format':{'type':'json_object'}}
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=25)) as session:
                async with session.post('https://api.groq.com/openai/v1/chat/completions',json=body,headers={'Authorization':'Bearer '+s.groq_key}) as r:
                    check(r.status)
                    async for line in r.content:
                        if not line.startswith(b'data:'): continue
                        value=line[5:].strip()
                        if value==b'[DONE]':break
                        obj=json.loads(value)
                        for choice in obj.get('choices',[]):
                            delta=choice.get('delta',{}).get('content')
                            if delta:
                                if first is None:first=time.monotonic()-start
                                parts.append(delta)
                        usage=obj.get('x_groq',{}).get('usage',usage)
            return {'text':''.join(parts),'usage':usage,'ttft_ms':None if first is None else first*1000}
        except aiohttp.ClientConnectionError as e: raise ProviderError('network') from e
