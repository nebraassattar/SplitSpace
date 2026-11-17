"""Integration tests use isolated SQLite, never Supabase."""
import os
os.environ.setdefault('DATABASE_URL','sqlite://')
import pytest
from app import create_app
from models import db
from api import split_cents

@pytest.fixture
def client():
    app=create_app('sqlite://')
    app.config.update(TESTING=True)
    with app.app_context():
        db.drop_all(); db.create_all()
        yield app.test_client()
        db.session.remove(); db.drop_all()

def register(c,name):
    r=c.post('/api/auth/register',json={'email':name+'@example.com','display_name':name,'password':'password123'})
    assert r.status_code==201
    return r.json['id']

def test_rounding():
    assert split_cents(1000,[3,1,2])=={1:334,2:333,3:333}
    assert split_cents(100,[4])=={4:100}

def test_auth_households_privacy(client):
    a=register(client,'a')
    h=client.post('/api/households',json={'name':'Apt'}).json
    assert len(h['invite_code'])==8
    client.post('/api/auth/logout')
    b=register(client,'b')
    assert client.get(f"/api/households/{h['id']}").status_code==404
    assert client.get(f"/api/households/{h['id']}/chores").status_code==404
    assert client.post('/api/households/join',json={'invite_code':h['invite_code']}).status_code==200
    assert client.get(f"/api/households/{h['id']}").status_code==200
    assert client.post('/api/households/join',json={'invite_code':h['invite_code']}).status_code==200
    assert client.post('/api/auth/login',json={'email':'a@example.com','password':'wrong'}).status_code==401
    assert client.post('/api/auth/register',json={'email':'A@example.com','display_name':'A','password':'password123'}).status_code==409

def test_expenses_settlement_and_chores(client):
    a=register(client,'a'); h=client.post('/api/households',json={'name':'Apt'}).json; hid=h['id']; code=h['invite_code']
    client.post('/api/auth/logout'); b=register(client,'b'); client.post('/api/households/join',json={'invite_code':code})
    client.post('/api/auth/logout'); c=register(client,'c'); client.post('/api/households/join',json={'invite_code':code})
    expense={'description':'Groceries','amount_cents':6000,'date':'2026-11-11','payer_id':a,'participant_ids':[a,b,c]}
    r=client.post(f'/api/households/{hid}/expenses',json=expense)
    assert r.status_code==201
    assert [s['share_cents'] for s in r.json['shares']]==[2000,2000,2000]
    balances=client.get(f'/api/households/{hid}/balances').json
    assert len(balances['debts'])==2
    client.post('/api/auth/logout'); client.post('/api/auth/login',json={'email':'b@example.com','password':'password123'})
    r=client.post(f'/api/households/{hid}/settlements',json={'from_user_id':b,'to_user_id':a,'amount_cents':2000,'date':'2026-11-12'})
    assert r.status_code==201
    assert client.get(f'/api/households/{hid}/balances').json['debts']==[{'from_user_id':c,'to_user_id':a,'amount_cents':2000}]
    r=client.post(f'/api/households/{hid}/chores',json={'title':'Trash','assignee_id':c,'due_date':'2026-11-20'})
    assert r.status_code==201
    cid=r.json['id']
    assert len(client.get(f'/api/households/{hid}/chores?status=open').json)==1
    assert client.patch(f'/api/households/{hid}/chores/{cid}',json={'completed':True}).status_code==200
    assert len(client.get(f'/api/households/{hid}/chores?status=done').json)==1
    assert client.patch(f'/api/households/{hid}/chores/{cid}',json={'completed':False}).status_code==200
    assert client.post(f'/api/households/{hid}/chores',json={'title':'Bad','assignee_id':999,'due_date':'2026-11-20'}).status_code==400
