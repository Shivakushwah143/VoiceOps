import asyncio,base64,json,time,secrets
from .audio import Codec,Endpoint
from .engine import VoiceEngine
from .providers.factory import manager
from .providers.telephony import Plivo
from .db import DomainError

class BrowserMedia:
    def __init__(self,ws):self.ws=ws;self.playback_done=asyncio.Event();self.lock=asyncio.Lock()
    async def event(self,kind,data):
        async with self.lock:await self.ws.send_json({'type':kind,'data':data})
    async def audio(self,pcm,generation):
        self.playback_done.clear();await self.event('audio',{'pcm':base64.b64encode(pcm).decode(),'generation':generation})
    async def audio_end(self,generation):await self.event('audio.end',{'generation':generation})
    async def clear(self,generation):await self.event('audio.clear',{'generation':generation});self.playback_done.set()
    async def wait_playback(self,timeout):
        try:await asyncio.wait_for(self.playback_done.wait(),timeout)
        except TimeoutError:pass
    async def close(self,reason):
        await self.event('call.end',{'reason':reason});await self.ws.close()

class PlivoMedia(BrowserMedia):
    def __init__(self,ws,stream_id,provider_id):
        super().__init__(ws);self.stream_id=stream_id;self.provider_id=provider_id;self.codec=Codec();self.clear_pending=False;self.clear_requested_at=0
    async def event(self,kind,data):return None
    async def audio(self,pcm,generation):
        deadline=time.monotonic()+3
        while self.clear_pending:
            if time.monotonic()>deadline:raise TimeoutError('Plivo clear acknowledgement missing')
            await asyncio.sleep(0.02)
        self.playback_done.clear()
        async with self.lock:await self.ws.send_json({'event':'playAudio','media':{'contentType':'audio/x-mulaw','sampleRate':8000,'payload':base64.b64encode(self.codec.encode(pcm)).decode()}})
    async def audio_end(self,generation):
        async with self.lock:await self.ws.send_json({'event':'checkpoint','streamId':self.stream_id,'name':str(generation)})
    async def clear(self,generation):
        async with self.lock:await self.ws.send_json({'event':'clearAudio','streamId':self.stream_id})
        self.clear_pending=True;self.clear_requested_at=time.monotonic()
    async def close(self,reason):
        try:await Plivo().hangup(self.provider_id)
        finally:await self.ws.close()

async def run_media(ws,call,redis,media,authenticate=None):
    lease='media:'+call.id
    owner=secrets.token_urlsafe(24)
    if not await redis.set(lease,owner,nx=True,ex=20):await ws.close(code=1008);return
    endpoint=Endpoint();engine=None;last_renew=time.monotonic();window=time.monotonic();input_bytes=0;sequence=-1
    async def audit(kind,data):await engine.audit(kind,data)
    engine=VoiceEngine(call.tenant_id,call.id,media,manager(call.mode,audit))
    try:
        await engine.start()
        while not engine.closed:
            if time.monotonic()-last_renew>5:
                if not await redis.eval("if redis.call('get',KEYS[1])==ARGV[1] then return redis.call('expire',KEYS[1],20) else return 0 end",1,lease,owner):raise DomainError('lease','Media ownership lost')
                last_renew=time.monotonic()
                if authenticate:authenticate()
            try:message=await asyncio.wait_for(ws.receive(),1)
            except TimeoutError:
                await engine.tick();continue
            if message['type']=='websocket.disconnect':break
            data=message.get('bytes')
            if message.get('text'):
                item=json.loads(message['text'])
                if isinstance(media,PlivoMedia):
                    if item.get('streamId') not in {None,media.stream_id}:raise ValueError('Stream mismatch')
                    if item.get('event')=='media':
                        seq=int(item.get('sequenceNumber',sequence+1))
                        if seq<=sequence:continue
                        sequence=seq
                        if item['media'].get('track','inbound')!='inbound':continue
                        data=media.codec.decode(base64.b64decode(item['media']['payload'],validate=True))
                    elif item.get('event')=='clearedAudio':
                        media.clear_pending=False;await engine.audit('playback.clear_confirmed',{})
                    elif item.get('event')=='playedStream' and not media.clear_pending:await engine.played(int(item['name']))
                    elif item.get('event')=='stop':break
                else:
                    if item.get('type')=='playback.finished':await engine.played(int(item['generation']))
                    elif item.get('type')=='stop':break
                    else:raise ValueError('Unknown browser event')
            if data is not None:
                if not data or len(data)>6400 or len(data)%2:raise ValueError('Invalid PCM frame')
                if time.monotonic()-window>1:window=time.monotonic();input_bytes=0
                input_bytes+=len(data)
                if input_bytes>64000:raise ValueError('Audio input rate exceeded')
                for kind,payload in endpoint.feed(data):
                    if kind=='start':await engine.speech_start(payload)
                    elif kind=='audio':await engine.speech_audio(payload)
                    else:await engine.speech_end()
            await engine.tick()
    except Exception as e:
        try:await engine.end('FAILED',type(e).__name__)
        except Exception:pass
    finally:
        try:
            if not engine.closed:await engine.end('COMPLETED','caller_disconnected')
        finally:await redis.eval("if redis.call('get',KEYS[1])==ARGV[1] then return redis.call('del',KEYS[1]) else return 0 end",1,lease,owner)
