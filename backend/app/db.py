from contextlib import contextmanager
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session as DBSession
from .config import settings
from .models import Event
engine=create_engine(settings.database_url,pool_pre_ping=True,pool_size=8,max_overflow=4,connect_args={'connect_timeout':5})
class DomainError(Exception):
    def __init__(self,code,message,status=400):
        self.code,self.message,self.status=code,message,status
        super().__init__(message)
@contextmanager
def transaction():
    with DBSession(engine,expire_on_commit=False) as db:
        with db.begin(): yield db

def owned(db,model,id,tenant,lock=False):
    q=select(model).where(model.id==id,model.tenant_id==tenant)
    if lock: q=q.with_for_update()
    obj=db.scalar(q)
    if obj is None: raise DomainError('not_found','Record not found',404)
    return obj

def public(obj):
    return {c.name:getattr(obj,c.name) for c in obj.__table__.columns if c.name not in {'password_hash','token_hash','text'}}

def event(db,tenant,kind,data=None,call=None,turn=None):
    from .observability import observe
    observe(kind,data or {},call,turn)
    db.add(Event(tenant_id=tenant,kind=kind,data=data or {},call_id=call,turn_id=turn))
