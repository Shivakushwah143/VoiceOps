from datetime import timedelta
from sqlalchemy import select
from .models import *
from .db import transaction,owned,event,public,DomainError
from .policy import TOOL_SCHEMAS,valid_time,valid_phone,TERMINAL,TRANSITIONS
from .config import settings

def authority(db,call):
    user=owned(db,User,call.user_id,call.tenant_id)
    tenant=db.get(Tenant,call.tenant_id)
    if not user.active or not tenant.active: raise DomainError('revoked','Call authority revoked',403)
    return user

def eligible(db,lead,phone=True):
    if lead.archived or lead.status in {'CLOSED','NOT_INTERESTED'}: raise DomainError('ineligible','Lead is not active for calling')
    suppression=db.scalar(select(Suppression).where(Suppression.tenant_id==lead.tenant_id,Suppression.phone==lead.phone))
    if lead.opted_out or suppression: raise DomainError('suppressed','Contact has opted out')
    if phone:
        valid_phone(lead.phone)
        if lead.phone not in settings.allowlist: raise DomainError('allowlist','Destination is not an authorized test number')
        if lead.consent!='GRANTED' or not lead.consent_source or not lead.consent_at:
            raise DomainError('consent','Recorded calling permission required')

def status(db,call,target,reason=''):
    if call.status in TERMINAL or target==call.status: return
    if target in TERMINAL and call.status in {'ACTIVE','CONNECTED'}: call.status='ENDING'
    if target not in TRANSITIONS.get(call.status,set()): return
    call.status=target
    if target=='CONNECTED': call.connected_at=now()
    if target in TERMINAL:
        call.ended_at=now();call.end_reason=reason
        if db.scalar(select(Turn.id).where(Turn.call_id==call.id).limit(1)): call.summary_status='PENDING'
    event(db,call.tenant_id,'call.status',{'status':target,'reason':reason},call.id)

def create_call(db,user,*,request_key,transport,mode,lead_id=None,kb_id=None,campaign_id=None,objective='Answer questions and offer a demo when requested.'):
    db.scalar(select(Tenant).where(Tenant.id==user.tenant_id).with_for_update())
    old=db.scalar(select(Call).where(Call.tenant_id==user.tenant_id,Call.request_key==request_key))
    if old:
        if (old.transport,old.mode,old.lead_id,old.kb_id,old.campaign_id,old.objective)!=(transport,mode,lead_id,kb_id,campaign_id,objective):
            raise DomainError('idempotency','Request key already used for different input',409)
        return old
    if transport not in {'browser','phone'} or mode not in {'local','production','hybrid'}: raise DomainError('profile','Invalid runtime profile')
    if transport=='phone' and not lead_id: raise DomainError('lead','Phone calls require a lead')
    if lead_id: eligible(db,owned(db,Lead,lead_id,user.tenant_id),transport=='phone')
    if kb_id and owned(db,KnowledgeBase,kb_id,user.tenant_id).archived: raise DomainError('kb','Knowledge base archived')
    c=Call(tenant_id=user.tenant_id,user_id=user.id,request_key=request_key,transport=transport,mode=mode,lead_id=lead_id,kb_id=kb_id,campaign_id=campaign_id,objective=objective,status='QUEUED' if transport=='phone' else 'CREATED')
    db.add(c);db.flush();event(db,user.tenant_id,'call.created',{},c.id)
    return c

