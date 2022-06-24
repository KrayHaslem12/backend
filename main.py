from flask import request, Flask, jsonify

import psycopg2

app = Flask(__name__)

conn = psycopg2.connect("dbname='crm' user='krayhaslem' host='localhost'")
cursor = conn.cursor()

org_id = -1

def create_all():
  cursor.execute("""
  CREATE TABLE IF NOT EXISTS Organizations (
    org_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL, 
    phone VARCHAR,
    city VARCHAR,
    state VARCHAR,
    active smallint
   );
  """)
  conn.commit()
  
  cursor.execute("SELECT org_id, name FROM Organizations WHERE name='DevPipeline';")
  results = cursor.fetchone()

  if not results:
   cursor.execute("""
      INSERT INTO Organizations
      (name, phone, city, state, active) 
      VALUES
      ('DevPipeline', '3853090807', 'Orem', 'UT', 1)
      RETURNING org_id; 
      """)

   conn.commit()
   org_id = cursor.fetchone()[0]

  else:
   org_id = results [0]

  cursor.execute("""
  CREATE TABLE IF NOT EXISTS Users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR NOT NULL, 
    last_name VARCHAR,
    email VARCHAR NOT NULL UNIQUE,
    phone VARCHAR,
    city VARCHAR,
    state VARCHAR,
    org_id int,
    active smallint
   );
  """)

  conn.commit()
  
  cursor.execute("SELECT org_id FROM Organizations WHERE name='DevPipeline';")
  org_id = cursor.fetchone()
  
  cursor.execute("SELECT email FROM users WHERE email='admin@devpipeline.com';")
  results = cursor.fetchone()
  if not results:
    cursor.execute("""
      INSERT INTO users
      (first_name, last_name, email, phone, city, state, org_id, active) 
      VALUES
      ('Admin','Admin','admin@devpipeline.com', '4357891234', 'Vernal', 'UT', %s, 1) 

    """, [org_id])
   
    conn.commit()


@app.route('/user/add', methods=['POST'])
def add_user():
   form = request.form

   fields = ['first_name', 'last_name', 'email', 'phone', 'city', 'state', 'org_id', 'acive']
   required_fields = ['first_name', 'email']
   values = []

   for field in fields:
      form_value = form.get(field)
      if form_value in required_fields and form_value == '':
         return jsonify(f'{field} is required'), 400

      values.append(form_value)

   cursor.execute("""
      INSERT INTO Users (first_name, last_name, email, phone, city, state, org_id, active)
      VALUES (%s, %s ,%s, %s, %s, %s, %s, %s)
   """, values)

   conn.commit()
   return jsonify('User added'), 200

@app.route('/organization/add', methods=['POST'])
def add_organization():
   form = request.form

   fields = ['name', 'phone', 'city', 'state', 'active']
   required_fields = ['name']
   values = []

   for field in fields:
      form_value = form.get(field)
      if form_value in required_fields and form_value == '':
         return jsonify(f'{field} is required'), 400

      values.append(form_value)

   cursor.execute("""
      INSERT INTO Organizations (name, phone, city, state, active)
      VALUES (%s, %s ,%s, %s, %s)
   """, values)

   conn.commit()
   return jsonify('Organization added'), 200


@app.route('/user/edit/<user_id>', methods=['POST'])
def edit_user(user_id, first_name = None, last_name = None, email = None, phone = None, city = None, state = None, active = None, org_id = None):
   form = request.form
   cursor.execute('SELECT user_id FROM users')
   id_list_tup = cursor.fetchall()
   if id_list_tup == []:
      return jsonify('Error: No users in db.'), 404

   id_list = []
   fields_list = []
   values = []

   for i in id_list_tup:
      id_list.append(i[0])
 
   try:
      cursor.execute('SELECT user_id, first_name, last_name, email, phone, city, state, org_id, active FROM users WHERE user_id = %s',(user_id))
      result = cursor.fetchone()
      if result:
         first_name = form.get('first_name')
         last_name = form.get('last_name')
         email = form.get('email')
         city = form.get('city')
         state = form.get('state')
         active = form.get('active')
         phone  = form.get('phone')
         org_id = form.get('org_id')
         
         
         if first_name != None:
            fields_list.append('first_name = %s')
            values.append(first_name)
         
         if last_name != None:
            fields_list.append('last_name = %s')
            values.append(last_name)

         if email != None:
            fields_list.append('email = %s')
            values.append(email)
         
         if city != None:
            fields_list.append('city = %s')
            values.append(city)
      
         if state != None:
            fields_list.append('state = %s')
            values.append(state)
                  
         if active != None:
            fields_list.append('active = %s')
            values.append(active)

         if phone != None:
            fields_list.append('phone = %s')
            values.append(phone)

         if org_id != None:
            fields_list.append('org_id = %s')
            values.append(org_id)

         values.append(user_id)

      else:
         return jsonify("Error: Check ID."), 404 
   except:
      return jsonify("Error: User not found."), 404

   fields = " , ".join(fields_list)
   query = f'UPDATE users SET {fields} WHERE user_id = %s'
  
   try:
      if int(user_id) not in id_list:
         return jsonify(' Error: user_id out of range.'),404
      cursor.execute(query,values)
      conn.commit() 
      return jsonify('User Updated'), 201
   except: 
     return jsonify('Error: Failed update.'), 400

