import argparse,getpass
from sqlalchemy import select,text
from .models import Base,Tenant,User
from .db import engine,transaction
from .security import password_hash

def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['init-db','bootstrap']);args=parser.parse_args()
    if args.command=='init-db':
        with engine.begin() as connection:
            connection.execute(text('SELECT pg_advisory_xact_lock(791237)'))
            Base.metadata.create_all(connection)
            connection.execute(text('CREATE TABLE IF NOT EXISTS schema_version (version integer PRIMARY KEY)'))
            connection.execute(text('INSERT INTO schema_version VALUES (1) ON CONFLICT DO NOTHING'))
        print('Schema version 1 initialized');return
    name=input('Tenant name: ').strip();email=input('Administrator email: ').strip().lower();password=getpass.getpass('Password (12+ characters): ')
    if not name or '@' not in email:raise SystemExit('Tenant name and valid email required')
    encoded=password_hash(password)
    with transaction() as db:
        if db.scalar(select(User.id).where(User.email==email)):raise SystemExit('Account already exists')
        tenant=Tenant(name=name);db.add(tenant);db.flush();db.add(User(tenant_id=tenant.id,name='Administrator',email=email,password_hash=encoded,role='ADMIN'))
    print('Administrator created')
if __name__=='__main__':main()
