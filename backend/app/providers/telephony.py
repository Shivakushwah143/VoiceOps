import asyncio
from .base import ProviderError
from ..config import settings as s

class Plivo:
    def client(self):
        if not s.plivo_id or not s.plivo_token or not s.plivo_from:raise ProviderError('credentials')
        import plivo
        return plivo.RestClient(s.plivo_id,s.plivo_token)
    async def dial(self,number,call_id):
        client=self.client()
        response=await asyncio.to_thread(client.calls.create,from_=s.plivo_from,to_=number,answer_url=s.public_url+'/telephony/answer/'+call_id,answer_method='POST',hangup_url=s.public_url+'/telephony/status/'+call_id,hangup_method='POST',ring_timeout=30)
        return str(response.request_uuid)
    async def hangup(self,provider_id):
        await asyncio.to_thread(self.client().calls.delete,provider_id)

def verify_signature(method,url,nonce,signature,params):
    if not s.plivo_token or not nonce or not signature:return False
    from plivo.utils import validate_v3_signature
    return validate_v3_signature(method,url,nonce,s.plivo_token,signature,params)