@app.route('/organization/edit/<org_id>', methods=['POST'])
def edit_organization(org_id, name = None, phone = None, city = None, state = None, active = None):
   form = request.form
   cursor.execute('SELECT org_id FROM Organizations;')
   id_list_tup = cursor.fetchall()
   if id_list_tup == []:
      return jsonify('Error: No users in db.'), 404

   id_list = []
   fields_list = []
   values = []

   for i in id_list_tup:
      id_list.append(i[0])
 
   try:
      cursor.execute('SELECT org_id, name, phone, city, state, active FROM Organizations WHERE org_id = %s',(org_id))
      result = cursor.fetchone()
      if result:
         name = form.get('name')
         phone  = form.get('phone')
         city = form.get('city')
         state = form.get('state')
         active = form.get('active')
         
         if org_id != None:
            fields_list.append('org_id = %s')
            values.append(org_id)
         
         if name != None:
            fields_list.append('name = %s')
            values.append(name)
         
         if phone != None:
            fields_list.append('phone = %s')
            values.append(phone)
         
         if city != None:
            fields_list.append('city = %s')
            values.append(city)
      
         if state != None:
            fields_list.append('state = %s')
            values.append(state)
                  
         if active != None:
            fields_list.append('active = %s')
            values.append(active)

         values.append(org_id)

      else:
         return jsonify("Error: Check ID."), 404 
   except:
      return jsonify("Error: Organization not found."), 404

   fields = " , ".join(fields_list)
   query = f'UPDATE Organizations SET {fields} WHERE org_id = %s'
  
   try:
      print(org_id,type(org_id),id_list,type(id_list))
      if int(org_id) not in id_list:
         return jsonify(' Error: org_id out of range.'),404
      cursor.execute(query,values)
      print(query, values, type(query), type(values))
      conn.commit() 
      return jsonify('Organization Updated'), 201
   except: 
     return jsonify('Error: Failed update.'), 400
 
@app.route('/user/delete/<user_id>', methods=['DELETE'])
def delete_user(user_id):
   cursor.execute('SELECT user_id FROM users')
   id_list_tup = cursor.fetchall()
   id_list = []
   if id_list_tup == []:
      return jsonify('Error: No users in db.'), 404
   for i in id_list_tup:
      id_list.append(i[0])
   try:
      if int(user_id) not in id_list:
         return jsonify('Error: user_id out of range.'),404
      else:
         cursor.execute('DELETE FROM users WHERE user_id = %s', (user_id,))
         conn.commit()
         return jsonify('User Deleted'), 201
   except:
     return jsonify('Error: Failed deletion.'), 400

@app.route('/organization/delete/<org_id>', methods=['DELETE'])
def delete_organization(org_id):
   cursor.execute('SELECT org_id FROM organizations')
   id_list_tup = cursor.fetchall()
   id_list = []
   if id_list_tup == []:
      return jsonify('Error: No organizations in db.'), 404 
   for i in id_list_tup:
      id_list.append(i[0])
   try:
      if int(org_id) not in id_list:
         return jsonify('Error: org_id out of range.'),404
      else:
         cursor.execute('DELETE FROM organizations WHERE org_id = %s', (org_id,))
         conn.commit()
         return jsonify('Organization Deleted'), 201
   except:
     return jsonify('Error: Failed deletion.'), 400

@app.route('/user/<user_id>', methods = ['GET'])
def get_user(user_id):
   cursor.execute('SELECT user_id FROM users')
   id_list_tup = cursor.fetchall()
   id_list = []
   if id_list_tup == []:
      return jsonify('Error: No users in db.'), 404
   for i in id_list_tup:
      id_list.append(i[0])
   try:
      if int(user_id) not in id_list:
         return jsonify('Error: user_id out of range.'),404
      else:
         cursor.execute("""
   SELECT 
      u.user_id, u.first_name, u.last_name, u.email,
      u.phone, u.city, u.state, u.org_id, u.active, 
      o.org_id, o.name, o.phone, o.city, o.state, o.active
   FROM Users u
   JOIN Organizations o
   ON o.org_id = u.org_id
   WHERE u.user_id = %s
   """, (user_id,))
         organization_list = cursor.fetchone()
         user_dict = {
         "user_id": organization_list[0],
         "first_name": organization_list[1],
         "last_name": organization_list[2],
         "email": organization_list[3],
         "phone": organization_list[4],
         "city": organization_list[5],
         "state": organization_list[6],
         "active": organization_list[8],
         "organization": {
            "org_id": organization_list[9],
            "name": organization_list[10],
            "phone": organization_list[11],
            "city": organization_list[12],
            "state": organization_list[13],
            "active": organization_list[14]
         }

      } 
         return jsonify(user_dict), 200
   except:
      return jsonify('Error: Failed to get User.'), 400

