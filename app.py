from flask import request, Flask, jsonify, Response
import marshmallow as ma
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import or_
import uuid
from datetime import datetime

app = Flask(__name__)

database_host = "127.0.0.1:5432"
database_name = "crm2"
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{database_host}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Organizations(db.Model):
   __tablename__= "organizations"
   org_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
   name = db.Column(db.String(), nullable = False)
   phone = db.Column(db.String(), nullable = False)
   city = db.Column(db.String(), nullable = False)
   state = db.Column(db.String())
   active = db.Column(db.Boolean(), nullable=False, default=False)
   users =  db.relationship('AppUsers', cascade="all,delete", backref = 'organization', lazy=True)

   def __init__(self, name, phone, city, state, active = True):
      self.name = name
      self.phone = phone
      self.city = city
      self.state = state
      self.active = active
   
class OrganizationsSchema(ma.Schema):
   class Meta:
      fields = ['org_id','name','phone','city','state','active']

organization_schema = OrganizationsSchema()
organizations_schema = OrganizationsSchema(many=True)


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
   org_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.org_id'), nullable=False)
   created_date = db.Column(db.DateTime, default=datetime.utcnow)
   role = db.Column(db.String(), default='user', nullable=False)
   
   def __init__(self, first_name, last_name, email, password, city, state, org_id, role):
      self.first_name = first_name
      self.last_name = last_name
      self.email = email
      self.password = password
      self.city = city
      self.state = state
      self.active = True
      self.org_id = org_id
      self.role = role
   
class AppUsersSchema(ma.Schema):
   class Meta:
      fields = ['user_id','first_name', 'last_name', 'email', 'city', 'state', 'active', 'org_id', 'created_date', 'role', 'organization']
   
   organization = ma.fields.Nested(OrganizationsSchema(only=("name","active")))
    
user_schema = AppUsersSchema()
users_schema = AppUsersSchema(many=True)

def create_all():
   db.create_all()
   
   print("Querying for DevPipeline organization...")
   org_data = db.session.query(Organizations).filter(Organizations.name == "DevPipeline").first()
   if org_data == None:
      print("DevPipeline organization not found. Creating DevPipeline Organization in database...")
      
      org_data = Organizations('DevPipeline', 'Orem', '3853090807', 'Utah')

      db.session.add(org_data)
      db.session.commit()
   else:
      print("DevPipeline Organization found!")

   print("Querying for Super Admin user...")
   
   user_data = db.session.query(AppUsers).filter(AppUsers.email == 'admin@devpipeline.com').first()
   
   if user_data == None:
      print("Super Admin not found! Creating foundation-admin@devpipeline user...")
      org_id = org_data.org_id
      password = ''
      while password == '' or password is None:
         password = input(' Enter a password for Super Admin:')

      record = AppUsers('Super', 'Admin', "admin@devpipeline.com", password, "Utah", "Orem", org_id, "super-admin")

      db.session.add(record)
      db.session.commit()
   
   else:
      print("Super Admin user found!")

@app.route('/organization/add', methods=['POST'])
def add_organization():

   form = request.form

   fields = ["name", "phone", "city", "state", "active"]
   req_fields = ["name"]
   values = []
   
   for field in fields:
      form_value = form.get(field)
      if form_value in req_fields and form_value == " ":
         return jsonify (f'{field} is required field'), 400

      values.append(form_value)
   
   name = form.get('name')
   phone = form.get('phone')
   city = form.get('city')
   state = form.get('state')
   
   new_organization = Organizations(name, phone, city, state)

   db.session.add(new_organization)
   db.session.commit()
   
   return jsonify('Organization Added'), 200

@app.route('/user/add', methods=['POST'])
def add_user():
   form = request.form

   fields = ["first_name", "last_name", "email", "password", "city", "state", "role", "org_id"]
   req_fields = ["first_name", "email", "org_id"]
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
   org_id = form.get('org_id')

   new_user_record = AppUsers(first_name, last_name, email, password, city, state, org_id, role)

   db.session.add(new_user_record)
   db.session.commit()
   
   return jsonify('User Added'), 200

