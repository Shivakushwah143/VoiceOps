import asyncio,hashlib,json,secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from xml.sax.saxutils import escape
from fastapi import FastAPI,Request,WebSocket,UploadFile,File,Form,Depends,Query
from fastapi.responses import JSONResponse,FileResponse,Response
from fastapi.staticfiles import StaticFiles
from pydantic import Field,ValidationError
from sqlalchemy import select,text,func,delete
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from redis.asyncio import Redis
from redis.exceptions import RedisError
from prometheus_client import generate_latest,CONTENT_TYPE_LATEST
from .config import settings as s
from .models import *
from .db import transaction,owned,public,event,DomainError,engine as dbengine
from .security import principal,admin,login,digest,password_hash
from .policy import Strict,valid_phone,TERMINAL,MeetingArgs,FollowupArgs,valid_time
from .domain import create_call,eligible,status
from .jobs import worker
from .providers.telephony import verify_signature
from .media import BrowserMedia,PlivoMedia,run_media
redis=Redis.from_url(s.redis_url,decode_responses=True)

@asynccontextmanager
async def lifespan(app):
    job=asyncio.create_task(worker(redis))
    yield
    job.cancel();await asyncio.gather(job,return_exceptions=True);await redis.aclose()
app=FastAPI(title='VoiceOps',version='0.1.0',lifespan=lifespan)

@app.exception_handler(RedisError)
async def coordination_error(request,error):return JSONResponse({'error':{'code':'coordination','message':'Redis unavailable'}},status_code=503)
@app.exception_handler(DomainError)
async def domain_error(request,error):return JSONResponse({'error':{'code':error.code,'message':error.message}},status_code=error.status)
@app.exception_handler(ValueError)
async def invalid_input(request,error):return JSONResponse({'error':{'code':'validation','message':'Invalid input; check phone, date, time and timezone'}},status_code=422)
@app.exception_handler(IntegrityError)
async def conflict(request,error):return JSONResponse({'error':{'code':'conflict','message':'Record conflicts with an existing operation'}},status_code=409)
@app.exception_handler(SQLAlchemyError)
async def database_error(request,error):return JSONResponse({'error':{'code':'database','message':'Persistence unavailable; operation was not confirmed'}},status_code=503)
@app.middleware('http')
async def security_headers(request,call_next):
    if request.url.path.startswith('/api') and request.method not in {'GET','HEAD','OPTIONS'} and request.headers.get('origin')!=s.public_url:
        return JSONResponse({'error':{'code':'origin','message':'Same-origin request required'}},status_code=403)
    if int(request.headers.get('content-length','0'))>6*1024*1024:return Response(status_code=413)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff';response.headers['Referrer-Policy']='no-referrer'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; worker-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'"
    if request.url.path.startswith('/api'):response.headers['Cache-Control']='no-store'
    return response

def user(request:Request):return principal(request.cookies.get('voiceops_session'))
class Login(Strict):
    email:str=Field(max_length=254)
    password:str=Field(max_length=200)
@app.post('/api/login')
async def sign_in(data:Login,request:Request):
    key='login:'+hashlib.sha256((request.client.host+data.email.lower()).encode()).hexdigest()
    n=await redis.incr(key)
    if n==1:await redis.expire(key,300)
    if n>10:raise DomainError('rate_limit','Try again later',429)
    token=login(data.email,data.password)
    response=JSONResponse({'ok':True});response.set_cookie('voiceops_session',token,httponly=True,secure=s.secure_cookie,samesite='strict',max_age=28800);return response
@app.post('/api/logout')
def logout(request:Request,u=Depends(user)):
    with transaction() as db:db.execute(delete(Session).where(Session.token_hash==digest(request.cookies['voiceops_session'])))
    response=JSONResponse({'ok':True});response.delete_cookie('voiceops_session');return response
