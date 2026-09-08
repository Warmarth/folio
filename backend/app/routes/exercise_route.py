from flask import request,jsonify,Blueprint
from app.database import db
from app.models import Exercise,ProfileCard,MentorCard
from flask_jwt_extended import jwt_required,get_jwt_identity

#creating the skeleton name for the exercise api
exercise = Blueprint('exercises',__name__)

@exercise.route('/create_exercise',methods=['POST'])
@jwt_required()
def create_exercise():
    levels = ("easy","medium","hard","expert","possible")
    xp_map = {
    "easy": 2,
    "medium": 3,
    "hard": 5,
    "expert": 7,
    "possible": 9
    }
    
    user_id = get_jwt_identity()
    profile = MentorCard.query.filter_by(user_id=user_id).first()
    
    if not profile:
        return jsonify({
            "message": "you must have a profile to create an exercise"
        }), 403
        
    if not request.is_json:
        return jsonify({
            "message": "Request must contain JSON data"
        }),400
    
    
    data = request.get_json()
    
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    level = data.get("level", "").strip()
    
    if not title or not description or not level:
        return jsonify({
            "message": "title, description and  level are required"
        }), 400
    
    if level not in levels:
        return jsonify({
            "message":"level not  found"
        }),400
    
    xp_points = xp_map[level]
    
    exe_card  = Exercise(
        title = title,
        description = description,
        level = level,
        xp_points = xp_points,
        created_by = user_id
    )
    db.session.add(exe_card)
    db.session.commit()
    
    return jsonify({
        "message": "Exercise created successfully",
        "exercise": exe_card.to_dict()
    }), 201


@exercise.route('/all_exercise',methods=['GET'])
@jwt_required()
def get_all_exercises():
    page = request.args.get('page',1,type=int)
    per_page = request.args.get('per_page',10,type=int) 
    per_page = min(per_page,50)
    
    pagination = Exercise.query.order_by(Exercise.created_at.desc()).paginate(page=page,per_page=per_page,error_out=False)
    
    return {
        "data":[exercise.to_dict() for exercise in pagination.items],
        "pagination":{
            "page":pagination.page,
            "per_page":pagination.per_page,
            "total":pagination.total,
            "pages":pagination.pages,
            "has_next":pagination.has_next,
            "has_prev":pagination.has_prev
        }
    }
    
@exercise.route('/all_exercise/<string:id>')
@jwt_required()
def get_one_exercise(id):
    
    current_exe = Exercise.query.get_or_404(id)
    return jsonify({
        "data": current_exe.to_dict()
    }),200

@exercise.route('/all_exercise/<string:exercise_id>/update',methods=['PUT','PATCH'])
@jwt_required()
def update_exercise(exercise_id):
    
    user_id = get_jwt_identity()
    
    current_exe = Exercise.query.get_or_404(exercise_id)
    
    if current_exe.created_by != user_id:
        return jsonify({
            "messege":"invalid action"
        }),403
    
    if not request.is_json:
        return jsonify({'message':'update must be of json type'}),400
    
    xp_map = {
        "easy": 2,
        "medium": 3,
        "hard": 5,
        "expert": 7,
        "possible": 9
        }    
    
    body = request.get_json()
    
    updated = False
    
    title = body.get('title','').strip()
    description = body.get('description','').strip()
    level = body.get('level','').strip()
    
    if "title" in body and title:
        current_exe.title = title 
        updated = True
        
    if "description" in body and description:
        current_exe.description =  description
        updated = True
        
    if "level" in body :
        if level not in xp_map:
            return jsonify({
            "message": "Invalid level"
        }), 400
        current_exe.level =  level
        current_exe.xp_points = xp_map[level]
        updated = True
    
    if updated:
        db.session.commit()

    
    return jsonify({
            "message": "exercise updated" if updated else "no changes made",
            "data": current_exe.to_dict()
        }), 200
    

@exercise.route('/all_exercise/<string:exercise_id>/delete',methods=['DELETE'])
@jwt_required()
def delete_exercise(exercise_id):
    user_id = get_jwt_identity()
    exercise = Exercise.query.get_or_404(exercise_id)
    
    if exercise.created_by != user_id:
        return jsonify({
            "message":"invalid action,you are not the author of this exercise "
        }),403
        
    exercise_title = exercise.title
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({
        "message":f"succsefully deleted {exercise_title}"
    }),204