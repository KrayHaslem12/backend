from flask import request, Flask, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import marshmallow as ma
import psycopg2

app = Flask(__name__)

database_host = "127.0.0.1:5432"
database_name = "crm"
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{database_host}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma  = Marshmallow(app)

conn = psycopg2.connect("dbname='crm' user='krayhaslem' host='localhost'")
cursor = conn.cursor()

org_id = -1


class AppUsers(db.Model):
   __tablename__= "users"
   user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
   first_name = db.Column(db.String(), nullable = False)
   last_name = db.Column(db.String(), nullable = False)
   email = db.Column(db.String(), nullable = False, unique = True)
   password = db.Column(db.String(), nullable = False)
   city = db.Column(db.String())
   state = db.Column(db.String())
   active = db.Column(db.Boolean(), nullable=False, default=False)
   # org_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Organizations.org_id'), nullable=False)
   created_date = db.Column(db.DateTime, default=datetime.utcnow)
   role = db.Column(db.String(), default='user', nullable=False)
   
   def __init__(self, first_name, last_name, email, password, city, state, role):
      self.first_name = first_name
      self.last_name = last_name
      self.email = email
      self.password = password
      self.city = city
      self.state = state
      self.active = True
      # self.org_id = org_id
      self.role = role
   
   
class AppUsersSchema(ma.Schema):
   class Meta:
      fields = ['user_id','first_name', 'last_name', 'email', 'password', 'phone', 'created_date', 'role', 'active']
   # organization = ma.fields.Nested(OrganizationsSchema(only=("name","active")))
    
user_schema = AppUsersSchema()
users_schema = AppUsersSchema(many=True)

def create_all():
   print("Querying for Super Admin user...")
   user_data = db.session.query(AppUsers).filter(AppUsers.email == 'admin@devpipeline.com').first()
   
   if user_data == None:
      print("Super Admin not found! Creating foundation-admin@devpipeline user...")
      
      password = ''
      while password == '' or password is None:
         password = input(' Enter a password for Super Admin:')
      # hashed_password = bcrypt.generate_password_hash(password).decode("utf8")

      record = AppUsers('Super', 'Admin', "admin@devpipeline.com", password, "Utah", "Orem", "super-admin")

      db.session.add(record)
      db.session.commit()
   
   else:
      print("Super Admin user found!")

@app.route('/user/add', methods=['POST'])
def add_user():
   form = request.form

   fields = ["first_name", "last_name", "email", "password", "city", "state", "role"]
   req_fields = ["first_name", "email"]
   values = []
   
   for field in fields:
      form_value = form.get(field)
      if form_value in req_fields and form_value == " ":
         return jsonify (f'{field} is required field'), 400

      values.append(form_value)
   
   first_name = form.get('first_name')
   last_name = form.get('last_name')
   email = form.get('email')
   password = form.get('password')
   city = form.get('city')
   state = form.get('state')
   role = form.get('role')

   new_user_record = AppUsers(first_name, last_name, email, password, city, state, role)

   db.session.add(new_user_record)
   db.session.commit()
   
   return jsonify('User Added'), 200

# update user's information
@app.route('/user/edit/<user_id>', methods=['PUT'])
def edit_user(user_id, first_name = None, last_name = None, email = None, password = None, city= None, state = None, active = None):
   user_record = db.session.query(AppUsers).filter(AppUsers.user_id == user_id).first()
   if not user_record:
      return ('User not found'), 404
   if request:
      form = request.form
      first_name = form.get('first_name')
      last_name = form.get('last_name')
      email = form.get('email')
      password = form.get('password')
      city = form.get('city')
      state = form.get('state')
      role = form.get('role')
      active = form.get('active')
   
   if first_name:
      user_record.first_name = first_name
   if last_name:
      user_record.last_name = last_name
   if email:
      user_record.email = email
   if password:
      user_record.password = password
   if city:
      user_record.city = city
   if state:
      user_record.state = state
   if role:
      user_record.role = role
   if active:
      user_record.active = active
   
   db.session.commit()

   return jsonify('User Updated'), 201

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
      if user_id not in id_list:
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
      if user_id not in id_list:
         return jsonify('Error: User not found.'),404
      else:
         cursor.execute("""
            SELECT 
               user_id, first_name, last_name, email, password, city, state, active, created_date, role
            FROM 
               Users 
            WHERE 
               user_id = %s
            """, (user_id,))

         user_list = cursor.fetchone()
         user_dict = {
         "user_id": user_list[0],
         "first_name": user_list[1],
         "last_name": user_list[2],
         "email": user_list[3],
         "password": user_list[4],
         "city": user_list[5],
         "state": user_list[6],
         "active": user_list[7],
         "created_date": user_list[8],
         "role": user_list[9]
         }
 
         return jsonify(user_dict), 200
   except:
      return jsonify('Error: Failed to get User.'), 400

@app.route('/user/list', methods=['GET'])
def get_users():
   list_users = []
   cursor.execute("""
            SELECT 
               user_id, first_name, last_name, email, password, city, state, active, created_date, role
            FROM 
               Users 
            """)

   org_list_tuples = cursor.fetchall()
   for user_list in org_list_tuples:
      user_dict = {
         "user_id": user_list[0],
         "first_name": user_list[1],
         "last_name": user_list[2],
         "email": user_list[3],
         "password": user_list[4],
         "city": user_list[5],
         "state": user_list[6],
         "active": user_list[7],
         "created_date": user_list[8],
         "role": user_list[9]
         }

      list_users.append(user_dict)

   return jsonify(list_users), 200



if __name__ == '__main__':
   create_all()
   app.run()
