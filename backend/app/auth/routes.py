import bcrypt
from flask import request,jsonify,Blueprint
from app.database import db
from app.models import User
from flask_jwt_extended import create_access_token

auth = Blueprint("auth",__name__)

@auth.route("/register",methods=['POST'])
def register():
    user_data = request.get_json()
    
    if not user_data:
        return jsonify({
            "message":'request body is required'
        })
    
    email = user_data.get('email')
    password = user_data.get('password')
    
    if not email or not password:
        return jsonify({
            "message":"email and password are required"
        }),400
    
    email = email.strip()
    
    already_exist = User.query.filter_by(email=email).first()
    
    if already_exist:
        return jsonify({
            "message":"user already exist"
        }),409
    
    password_hash = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
    
    data = User(
        email = email,
        password_hash = password_hash
    )
    
    db.session.add(data)
    db.session.commit()
    
    return jsonify({
        "message": "user successfully created !!"
    })
    
    

@auth.route("/login",methods=['POST'])
def login():
    user_data = request.get_json()
    
    if not user_data:
        return jsonify({
            "message":"email and password required"
        }),400
    
    email = user_data.get('email')
    password = user_data.get('password')
    
    if not email or not password:
        return jsonify({
            "message":"email and password are required"
        }),400
        
    email = email.strip()
            
    already_exist = User.query.filter_by(email=email).first()
    
    if not already_exist:
        return jsonify({
            "message": "invalid email or password"
        }),401
        
    valid_password = bcrypt.checkpw(password.encode('utf-8'),already_exist.password_hash.encode('utf-8'))
    
    if not valid_password:
        return jsonify({
            "message": "invalid email or password"
        }),401
    
    access_token = create_access_token(
        identity= already_exist.id
    )
    
    return jsonify({
        "message":"login successful !!",
        "access_token": access_token
    }),200
    
    