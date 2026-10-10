from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey, JSON, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

def now(): return datetime.now(timezone.utc)
def uid(): return str(uuid4())
class Base(DeclarativeBase): pass
class Record:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=now)
class Owned(Record):
    tenant_id: Mapped[str] = mapped_column(ForeignKey('tenants.id'),index=True)
class Tenant(Record,Base):
    __tablename__='tenants'
    name: Mapped[str] = mapped_column(String(200))
    active: Mapped[bool] = mapped_column(default=True)
    dispatch_blocked: Mapped[bool] = mapped_column(default=False)
class User(Owned,Base):
    __tablename__='users'
    email: Mapped[str] = mapped_column(String(254),unique=True)
    name: Mapped[str] = mapped_column(String(200))
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(20),default='OPERATOR')
    active: Mapped[bool] = mapped_column(default=True)
class Session(Record,Base):
    __tablename__='sessions'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'),index=True)
    token_hash: Mapped[str] = mapped_column(String(64),unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
class Lead(Owned,Base):
    __tablename__='leads'
    name: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str] = mapped_column(String(20),default='',index=True)
    company: Mapped[str] = mapped_column(String(200),default='')
    interest: Mapped[str] = mapped_column(String(500),default='')
    status: Mapped[str] = mapped_column(String(30),default='NEW')
    consent: Mapped[str] = mapped_column(String(20),default='UNKNOWN')
    consent_source: Mapped[str] = mapped_column(String(500),default='')
    consent_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)
    opted_out: Mapped[bool] = mapped_column(default=False)
    archived: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[list] = mapped_column(JSON,default=list)
class Suppression(Owned,Base):
    __tablename__='suppressions'
    __table_args__=(UniqueConstraint('tenant_id','phone'),)
    phone: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str] = mapped_column(String(500))
class KnowledgeBase(Owned,Base):
    __tablename__='knowledge_bases'
    name: Mapped[str] = mapped_column(String(200))
    archived: Mapped[bool] = mapped_column(default=False)
class Document(Owned,Base):
    __tablename__='documents'
    __table_args__=(UniqueConstraint('kb_id','digest'),)
    kb_id: Mapped[str] = mapped_column(ForeignKey('knowledge_bases.id'),index=True)
    name: Mapped[str] = mapped_column(String(250))
    digest: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(30),default='RECEIVED')
    text: Mapped[str] = mapped_column(Text,default='')
    error: Mapped[str] = mapped_column(String(200),default='')
    chunk_count: Mapped[int] = mapped_column(default=0)
class Campaign(Owned,Base):
    __tablename__='campaigns'
    name: Mapped[str] = mapped_column(String(200))
    objective: Mapped[str] = mapped_column(String(2000))
    kb_id: Mapped[str] = mapped_column(ForeignKey('knowledge_bases.id'))
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    lead_ids: Mapped[list] = mapped_column(JSON,default=list)
    status: Mapped[str] = mapped_column(String(30),default='DRAFT')
    mode: Mapped[str] = mapped_column(String(20),default='production')
class Call(Owned,Base):
    __tablename__='calls'
    __table_args__=(UniqueConstraint('tenant_id','request_key'),)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    lead_id: Mapped[str|None] = mapped_column(ForeignKey('leads.id'),nullable=True)
    campaign_id: Mapped[str|None] = mapped_column(ForeignKey('campaigns.id'),nullable=True)
    kb_id: Mapped[str|None] = mapped_column(ForeignKey('knowledge_bases.id'),nullable=True)
    request_key: Mapped[str] = mapped_column(String(150))
    transport: Mapped[str] = mapped_column(String(20))
    direction: Mapped[str] = mapped_column(String(20),default='outbound')
    mode: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(30),default='CREATED',index=True)
    provider_id: Mapped[str|None] = mapped_column(String(100),nullable=True,unique=True)
    provider_request_id: Mapped[str|None] = mapped_column(String(100),nullable=True)
    objective: Mapped[str] = mapped_column(String(2000),default='Answer questions and offer a demo when requested.')
    outcome: Mapped[str] = mapped_column(String(30),default='UNRESOLVED')
    summary_status: Mapped[str] = mapped_column(String(30),default='NOT_READY')
    summary: Mapped[dict] = mapped_column(JSON,default=dict)
    end_reason: Mapped[str] = mapped_column(String(200),default='')
    connected_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)
    ended_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True),nullable=True)
class Turn(Owned,Base):
    __tablename__='turns'
    call_id: Mapped[str] = mapped_column(ForeignKey('calls.id'),index=True)
    user_text: Mapped[str] = mapped_column(Text)
    assistant_text: Mapped[str] = mapped_column(Text,default='')
    status: Mapped[str] = mapped_column(String(30),default='THINKING')
    delivery: Mapped[str] = mapped_column(String(30),default='NOT_SENT')
    sources: Mapped[list] = mapped_column(JSON,default=list)
class Event(Owned,Base):
    __tablename__='events'
    call_id: Mapped[str|None] = mapped_column(ForeignKey('calls.id'),nullable=True,index=True)
    turn_id: Mapped[str|None] = mapped_column(ForeignKey('turns.id'),nullable=True)
    kind: Mapped[str] = mapped_column(String(60))
    data: Mapped[dict] = mapped_column(JSON,default=dict)
class ToolExecution(Owned,Base):
    __tablename__='tool_executions'
    __table_args__=(UniqueConstraint('tenant_id','intent_id'),)
    call_id: Mapped[str] = mapped_column(ForeignKey('calls.id'),index=True)
    turn_id: Mapped[str] = mapped_column(ForeignKey('turns.id'))
    intent_id: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(50))
    args: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(30))
    result: Mapped[dict] = mapped_column(JSON,default=dict)
class Meeting(Owned,Base):
    __tablename__='meetings'
    lead_id: Mapped[str] = mapped_column(ForeignKey('leads.id'))
    call_id: Mapped[str|None] = mapped_column(ForeignKey('calls.id'),nullable=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    purpose: Mapped[str] = mapped_column(String(500))
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    timezone: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30),default='SCHEDULED')
class FollowUp(Owned,Base):
    __tablename__='followups'
    lead_id: Mapped[str] = mapped_column(ForeignKey('leads.id'))
    call_id: Mapped[str|None] = mapped_column(ForeignKey('calls.id'),nullable=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    purpose: Mapped[str] = mapped_column(String(500))
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    timezone: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30),default='PENDING')
