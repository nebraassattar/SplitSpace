"""SplitSpace MVP API. Uses existing SQLAlchemy models from models.py."""
import secrets
import string
from collections import defaultdict
from datetime import date, datetime, timezone
from functools import wraps
from flask import Blueprint, jsonify, request, session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Household, Membership, Expense, ExpenseShare, Settlement, Chore

api = Blueprint('api', __name__, url_prefix='/api')

def fail(message, status=400): return jsonify(error=message), status

def body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}

def valid_id(v): return type(v) is int and v > 0

def valid_amount(v, limit=10_000_000): return valid_id(v) and v <= limit

def valid_text(v, maxlen): return isinstance(v, str) and 0 < len(v.strip()) <= maxlen

def parse_date(v):
    try:
        if not isinstance(v, str): return None
        return date.fromisoformat(v) if len(v) == 10 else None
    except ValueError: return None

def current_user():
    uid = session.get('user_id')
    return db.session.get(User, uid) if valid_id(uid) else None

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if current_user() is None: return fail('Login required', 401)
        return fn(*args, **kwargs)
    return wrapper

def member(hid):
    user = current_user()
    if not user: return None
    return db.session.scalar(select(Membership).where(Membership.household_id == hid, Membership.user_id == user.id))

def household_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(hid, *args, **kwargs):
        membership = member(hid)
        if membership is None: return fail('Not found', 404)
        return fn(hid, membership, *args, **kwargs)
    return wrapper

def can_edit(record, membership):
    return record.created_by == membership.user_id or membership.role == 'owner'

def all_member_ids(hid):
    return set(db.session.scalars(select(Membership.user_id).where(Membership.household_id == hid)).all())

def user_json(u): return {'id':u.id,'email':u.email,'display_name':u.display_name}

def household_json(h, membership):
    memberships = db.session.scalars(select(Membership).where(Membership.household_id == h.id).order_by(Membership.id)).all()
    return {'id':h.id,'name':h.name,'invite_code':h.invite_code,'role':membership.role,
            'members':[{'id':m.user_id,'display_name':db.session.get(User,m.user_id).display_name,'role':m.role} for m in memberships]}

def expense_json(e):
    return {'id':e.id,'description':e.description,'amount_cents':e.amount_cents,'date':e.date.isoformat(),
            'payer_id':e.payer_id,'created_by':e.created_by,
            'shares':[{'user_id':s.user_id,'share_cents':s.share_cents} for s in sorted(e.shares,key=lambda x:x.user_id)]}

def settlement_json(s):
    return {'id':s.id,'from_user_id':s.from_user_id,'to_user_id':s.to_user_id,'amount_cents':s.amount_cents,
            'date':s.date.isoformat(),'note':s.note,'created_by':s.created_by}

def chore_json(c):
    return {'id':c.id,'title':c.title,'assignee_id':c.assignee_id,'due_date':c.due_date.isoformat(),
            'completed_at':c.completed_at.isoformat() if c.completed_at else None,'created_by':c.created_by}

@api.post('/auth/register')
def register():
    d=body(); email=d.get('email'); password=d.get('password'); name=d.get('display_name')
    if not isinstance(email,str) or '@' not in email or len(email)>255 or not valid_text(name,80) or not isinstance(password,str) or len(password)<8:
        return fail('Provide a valid email, display name and password of at least 8 characters')
    email=email.strip().lower()
    if db.session.scalar(select(User).where(User.email==email)): return fail('Email already registered',409)
    u=User(email=email,display_name=name.strip(),password_hash=generate_password_hash(password, method="pbkdf2:sha256"))
    db.session.add(u)
    try: db.session.commit()
    except IntegrityError:
        db.session.rollback(); return fail('Email already registered',409)
    session.clear(); session['user_id']=u.id
    return jsonify(user_json(u)),201

@api.post('/auth/login')
def login():
    d=body(); email=d.get('email',''); password=d.get('password','')
    if not isinstance(email,str) or not isinstance(password,str): return fail('Invalid email or password',401)
    u=db.session.scalar(select(User).where(User.email==email.strip().lower()))
    if not u or not check_password_hash(u.password_hash,password): return fail('Invalid email or password',401)
    session.clear(); session['user_id']=u.id
    return jsonify(user_json(u))

@api.post('/auth/logout')
def logout(): session.clear(); return '',204

@api.get('/auth/me')
@login_required
def me(): return jsonify(user_json(current_user()))

@api.get('/households')
@login_required
def households():
    ms=db.session.scalars(select(Membership).where(Membership.user_id==current_user().id).order_by(Membership.id)).all()
    return jsonify([household_json(db.session.get(Household,m.household_id),m) for m in ms])

