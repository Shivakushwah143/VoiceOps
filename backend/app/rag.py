import io,uuid
from pathlib import Path
from sqlalchemy import select
from .models import Document,KnowledgeBase
from .db import transaction,owned,DomainError
from .providers.local import OllamaEmbedding
from .providers.http import json_request
from .config import settings as s
COLLECTION='voiceops_nomic_768_v1'

async def ingest(doc_id,tenant):
    with transaction() as db:
        doc=owned(db,Document,doc_id,tenant,True)
        if doc.status not in {'RECEIVED','FAILED'}:return
        doc.status='EXTRACTING';name=doc.name
    try:
        data=(Path(s.data_dir)/'documents'/doc_id).read_bytes()
        if name.lower().endswith('.pdf'):
            from pypdf import PdfReader
            pdf=PdfReader(io.BytesIO(data))
            if pdf.is_encrypted or len(pdf.pages)>300:raise ValueError('Unsupported PDF')
            text='\n'.join(p.extract_text() or '' for p in pdf.pages)
        else:text=data.decode('utf-8')
        if not text.strip() or len(text)>200000:raise ValueError('Empty or oversized text')
        chunks=[text[i:i+1200] for i in range(0,len(text),1000)]
        with transaction() as db:
            doc=owned(db,Document,doc_id,tenant);doc.status='EMBEDDING';doc.text=text;kb=doc.kb_id
        collections=await json_request('GET',s.qdrant_url+'/collections')
        if COLLECTION not in [c['name'] for c in collections['result']['collections']]:
            await json_request('PUT',s.qdrant_url+'/collections/'+COLLECTION,{'vectors':{'size':768,'distance':'Cosine'}})
        for offset in range(0,len(chunks),8):
            batch=chunks[offset:offset+8];vectors=await OllamaEmbedding().embed(batch)
            points=[{'id':str(uuid.uuid5(uuid.NAMESPACE_URL,doc_id+':'+str(offset+i))),'vector':vector,'payload':{'tenant_id':tenant,'kb_id':kb,'doc_id':doc_id,'chunk':offset+i,'text':chunk}} for i,(chunk,vector) in enumerate(zip(batch,vectors))]
            await json_request('PUT',s.qdrant_url+'/collections/'+COLLECTION+'/points?wait=true',{'points':points})
        with transaction() as db:
            doc=owned(db,Document,doc_id,tenant);doc.status='READY_FOR_REVIEW';doc.chunk_count=len(chunks);doc.error=''
    except Exception as e:
        with transaction() as db:
            doc=owned(db,Document,doc_id,tenant);doc.status='FAILED';doc.error=type(e).__name__
        raise

async def retrieve(tenant,kb_id,query):
    if not kb_id:return []
    with transaction() as db:
        kb=owned(db,KnowledgeBase,kb_id,tenant)
        if kb.archived:return []
        allowed=list(db.scalars(select(Document.id).where(Document.tenant_id==tenant,Document.kb_id==kb_id,Document.status=='APPROVED')))
    if not allowed:return []
    vector=(await OllamaEmbedding().embed([query]))[0]
    result=await json_request('POST',s.qdrant_url+'/collections/'+COLLECTION+'/points/search',{'vector':vector,'limit':4,'score_threshold':0.35,'with_payload':True,'filter':{'must':[{'key':'tenant_id','match':{'value':tenant}},{'key':'kb_id','match':{'value':kb_id}},{'key':'doc_id','match':{'any':allowed}}]}})
    hits=[]
    with transaction() as db:
        kb=owned(db,KnowledgeBase,kb_id,tenant)
        if kb.archived:return []
        for point in result['result']:
            payload=point['payload']
            doc=db.scalar(select(Document).where(Document.id==payload.get('doc_id'),Document.tenant_id==tenant,Document.kb_id==kb_id,Document.status=='APPROVED'))
            if doc and payload.get('tenant_id')==tenant and payload.get('kb_id')==kb_id:
                hits.append({'document_id':doc.id,'name':doc.name,'chunk':payload['chunk'],'text':payload['text'],'score':point['score']})
    return hits
