from flask import request,jsonify,Blueprint
from app.database import db
from app.models import Exercise,ProfileCard

#creating the skeleton name for the exercise api
exercise = Blueprint('exercises',__name__)

@exercise.route('/<string:id>/create_exercise',methods=['POST'])
def create_exercise(id):
    levels = ("easy","medium","hard","expert","possible")
    xp_map = {
    "easy": 2,
    "medium": 3,
    "hard": 5,
    "expert": 7,
    "possible": 9
    }    
    profile_id = ProfileCard.query.get_or_404(id)
    
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
        created_by = profile_id.id
    )
    db.session.add(exe_card)
    db.session.commit()
    
    return jsonify({
        "message": "Exercise created successfully",
        "exercise": exe_card.to_dict()
    }), 201


#=== 
@exercise.route('/all_exercise',methods=['GET'])
def get_all_exercises():
    page = request.args.get('page',type=int)
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
def get_one_exercise(id):
    
    current_exe = Exercise.query.get_or_404(id)
    return jsonify({
        "data": current_exe.to_dict()
    }),201

@exercise.route('/<string:profile_id>/all_exercise/<string:exercise_id>/update',methods=['PUT','PATCH'])
def update_exercise(profile_id,exercise_id):
    
    current_exe = Exercise.query.get_or_404(exercise_id)
    
    if profile_id != current_exe.created_by:
        return jsonify({
            "messege":"invalid action"
        }),400
    
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
    

@exercise.route('/<string:profile_id>/all_exercise/<string:exercise_id>/delete',methods=['DELETE'])
def delete_exercise(profile_id,exercise_id):
    
    exercise = Exercise.query.get_or_404(exercise_id)
    profile = ProfileCard.query.get_or_404(profile_id)
    if exercise.created_by != profile.id:
        return jsonify({
            "message":"invalid action,you are not the author of this exercise "
        }),400
        
    exercise_title = exercise.title
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({
        "message":f"succsefully deleted {exercise_title}"
    }),200