@api.post('/households')
@login_required
def create_household():
    name=body().get('name')
    if not valid_text(name,80): return fail('Household name is required (up to 80 characters)')
    for _ in range(5):
        code=''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(8))
        if not db.session.scalar(select(Household).where(Household.invite_code==code)): break
    h=Household(name=name.strip(),invite_code=code,created_by=current_user().id)
    db.session.add(h); db.session.flush()
    m=Membership(household_id=h.id,user_id=current_user().id,role='owner')
    db.session.add(m); db.session.commit()
    return jsonify(household_json(h,m)),201

@api.post('/households/join')
@login_required
def join_household():
    code=body().get('invite_code')
    if not isinstance(code,str): return fail('Invalid invite code',404)
    h=db.session.scalar(select(Household).where(Household.invite_code==code.strip().upper()))
    if not h: return fail('Invalid invite code',404)
    m=member(h.id)
    if not m:
        m=Membership(household_id=h.id,user_id=current_user().id,role='member')
        db.session.add(m)
        try: db.session.commit()
        except IntegrityError:
            db.session.rollback(); m=member(h.id)
    return jsonify(household_json(h,m))

@api.get('/households/<int:hid>')
@household_required
def get_household(hid,m): return jsonify(household_json(db.session.get(Household,hid),m))

def split_cents(amount, ids):
    ids=sorted(ids); base, remainder=divmod(amount,len(ids))
    return {uid:base+(i<remainder) for i,uid in enumerate(ids)}

def validate_expense(d,hid):
    description=d.get('description'); amount=d.get('amount_cents'); payer=d.get('payer_id'); ids=d.get('participant_ids'); when=parse_date(d.get('date'))
    members=all_member_ids(hid)
    if not valid_text(description,120) or not valid_amount(amount) or not when: return None,'Invalid description, amount or date'
    if not valid_id(payer) or payer not in members: return None,'Payer must be a household member'
    if not isinstance(ids,list) or not ids or any(not valid_id(x) for x in ids) or len(set(ids))!=len(ids) or not set(ids)<=members:
        return None,'Participants must be distinct household members'
    return (description.strip(),amount,when,payer,split_cents(amount,ids)),None

@api.route('/households/<int:hid>/expenses',methods=['GET','POST'])
@household_required
def expenses(hid,m):
    if request.method=='GET':
        rows=db.session.scalars(select(Expense).where(Expense.household_id==hid).order_by(Expense.date.desc(),Expense.id.desc())).all()
        return jsonify([expense_json(e) for e in rows])
    fields,error=validate_expense(body(),hid)
    if error: return fail(error)
    desc,amount,when,payer,shares=fields
    e=Expense(household_id=hid,description=desc,amount_cents=amount,date=when,payer_id=payer,created_by=m.user_id)
    e.shares=[ExpenseShare(user_id=uid,share_cents=cents) for uid,cents in shares.items()]
    db.session.add(e); db.session.commit()
    return jsonify(expense_json(e)),201

@api.route('/households/<int:hid>/expenses/<int:eid>',methods=['PUT','DELETE'])
@household_required
def expense_detail(hid,m,eid):
    e=db.session.scalar(select(Expense).where(Expense.id==eid,Expense.household_id==hid))
    if not e: return fail('Not found',404)
    if not can_edit(e,m): return fail('Not allowed',403)
    if request.method=='DELETE':
        db.session.delete(e); db.session.commit(); return '',204
    fields,error=validate_expense(body(),hid)
    if error: return fail(error)
    e.description,e.amount_cents,e.date,e.payer_id,shares=fields
    e.shares=[ExpenseShare(user_id=uid,share_cents=cents) for uid,cents in shares.items()]
    db.session.commit(); return jsonify(expense_json(e))

def compute_balances(hid):
    # Pairwise netting, without household-wide debt simplification.
    pair=defaultdict(int)
    expenses=db.session.scalars(select(Expense).where(Expense.household_id==hid)).all()
    for e in expenses:
        for s in e.shares:
            if s.user_id!=e.payer_id:
                pair[(s.user_id,e.payer_id)]+=s.share_cents
    settlements=db.session.scalars(select(Settlement).where(Settlement.household_id==hid)).all()
    for s in settlements: pair[(s.from_user_id,s.to_user_id)]-=s.amount_cents
    debts=[]; net={uid:0 for uid in all_member_ids(hid)}
    seen=set()
    for a,b in sorted(pair):
        key=tuple(sorted((a,b)))
        if key in seen: continue
        seen.add(key)
        diff=pair[(a,b)]-pair[(b,a)]
        if diff==0: continue
        sender,receiver=(a,b) if diff>0 else (b,a)
        amount=abs(diff)
        debts.append({'from_user_id':sender,'to_user_id':receiver,'amount_cents':amount})
        net[sender]-=amount; net[receiver]+=amount
    debts.sort(key=lambda x:(x['from_user_id'],x['to_user_id']))
    return {'debts':debts,'net':[{'user_id':uid,'net_cents':net[uid]} for uid in sorted(net)]}