@app.get('/api/me')
def me(u=Depends(user)):return public(u)
@app.get('/livez')
def live():return {'status':'alive'}
@app.get('/readyz')
async def ready():
    with transaction() as db:db.execute(select(Tenant.id).limit(1))
    await redis.ping();return {'status':'ready'}
@app.get('/metrics')
def metrics(request:Request):
    if not s.metrics_token or not secrets.compare_digest(request.headers.get('authorization',''),'Bearer '+s.metrics_token):return Response(status_code=401)
    return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)

RESOURCES={'leads':Lead,'campaigns':Campaign,'knowledge-bases':KnowledgeBase,'documents':Document,'calls':Call,'meetings':Meeting,'followups':FollowUp,'users':User}
@app.get('/api/list/{resource}')
def listing(resource:str,offset:int=Query(0,ge=0),limit:int=Query(50,ge=1,le=100),u=Depends(user)):
    model=RESOURCES.get(resource)
    if not model:raise DomainError('resource','Not found',404)
    if model is User:admin(u)
    with transaction() as db:
        records=db.scalars(select(model).where(model.tenant_id==u.tenant_id).order_by(model.created_at.desc()).offset(offset).limit(limit)).all()
        return {'items':[public(x) for x in records],'offset':offset,'limit':limit}
class LeadInput(Strict):
    name:str=Field(min_length=1,max_length=200)
    phone:str=Field(default='',max_length=20)
    company:str=Field(default='',max_length=200)
    interest:str=Field(default='',max_length=500)
    status:Literal['NEW','CONTACTED','QUALIFIED','NOT_INTERESTED','CLOSED']='NEW'
    consent:Literal['UNKNOWN','GRANTED','DENIED']='UNKNOWN'
    consent_source:str=Field(default='',max_length=500)
    consent_at:datetime|None=None
@app.post('/api/leads')
def add_lead(data:LeadInput,u=Depends(user)):
    if data.phone:valid_phone(data.phone)
    if data.consent=='GRANTED' and (not data.consent_source or not data.consent_at or data.consent_at.tzinfo is None):raise DomainError('consent','Explicit consent source and timestamp required')
    with transaction() as db:
        l=Lead(tenant_id=u.tenant_id,**data.model_dump());db.add(l);db.flush();return public(l)
@app.put('/api/leads/{id}')
def edit_lead(id:str,data:LeadInput,u=Depends(user)):
    if data.phone:valid_phone(data.phone)
    with transaction() as db:
        l=owned(db,Lead,id,u.tenant_id,True)
        if data.phone!=l.phone:
            data.consent='UNKNOWN';data.consent_source='';data.consent_at=None
        if data.consent=='GRANTED' and (not data.consent_source or not data.consent_at or data.consent_at.tzinfo is None):raise DomainError('consent','Consent evidence required')
        for k,v in data.model_dump().items():setattr(l,k,v)
        return public(l)
@app.post('/api/leads/{id}/archive')
def archive_lead(id:str,u=Depends(user)):
    with transaction() as db:owned(db,Lead,id,u.tenant_id).archived=True
    return {'ok':True}
class Named(Strict):name:str=Field(min_length=1,max_length=200)
@app.post('/api/knowledge-bases')
def add_kb(data:Named,u=Depends(user)):
    with transaction() as db:
        k=KnowledgeBase(tenant_id=u.tenant_id,name=data.name);db.add(k);db.flush();return public(k)
