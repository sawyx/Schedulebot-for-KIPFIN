from replit import db

def create_db():
  db['users'] = {} # id - inc, username
  db['sub'] = {} # chat_id - group
  db['tsub'] = {} # chat_id - teacher

def add_user(from_id, username):
  users_db = db['users']
  users_db[from_id] = [len(users_db), username]

def exists_user(uid):
  date = db['users']
  return str(uid) in date 

def set_sub(chat_id, group):
  sub_db = db['sub']
  sub_db[chat_id] = group

def del_sub(chat_id):
  sub_db = db['sub']
  del sub_db[str(chat_id)]

def exists_sub(cid):
  sub_db = db['sub']
  return str(cid) in sub_db 

def iter_sub():
  sub_db = db['sub']
  for i, k in sub_db.items():
    yield i, k

def set_tsub(chat_id, teacher):
  tsub_db = db['tsub']
  tsub_db[chat_id] = teacher

def del_tsub(chat_id):
  tsub_db = db['tsub']
  del tsub_db[str(chat_id)]

def exists_tsub(cid):
  tsub_db = db['tsub']
  return str(cid) in tsub_db 

def len_tsub():
  tsub_db = db["tsub"]
  return len(tsub_db)

def iter_tsub():
  tsub_db = db['tsub']
  for i, k in tsub_db.items():
    yield i, k

def iter_users():
  users_db = db['users']
  for i, u in users_db.items():
    yield i, u[1]
