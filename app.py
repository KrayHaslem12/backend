import json
from flask import request, Flask, jsonify, Response
from flask_bcrypt import generate_password_hash

import psycopg2

app = Flask(__name__)

conn = psycopg2.connect("dbname='backend' user='krayhaslem' host='localhost'")
cursor = conn.cursor()

@app.route('/user/add', methods=['POST'])
def add_user():
   form = request.form
   first_name = form.get('first_name')
   last_name = form.get('last_name')
   email = form.get('email')
   password = form.get('password')
   city = form.get('city')
   state = form.get('state')
   active = form.get('active')
   hashed_pw = generate_password_hash(password)

   if first_name == '':
      return jsonify('Missing required field first_name') , 400
   if email == '':
      return jsonify('Missing required field email') , 400
   if password == '':
      return jsonify('Missing required field password') , 400
   if active == None:
      active = True
   try:
      cursor.execute('INSERT INTO users (first_name, last_name, email, password, city, state, active) VALUES (%s, %s, %s, %s, %s, %s, %s)', (first_name, last_name, email, hashed_pw, city, state, active))
      conn.commit()
      return jsonify('User created'), 201
   except:
     return jsonify('Error: User not created.'), 400

@app.route('/user/edit/<user_id>', methods=['POST'])
def edit_user(user_id, first_name = None, last_name = None, email = None, password = None, city = None, state = None, active = None):
   form = request.form
   cursor.execute('SELECT user_id FROM users')
   id_list_tup = cursor.fetchall()
   try:
      cursor.execute('SELECT user_id, first_name, last_name, email, password, city, state, active FROM users WHERE user_id = %s',(user_id))
      result = cursor.fetchone()
   except:
      return jsonify("Error: User not found."), 404

   id_list = []
   fields_list = []
   values = []

   if id_list_tup == []:
      return jsonify('Error: No users in db.'), 404
   
   for i in id_list_tup:
      id_list.append(i[0])
 
   if result:
      first_name = form.get('first_name')
      last_name = form.get('last_name')
      email = form.get('email')
      city = form.get('city')
      state = form.get('state')
      active = form.get('active')
      password = form.get('password')
      
      
      if first_name != None:
         fields_list.append('first_name = %s')
         values.append(first_name)
      
      if last_name != None:
         fields_list.append('last_name = %s')
         values.append(last_name)

      if email != None:
         fields_list.append('email = %s')
         values.append(email)

      if password != None:
         hashed_pw = generate_password_hash(password)
         fields_list.append('password = %s')
         values.append(hashed_pw)
      
      if city != None:
         fields_list.append('city = %s')
         values.append(city)
   
      if state != None:
         fields_list.append('state = %s')
         values.append(state)
                
      if active != None:
         fields_list.append('active = %s')
         values.append(active)
      values.append(user_id)
   else:
      return jsonify("Error: No results."), 404 
   fields = " , ".join(fields_list)
   # fields = "first_name = %s, last_name = %s, email = %s, password = %s, city = %s, state = %s, active = %s"
   query = f'UPDATE users SET {fields} WHERE user_id = %s'
   try:
      if int(user_id) not in id_list:
         return jsonify('Error: user_id out of range.'),404
      # print(query,values,type(query),type(values))
      cursor.execute(query,values)
      conn.commit()
      return jsonify('User Updated'), 201
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
         cursor.execute('SELECT user_id, first_name, last_name, email, password, city, state, active FROM users WHERE user_id = %s', (user_id,))
         user_list = cursor.fetchone()
         fields = ['user_id', 'first_name', 'last_name', 'email', 'password', 'city', 'state', 'active']
         user_dict = {}
         for key,value in enumerate(fields):
            user_dict[value] = user_list[key]
         return jsonify(user_dict), 200
   except:
      return jsonify('Error: Failed to get User.'), 400

@app.route('/user/list', methods=['GET'])
def get_users():
   list_users = []
   cursor.execute('SELECT user_id, first_name, last_name, email, password, city, state, active FROM users')
   fields = ['user_id', 'first_name', 'last_name', 'email', 'password', 'city', 'state', 'active']
   user_list_tuples = cursor.fetchall()
   for user_list in user_list_tuples:
      user_dict = {} 
      for key,value in enumerate(user_list):
         user_dict[fields[key]] = value
      list_users.append(user_dict)
   return jsonify(list_users), 200

@app.route('/user/search/<search_term>', methods=['GET'])
def search_users(search_term):
   search_list = []
   search_term = search_term.lower()
   cursor.execute('SELECT user_id, first_name, last_name, email, password, city, state, active FROM users WHERE LOWER(first_name) LIKE %s OR LOWER(last_name) LIKE %s OR LOWER(email) LIKE %s OR LOWER(city) LIKE %s or LOWER(state) LIKE %s', (f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',f'%{search_term}%',f'%{search_term}%'))
   search_items = cursor.fetchall()
   for i in search_items:
      search_list.append(i)
   return jsonify({ 'results': search_list })

if __name__ == '__main__':
   app.run()