@app.post('/api/documents')
async def upload(kb_id:str=Form(...),file:UploadFile=File(...),u=Depends(user)):
    name=Path(file.filename or '').name
    if Path(name).suffix.lower() not in {'.pdf','.txt','.md'}:raise DomainError('file','Upload PDF, TXT or Markdown')
    data=await file.read(5*1024*1024+1)
    if not data or len(data)>5*1024*1024:raise DomainError('file','File must be 1 byte to 5 MiB')
    sha=hashlib.sha256(data).hexdigest()
    with transaction() as db:
        if owned(db,KnowledgeBase,kb_id,u.tenant_id).archived:raise DomainError('kb','Knowledge base archived')
        existing=db.scalar(select(Document).where(Document.kb_id==kb_id,Document.tenant_id==u.tenant_id,Document.digest==sha))
        if existing:return public(existing)
        doc=Document(tenant_id=u.tenant_id,kb_id=kb_id,name=name[:250],digest=sha);db.add(doc);db.flush()
        path=Path(s.data_dir)/'documents';path.mkdir(parents=True,exist_ok=True);(path/doc.id).write_bytes(data)
        return public(doc)
@app.post('/api/documents/{id}/{action}')
def document_action(id:str,action:str,u=Depends(user)):
    with transaction() as db:
        doc=owned(db,Document,id,u.tenant_id,True)
        if action in {'approve','withdraw'}:admin(u)
        if action=='approve' and doc.status=='READY_FOR_REVIEW':doc.status='APPROVED'
        elif action=='withdraw' and doc.status=='APPROVED':doc.status='READY_FOR_REVIEW'
        elif action=='retry' and doc.status=='FAILED':doc.status='RECEIVED'
        else:raise DomainError('state','Action invalid for document state',409)
        event(db,u.tenant_id,'document.'+action,{'document_id':id,'user_id':u.id});return public(doc)
class CallInput(Strict):
    request_key:str=Field(min_length=8,max_length=150)
    transport:Literal['browser','phone']='browser'
    mode:Literal['local','production','hybrid']='local'
    lead_id:str|None=None
    kb_id:str|None=None
    objective:str=Field(default='Answer questions and offer a demo when requested.',max_length=2000)
@app.post('/api/calls')
async def start_call(data:CallInput,u=Depends(user)):
    await redis.ping()
    if data.transport=='phone' and (not s.public_url.startswith('https://') or not all([s.plivo_id,s.plivo_token,s.plivo_from])):raise DomainError('telephony','Plivo credentials and public HTTPS URL required')
    with transaction() as db:return public(create_call(db,u,**data.model_dump()))
@app.get('/api/calls/{id}')
def call_detail(id:str,u=Depends(user)):
    with transaction() as db:
        c=owned(db,Call,id,u.tenant_id);result=public(c)
        for key,model in [('turns',Turn),('events',Event),('tools',ToolExecution)]:result[key]=[public(x) for x in db.scalars(select(model).where(model.tenant_id==u.tenant_id,model.call_id==id).order_by(model.created_at).limit(1000))]
        return result
@app.post('/api/calls/{id}/{action}')
def call_action(id:str,action:str,u=Depends(user)):
    with transaction() as db:
        c=owned(db,Call,id,u.tenant_id,True)
        if action=='cancel':status(db,c,'CANCELLED','operator_cancelled')
        elif action=='summary-retry' and c.summary_status=='FAILED':c.summary_status='PENDING'
        else:raise DomainError('action','Invalid call action')
        return public(c)
class CampaignInput(Strict):
    name:str=Field(min_length=1,max_length=200)
    objective:str=Field(min_length=1,max_length=2000)
    kb_id:str
    lead_ids:list[str]=Field(min_length=1,max_length=100)
    mode:Literal['production','hybrid']='production'
@app.post('/api/campaigns')
def add_campaign(data:CampaignInput,u=Depends(user)):
    with transaction() as db:
        owned(db,KnowledgeBase,data.kb_id,u.tenant_id)
        for id in data.lead_ids:owned(db,Lead,id,u.tenant_id)
        c=Campaign(tenant_id=u.tenant_id,user_id=u.id,**data.model_dump());db.add(c);db.flush();return public(c)
