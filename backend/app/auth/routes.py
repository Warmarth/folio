import bcrypt
from flask import request,jsonify,Blueprint
from app.database import db
from app.models import User
from flask_jwt_extended import create_access_token

auth = Blueprint("auth",__name__)

@auth.route("/register", methods=["POST"])
def register():
    user_data = request.get_json()

    if not user_data:
        return jsonify({
            "message": "request body is required"
        }), 400

    email = user_data.get("email")
    password = user_data.get("password")
    role = user_data.get("role")

    if not email or not password or not role:
        return jsonify({
            "message": "email, password and role are required"
        }), 400

    email = email.strip()

    if role not in ["learner", "mentor"]:
        return jsonify({
            "message": "Invalid role"
        }), 400

    already_exist = User.query.filter_by(email=email).first()

    if already_exist:
        return jsonify({
            "message": "user already exists"
        }), 409

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    user = User(
        email=email,
        password_hash=password_hash,
        role=role
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": f"{role} successfully created!"
    }), 201
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
    role = already_exist.role
    access_token = create_access_token(
        identity= already_exist.id
    )
    
    return jsonify({
        "message":"login successful !!",
        "access_token": access_token,
        "role": role
    }),200
    
    