@app.route('/organization/edit/<org_id>', methods=['PUT'])
def edit_organization(org_id, name = None, phone = None, city = None, state = None, active = None):
   organization_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
   if not organization_record:
      return ('Organization not found'), 404
   if request:
      form = request.form
      name = form.get('name')
      phone = form.get('phone')
      city = form.get('city')
      state = form.get('state')
      active = form.get('active')
   
   if name:
      organization_record.name = name
   if phone:
      organization_record.phone = phone
   if city:
      organization_record.city = city
   if state:
      organization_record.state = state
   if active:
      organization_record.active = active
   
   db.session.commit()

   return jsonify('Organization Updated'), 201

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

@app.route("/organization/delete/<org_id>", methods=["DELETE"])
def organization_delete_by_id(org_id):
    org_data = db.session.query(Organizations).filter(Organizations.org_id==org_id).first()
    
    if org_data:
        db.session.delete(org_data)
        db.session.commit()

        return jsonify(f'Organizations with org_id {org_id} deleted'), 201

    return jsonify(f'Organizations with org_id {org_id} not found'), 404

@app.route('/user/delete/<user_id>', methods=['DELETE'])
def delete_user(user_id):
   user_data = db.session.query(AppUsers).filter(AppUsers.user_id == user_id).first()
   if user_data:
        db.session.delete(user_data)
        db.session.commit()

        return jsonify(f'User with user_id {user_id} deleted'), 200

   else:
      return jsonify(f'User with user_id {user_id} not found'), 404

@app.route('/user/<user_id>', methods = ['GET'])
def get_user_by_id(user_id):
   user_record = db.session.query(AppUsers).filter(AppUsers.user_id==user_id).first()

   return jsonify(user_schema.dump(user_record)), 200

@app.route('/organizations/list', methods=['GET'])
def get_all_organizations():
   organization_records = db.session.query(Organizations).all()

   return jsonify(organizations_schema.dump(organization_records)), 200

@app.route('/user/list', methods=['GET'])
def get_all_users():
   user_records = db.session.query(AppUsers).all()

   return jsonify(users_schema.dump(user_records)), 200

@app.route('/user/activate/<user_id>', methods=['PUT'])
def activate_user(user_id):
   user_record = db.session.query(AppUsers).filter(AppUsers.user_id == user_id).first()

   if not user_record:
      return ('User not found'), 404
   
   user_record.active = True
   db.session.commit()

   return jsonify("User Activated"), 200

@app.route('/user/deactivate/<user_id>', methods=['PUT'])
def deactivate_user(user_id):
   user_record = db.session.query(AppUsers).filter(AppUsers.user_id == user_id).first()

   if not user_record:
      return ('User not found'), 404
   
   user_record.active = False
   db.session.commit()

   return jsonify("User Deactivated"), 200

@app.route('/organization/activate/<org_id>', methods=['PUT'])
def activate_organization(org_id):
   organization_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

   if not organization_record:
      return ('Organization not found'), 404
   
   organization_record.active = True
   db.session.commit()

   return jsonify("Organization Activated"), 200

@app.route('/organization/deactivate/<org_id>', methods=['PUT'])
def deactivate_organization(org_id):
   organization_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

   if not organization_record:
      return ('Organization not found'), 404
   
   organization_record.active = False
   db.session.commit()

   return jsonify("Organization Deactivated"), 200

@app.route('/search/<search_term>', methods=['GET'])
def get_records_by_search(search_term):
   user_results = []

   if search_term:
      search_term = search_term.lower()

      user_results = db.session.query(AppUsers) \
         .filter(db.or_( \
            db.func.lower(AppUsers.first_name).contains(search_term), \
            db.func.lower(AppUsers.last_name).contains(search_term),  \
            db.func.lower(AppUsers.city).contains(search_term))) \
         .all()

   else: 
      return jsonify('No search term'), 400

   return jsonify(users_schema.dump(user_results)), 200


if __name__ == '__main__':
   create_all()
   app.run()
