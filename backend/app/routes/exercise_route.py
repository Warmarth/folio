from flask import request,jsonify,Blueprint
from app.database import db
from app.models import Exercise,ProfileCard

#creating the skeleton name for the exercise api
exercise = Blueprint('exercises',__name__)

@exercise.route('/<string:id>/create_exercise',methods=['POST'])
def create_exercise(id):
    profile_id = ProfileCard.query.get_or_404(id,description="profile found")
    
    if not request.is_json:
        return jsonify({
            "message": "Request must contain JSON data"
        }),400
    
    data = request.get_json()
    
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    level = data.get("level", "").strip()
    xp_points = data.get("xp_points")
    
    if not title or not description or not level or xp_points is None:
        return jsonify({
            "message": "title, description, level and xp_points are required"
        }), 400
    
    try:
        xp_points = int(xp_points)
    except (TypeError,ValueError):
        return jsonify({
            "message": "xp_points must be an integer"
        }),400
    
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