@app.route('/organization/<org_id>', methods = ['GET'])
def get_organization(org_id):
   cursor.execute('SELECT org_id FROM organizations')
   id_list_tup = cursor.fetchall()
   id_list = []
   if id_list_tup == []:
      return jsonify('Error: No organizations in db.'), 404
   for i in id_list_tup:
      id_list.append(i[0])
   try:
      if int(org_id) not in id_list:
         return jsonify('Error: org_id out of range.'),404
      else:
         cursor.execute("""
            SELECT 
               org_id, name, phone, city, state, active 
            FROM 
               organizations
            WHERE 
               org_id=%s;
            """, (org_id,))
        
         organization_list = cursor.fetchone()
         user_dict = {
         "org_id": organization_list[0],
         "name": organization_list[1],
         "phone": organization_list[2],
         "city": organization_list[3],
         "state": organization_list[4],
         "active": organization_list[5]
         }
       
         return jsonify(user_dict), 200
   except:
      return jsonify('Error: Failed to get User.'), 400

@app.route('/user/list', methods=['GET'])
def get_users():
   list_users = []
   cursor.execute("""
   SELECT 
      u.user_id, u.first_name, u.last_name, u.email,
      u.phone, u.city, u.state, u.org_id, u.active, 
      o.org_id, o.name, o.phone, o.city, o.state, o.active
   FROM Users u
   JOIN Organizations o
   ON o.org_id = u.org_id;
   """)

   org_list_tuples = cursor.fetchall()
   for organization_list in org_list_tuples:
      user_dict = {
         "user_id": organization_list[0],
         "first_name": organization_list[1],
         "last_name": organization_list[2],
         "email": organization_list[3],
         "phone": organization_list[4],
         "city": organization_list[5],
         "state": organization_list[6],
         "active": organization_list[8],
         "organization": {
            "org_id": organization_list[9],
            "name": organization_list[10],
            "phone": organization_list[11],
            "city": organization_list[12],
            "state": organization_list[13],
            "active": organization_list[14]
         }

      } 

      list_users.append(user_dict)

   return jsonify(list_users), 200

@app.route('/organizations/list', methods=['GET'])
def get_organizations():
   list_organizations = []
   cursor.execute("""
   SELECT 
      org_id, name, phone, city, state, active 
   FROM 
      organizations;
   """)

   org_list_tuples = cursor.fetchall()
   for organization_list in org_list_tuples:
      org_dict = {
         "org_id": organization_list[0],
         "name": organization_list[1],
         "phone": organization_list[2],
         "city": organization_list[3],
         "state": organization_list[4],
         "active": organization_list[5]
         }

      list_organizations.append(org_dict)

   return jsonify(list_organizations), 200

@app.route('/user/search/<search_term>', methods=['GET'])
def search_users(search_term):
   search_list = []
   search_term = search_term.lower()
   cursor.execute("""
   SELECT 
      user_id, first_name, last_name, email, phone, city, state, org_id, active 
   FROM 
      users 
   WHERE 
      LOWER(first_name) LIKE %s OR LOWER(last_name) LIKE %s OR LOWER(email) LIKE %s OR LOWER(city) LIKE %s or LOWER(state) LIKE %s', (f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',f'%{search_term}%')
   """)
   search_items = cursor.fetchall()
   for i in search_items:
      search_list.append(i)
   return jsonify({ 'results': search_list })

@app.route('/organization/search/<search_term>', methods=['GET'])
def search_organization(search_term):
   search_list = []
   search_term = search_term.lower()
   cursor.execute("""
   SELECT 
      org_id, name, phone, city, state, active 
   FROM 
      organizations 
   WHERE 
      LOWER(name) LIKE %s OR LOWER(city) LIKE %s or LOWER(state) LIKE %s', (f'%{search_term}%',f'%{search_term}%',f'%{search_term}%')
   """)
   search_items = cursor.fetchall()
   for i in search_items:
      search_list.append(i)
   return jsonify({ 'results': search_list })

if __name__ == '__main__':
   create_all()
   app.run()