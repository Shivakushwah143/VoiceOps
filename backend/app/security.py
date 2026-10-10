import hashlib, hmac, secrets
from datetime import timedelta
from sqlalchemy import select
from .models import User,Tenant,Session,now
from .db import transaction,DomainError

def password_hash(password):
    if not 12<=len(password)<=200: raise DomainError('password','Password must contain 12–200 characters')
    salt=secrets.token_bytes(16)
    return salt.hex()+':'+hashlib.pbkdf2_hmac('sha256',password.encode(),salt,600000).hex()
def verify(password,encoded):
    salt,digest=encoded.split(':')
    return hmac.compare_digest(hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),600000).hex(),digest)
def digest(token): return hashlib.sha256(token.encode()).hexdigest()
DUMMY=password_hash('invalid-password-never-used')
def login(email,password):
    with transaction() as db:
        u=db.scalar(select(User).where(User.email==email.lower().strip()))
        match=verify(password,u.password_hash if u else DUMMY)
        if not u or not match or not u.active or not db.get(Tenant,u.tenant_id).active:
            raise DomainError('login','Invalid credentials',401)
        token=secrets.token_urlsafe(32)
        db.add(Session(user_id=u.id,token_hash=digest(token),expires_at=now()+timedelta(hours=8)))
        return token

def principal(token):
    if not token: raise DomainError('auth','Sign in required',401)
    with transaction() as db:
        s=db.scalar(select(Session).where(Session.token_hash==digest(token),Session.expires_at>now()))
        u=db.get(User,s.user_id) if s else None
        if not u or not u.active or not db.get(Tenant,u.tenant_id).active:
            raise DomainError('auth','Session expired or revoked',401)
        return u

def admin(u):
    if u.role!='ADMIN': raise DomainError('forbidden','Administrator permission required',403)