@api.get('/households/<int:hid>/balances')
@household_required
def balances(hid,m): return jsonify(compute_balances(hid))

@api.route('/households/<int:hid>/settlements',methods=['GET','POST'])
@household_required
def settlements(hid,m):
    if request.method=='GET':
        rows=db.session.scalars(select(Settlement).where(Settlement.household_id==hid).order_by(Settlement.date.desc(),Settlement.id.desc())).all()
        return jsonify([settlement_json(s) for s in rows])
    d=body(); sender=d.get('from_user_id'); receiver=d.get('to_user_id'); amount=d.get('amount_cents'); when=parse_date(d.get('date')); note=d.get('note','')
    members=all_member_ids(hid)
    if not valid_id(sender) or not valid_id(receiver) or sender==receiver or sender not in members or receiver not in members: return fail('Both parties must be different household members')
    if not valid_amount(amount) or not when or not isinstance(note,str) or len(note)>120: return fail('Invalid amount, date or note')
    if m.role!='owner' and m.user_id not in (sender,receiver): return fail('Not allowed',403)
    outstanding=next((x['amount_cents'] for x in compute_balances(hid)['debts'] if x['from_user_id']==sender and x['to_user_id']==receiver),0)
    if amount>outstanding: return fail('Payment exceeds outstanding debt')
    s=Settlement(household_id=hid,from_user_id=sender,to_user_id=receiver,amount_cents=amount,date=when,note=note,created_by=m.user_id)
    db.session.add(s); db.session.commit(); return jsonify(settlement_json(s)),201

@api.delete('/households/<int:hid>/settlements/<int:sid>')
@household_required
def delete_settlement(hid,m,sid):
    s=db.session.scalar(select(Settlement).where(Settlement.id==sid,Settlement.household_id==hid))
    if not s: return fail('Not found',404)
    if not can_edit(s,m): return fail('Not allowed',403)
    db.session.delete(s); db.session.commit(); return '',204

@api.route('/households/<int:hid>/chores',methods=['GET','POST'])
@household_required
def chores(hid,m):
    if request.method=='GET':
        status=request.args.get('status','open')
        if status not in ('open','done'): return fail('Invalid status')
        q=select(Chore).where(Chore.household_id==hid)
        q=q.where(Chore.completed_at.is_(None) if status=='open' else Chore.completed_at.is_not(None))
        rows=db.session.scalars(q.order_by(Chore.due_date,Chore.id)).all()
        return jsonify([chore_json(c) for c in rows])
    d=body(); title=d.get('title'); assignee=d.get('assignee_id'); due=parse_date(d.get('due_date'))
    if not valid_text(title,120) or not due: return fail('Invalid title or due date')
    if not valid_id(assignee) or assignee not in all_member_ids(hid): return fail('Assignee must be a household member')
    c=Chore(household_id=hid,title=title.strip(),assignee_id=assignee,due_date=due,created_by=m.user_id)
    db.session.add(c); db.session.commit(); return jsonify(chore_json(c)),201

@api.route('/households/<int:hid>/chores/<int:cid>',methods=['PATCH','DELETE'])
@household_required
def chore_detail(hid,m,cid):
    c=db.session.scalar(select(Chore).where(Chore.id==cid,Chore.household_id==hid))
    if not c: return fail('Not found',404)
    if request.method=='DELETE':
        if not can_edit(c,m): return fail('Not allowed',403)
        db.session.delete(c); db.session.commit(); return '',204
    d=body()
    if not d or set(d)-{'title','assignee_id','due_date','completed'}: return fail('Invalid fields')
    if any(k in d for k in ('title','assignee_id','due_date')) and not can_edit(c,m): return fail('Not allowed',403)
    if 'title' in d:
        if not valid_text(d['title'],120): return fail('Invalid title')
    if 'assignee_id' in d:
        if not valid_id(d['assignee_id']) or d['assignee_id'] not in all_member_ids(hid): return fail('Assignee must be a household member')
    if 'due_date' in d and not parse_date(d['due_date']): return fail('Invalid date')
    if 'completed' in d and type(d['completed']) is not bool: return fail('Invalid completed flag')
    if 'title' in d: c.title=d['title'].strip()
    if 'assignee_id' in d: c.assignee_id=d['assignee_id']
    if 'due_date' in d: c.due_date=parse_date(d['due_date'])
    if 'completed' in d:
        if d['completed'] and c.completed_at is None: c.completed_at=datetime.now(timezone.utc)
        elif not d['completed']: c.completed_at=None
    db.session.commit(); return jsonify(chore_json(c))