@app.post('/api/campaigns/{id}/{action}')
def campaign_action(id:str,action:str,u=Depends(user)):
    with transaction() as db:
        db.scalar(select(Tenant).where(Tenant.id==u.tenant_id).with_for_update())
        c=owned(db,Campaign,id,u.tenant_id,True)
        if action=='start' and c.status in {'DRAFT','PAUSED'}:
            if not all([s.plivo_id,s.plivo_token,s.plivo_from]) or not s.public_url.startswith('https://'):raise DomainError('telephony','Configure Plivo and HTTPS before launching')
            kb=owned(db,KnowledgeBase,c.kb_id,u.tenant_id)
            if kb.archived or not db.scalar(select(Document.id).where(Document.kb_id==kb.id,Document.tenant_id==u.tenant_id,Document.status=='APPROVED').limit(1)):raise DomainError('kb','Approved knowledge required')
            for lead_id in c.lead_ids:eligible(db,owned(db,Lead,lead_id,u.tenant_id))
            for lead_id in c.lead_ids:create_call(db,u,request_key='campaign:'+c.id+':'+lead_id,transport='phone',mode=c.mode,lead_id=lead_id,kb_id=c.kb_id,campaign_id=c.id,objective=c.objective)
            c.status='RUNNING'
        elif action=='pause' and c.status=='RUNNING':c.status='PAUSED'
        elif action=='cancel' and c.status in {'DRAFT','RUNNING','PAUSED'}:
            c.status='CANCELLED'
            for call in db.scalars(select(Call).where(Call.tenant_id==u.tenant_id,Call.campaign_id==id,Call.status=='QUEUED')):status(db,call,'CANCELLED','campaign_cancelled')
        else:raise DomainError('state','Action invalid for campaign state',409)
        return public(c)
class UserInput(Strict):
    name:str=Field(min_length=1,max_length=200)
    email:str=Field(min_length=3,max_length=254)
    password:str=Field(min_length=12,max_length=200)
    role:Literal['ADMIN','OPERATOR']='OPERATOR'
@app.post('/api/users')
def add_user(data:UserInput,u=Depends(user)):
    admin(u)
    with transaction() as db:
        v=User(tenant_id=u.tenant_id,name=data.name,email=data.email.lower(),role=data.role,password_hash=password_hash(data.password));db.add(v);db.flush();return public(v)
@app.post('/api/users/{id}/deactivate')
def deactivate(id:str,u=Depends(user)):
    admin(u)
    if id==u.id:raise DomainError('self','Cannot deactivate your current account')
    with transaction() as db:
        owned(db,User,id,u.tenant_id).active=False;db.execute(delete(Session).where(Session.user_id==id))
    return {'ok':True}
@app.post('/api/{resource}/{id}/complete')
def complete_record(resource:str,id:str,u=Depends(user)):
    model={'meetings':Meeting,'followups':FollowUp}.get(resource)
    if not model:raise DomainError('resource','Not found',404)
    with transaction() as db:
        record=owned(db,model,id,u.tenant_id)
        if record.status not in {'SCHEDULED','PENDING'}:raise DomainError('state','Record cannot be completed',409)
        record.status='COMPLETED';return public(record)
@app.get('/api/system')
async def system(u=Depends(user)):
    return {'mode':s.mode,'providers':{'stt':s.stt or 'mode default','llm':s.llm or 'mode default','tts':s.tts or 'mode default'},'configured':{'sarvam':bool(s.sarvam_key),'groq':bool(s.groq_key),'plivo':bool(s.plivo_id and s.plivo_token and s.plivo_from),'whisper_assets':Path(s.whisper_dir).is_dir(),'kokoro_assets':Path(s.kokoro_dir).is_dir()},'note':'Configuration presence does not verify provider health. Estimated and billed costs unavailable until pricing/usage are reconciled.'}
@app.get('/api/dashboard')
def dashboard(u=Depends(user)):
    with transaction() as db:return {key:db.scalar(select(func.count()).select_from(model).where(model.tenant_id==u.tenant_id)) for key,model in RESOURCES.items() if key!='users'}