def execute_tool(tenant,call_id,turn_id,intent_id,name,args,confirmed=False):
    model=TOOL_SCHEMAS.get(name)
    if not model: raise DomainError('tool','Unknown tool')
    values=model.model_validate(args); serialized=values.model_dump(mode='json')
    with transaction() as db:
        db.scalar(select(Tenant).where(Tenant.id==tenant).with_for_update())
        call=owned(db,Call,call_id,tenant,True);authority(db,call)
        turn=owned(db,Turn,turn_id,tenant)
        if turn.call_id!=call.id: raise DomainError('turn','Invalid turn')
        old=db.scalar(select(ToolExecution).where(ToolExecution.tenant_id==tenant,ToolExecution.intent_id==intent_id))
        if old:
            if old.call_id!=call_id or old.name!=name or old.args!=serialized: raise DomainError('idempotency','Intent collision',409)
            return old.result
        if call.status!='ACTIVE': raise DomainError('call','Call is no longer active',409)
        if not call.lead_id: raise DomainError('lead','No lead bound to session')
        lead=owned(db,Lead,call.lead_id,tenant,True)
        if name in {'schedule_demo','create_followup','update_lead'} and not confirmed:
            raise DomainError('confirmation','Caller confirmation required')
        if name!='opt_out_contact': eligible(db,lead,False)
        if name=='add_call_note':
            lead.notes=[*lead.notes,{'at':now().isoformat(),'text':values.note,'call_id':call_id}]; result={'message':'Note saved.'}
        elif name=='update_lead':
            if values.interest is not None: lead.interest=values.interest
            if values.status is not None: lead.status=values.status
            result={'message':'Lead updated.'}
        elif name=='schedule_demo':
            start=valid_time(values.start_at,values.timezone)
            meetings=db.scalars(select(Meeting).where(Meeting.tenant_id==tenant,Meeting.user_id==call.user_id,Meeting.status=='SCHEDULED')).all()
            if any(start<m.start_at+timedelta(minutes=m.duration_minutes) and start+timedelta(minutes=values.duration_minutes)>m.start_at for m in meetings):
                raise DomainError('overlap','That operator already has a meeting at this time',409)
            m=Meeting(tenant_id=tenant,lead_id=lead.id,call_id=call.id,user_id=call.user_id,**values.model_dump())
            db.add(m);db.flush();call.outcome='DEMO_SCHEDULED'; result={'id':m.id,'message':'Demo recorded. No calendar invitation was sent.'}
        elif name=='create_followup':
            valid_time(values.due_at,values.timezone)
            f=FollowUp(tenant_id=tenant,lead_id=lead.id,call_id=call.id,user_id=call.user_id,**values.model_dump())
            db.add(f);db.flush();call.outcome='FOLLOWUP_REQUESTED';result={'id':f.id,'message':'Follow-up recorded.'}
        elif name=='set_call_outcome':
            if values.outcome=='OPTED_OUT': raise DomainError('tool','Use opt_out_contact to persist suppression')
            if values.outcome=='DEMO_SCHEDULED' and not db.scalar(select(Meeting.id).where(Meeting.call_id==call.id)): raise DomainError('outcome','No meeting was created')
            call.outcome=values.outcome;result={'message':'Call outcome recorded.'}
        else:
            if not lead.phone: raise DomainError('phone','No phone number bound to this contact')
            if not db.scalar(select(Suppression).where(Suppression.tenant_id==tenant,Suppression.phone==lead.phone)):
                db.add(Suppression(tenant_id=tenant,phone=lead.phone,reason=values.reason))
            ids=[]
            for other in db.scalars(select(Lead).where(Lead.tenant_id==tenant,Lead.phone==lead.phone)):
                other.opted_out=True;ids.append(other.id)
            for queued in db.scalars(select(Call).where(Call.tenant_id==tenant,Call.lead_id.in_(ids),Call.status=='QUEUED')): status(db,queued,'CANCELLED','opt_out')
            for f in db.scalars(select(FollowUp).where(FollowUp.tenant_id==tenant,FollowUp.lead_id.in_(ids),FollowUp.status=='PENDING')): f.status='BLOCKED_SUPPRESSION'
            call.outcome='OPTED_OUT';result={'message':'Your request has been recorded. We will not call this number again.'}
        db.add(ToolExecution(tenant_id=tenant,call_id=call_id,turn_id=turn_id,intent_id=intent_id,name=name,args=serialized,status='SUCCEEDED',result=result))
        event(db,tenant,'tool.succeeded',{'name':name,'intent_id':intent_id,'result':result},call_id,turn_id)
        return result
