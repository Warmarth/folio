import os
from flask import Flask
from app.database import db
from app.routes.routes import api
from app.routes.exercise_route import exercise

def create_app(config_name='development'):
    app = Flask(__name__,instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    
    
    db.init_app(app)
    
    app.register_blueprint(api,url_prefix='/api')
    app.register_blueprint(exercise,url_prefix='/api/exercises')
    
    with app.app_context():
        db.create_all()
    return app