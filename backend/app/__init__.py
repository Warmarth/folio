import os
from flask import Flask
from app.database import db
from app.routes.routes import api
from app.auth.routes import auth
from app.routes.exercise_route import exercise
from app.routes.submitted import submitted
from flask_jwt_extended import JWTManager
from flask_cors import CORS

def create_app(config_name='development'):
    app = Flask(__name__,instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] =  os.getenv('JWT_SECRET_KEY')
    
    jwt = JWTManager(app)
    
    CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:3000",
                "http://127.0.0.1:3000"
            ]
            
        }
    },
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)

    
    db.init_app(app)
    app.register_blueprint(auth,url_prefix='/auth')
    app.register_blueprint(api,url_prefix='/api')
    app.register_blueprint(exercise,url_prefix='/api/exercises')
    app.register_blueprint(submitted,url_prefix='/api/submit')
    
    with app.app_context():
        db.create_all()
    return app