@app.get('/api/evaluations')
def evaluations(u=Depends(user)):
    admin(u);p=Path(s.data_dir)/'evaluations.json'
    return json.loads(p.read_text()) if p.exists() else {'status':'NOT_RUN','results':[]}
@app.websocket('/ws/browser/{id}')
async def browser(ws:WebSocket,id:str):
    try:
        if ws.headers.get('origin')!=s.public_url:raise DomainError('origin','Forbidden')
        token=ws.cookies.get('voiceops_session');u=principal(token)
        with transaction() as db:
            c=owned(db,Call,id,u.tenant_id)
            if c.transport!='browser' or c.user_id!=u.id or c.status!='CREATED':raise DomainError('call','Session unavailable')
        await ws.accept();await run_media(ws,c,redis,BrowserMedia(ws),lambda:principal(token))
    except Exception:
        try:await ws.close(code=1008)
        except Exception:pass
async def verified_form(request):
    form=dict(await request.form())
    url=s.public_url+request.url.path+('?' + request.url.query if request.url.query else '')
    if not verify_signature(request.method,url,request.headers.get('x-plivo-signature-v3-nonce',''),request.headers.get('x-plivo-signature-v3',''),form):raise DomainError('signature','Invalid callback signature',403)
    return form
@app.post('/telephony/answer/{id}')
async def answer(id:str,request:Request):
    form=await verified_form(request)
    with transaction() as db:
        c=db.get(Call,id)
        if not c or c.status in TERMINAL:return Response('<Response><Hangup/></Response>',media_type='application/xml')
        if c.provider_id and c.provider_id!=form.get('CallUUID'):raise DomainError('call','Call identity mismatch',403)
        if form.get('To')!=owned(db,Lead,c.lead_id,c.tenant_id).phone:raise DomainError('call','Destination mismatch',403)
        c.provider_id=form['CallUUID']
    token=secrets.token_urlsafe(32);await redis.set('plivo:'+token,id,ex=60)
    url=s.public_url.replace('https://','wss://')+'/ws/plivo/'+token
    return Response('<Response><Stream bidirectional="true" keepCallAlive="true" contentType="audio/x-mulaw;rate=8000">'+escape(url)+'</Stream></Response>',media_type='application/xml')
@app.post('/telephony/status/{id}')
async def phone_status(id:str,request:Request):
    form=await verified_form(request)
    with transaction() as db:
        c=db.get(Call,id)
        if c and c.provider_id==form.get('CallUUID'):
            target={'completed':'COMPLETED','busy':'BUSY','no-answer':'NO_ANSWER','failed':'FAILED','ringing':'RINGING'}.get(form.get('CallStatus'))
            if target:status(db,c,target,'provider_callback')
    return {'ok':True}
@app.websocket('/ws/plivo/{token}')
async def phone_socket(ws:WebSocket,token:str):
    try:
        id=await redis.getdel('plivo:'+token)
        if not id:await ws.close(code=1008);return
        await ws.accept()
        start=await asyncio.wait_for(ws.receive_json(),10)
        if start.get('event')=='connected':start=await asyncio.wait_for(ws.receive_json(),10)
        with transaction() as db:c=db.get(Call,id)
        data=start.get('start',{});fmt=data.get('mediaFormat',{})
        if start.get('event')!='start' or data.get('callId')!=c.provider_id or data.get('accountId')!=s.plivo_id or fmt.get('sampleRate')!=8000 or fmt.get('encoding')!='audio/x-mulaw':raise ValueError('Invalid stream')
        await run_media(ws,c,redis,PlivoMedia(ws,start.get('streamId') or data['streamId'],c.provider_id))
    except Exception:
        try:await ws.close(code=1008)
        except Exception:pass
frontend=Path(__file__).resolve().parents[2]/'frontend'
app.mount('/assets',StaticFiles(directory=frontend),name='assets')
@app.get('/')
def index():return FileResponse(frontend/'index.html')
