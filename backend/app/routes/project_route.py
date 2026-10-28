from flask import request,jsonify,Blueprint
from app.database import db
from app.models import Exercise,ProfileCard
from flask_jwt_extended import jwt_required,get_jwt_identity
