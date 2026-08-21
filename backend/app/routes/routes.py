from flask import request,jsonify,Blueprint
from app.database import db
import base64
from app.models import ProfileCard
from flask_jwt_extended import get_jwt_identity,jwt_required

api = Blueprint('api',__name__)


#=== create profile card ===
@api.route('/create_profile', methods=["POST"])
@jwt_required()
def create_profile_card():
    # Support both JSON and form-data
    access_token  = get_jwt_identity()
    
    if request.is_json:
        name = request.json.get('name', '').strip()
        # email = request.json.get('email', '').strip()
        bio = request.json.get('bio')
        image_b64 = request.json.get('image')  # base64 string
        image_bytes = base64.b64decode(image_b64) if image_b64 else None
        mimetype = request.json.get('image_mini')
    else:
        name = request.form.get('name', '').strip()
        # email = request.form.get('email', '').strip()
        bio = request.form.get('bio')
        file = request.files.get('image')
        image_bytes = file.read() if file else None
        mimetype = file.mimetype if file else request.form.get('image_mini')
    
    if not name:
        return jsonify({"error": "fields 'name' is required"}), 400
    
    # Prevent duplicates
    if ProfileCard.query.filter_by(user_id=access_token).first():
        return jsonify({"error": "email already registered"}), 409
    
    file = request.files.get('image')
    image_bytes = None
    mimetype = None
    
    if file and file.filename:
        # Size check (max 2 MB)
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        
        if size > 2 * 1024 * 1024:
            return jsonify({"error": "image too large (max 2MB)"}), 400
        
        if not file.mimetype.startswith('image/'):
            return jsonify({"error": "file must be an image"}), 400
        
        image_bytes = file.read()
        mimetype = file.mimetype
    
    card = ProfileCard(
        user_id = access_token,
        name=name,
        # email=email,
        bio=bio,
        image=image_bytes,
        image_mini=mimetype
    )
    
    db.session.add(card)
    db.session.commit()
    
    return jsonify({'data': card.to_dict()}), 201

#=== read one ===
@api.route('/profile',methods=['GET'])
@jwt_required()
def get_one():
    user_id = get_jwt_identity()
    profile = ProfileCard.query.filter_by(user_id=user_id).first_or_404(description="user is not found")
    return jsonify({"data": profile.to_dict()}), 200

#=== read all ===
@api.route('/all_profile',methods=["GET"])
def get_all_profile():
    page = request.args.get('page',1,type=int)
    per_page = request.args.get('per_page',10,type=int)
    
    per_page = min(per_page,50)
    
    pagination = ProfileCard.query.order_by(ProfileCard.created_at.desc()).paginate(page=page,per_page=per_page,error_out=False)
    return jsonify({
        "data":[profile.to_dict() for profile in pagination.items],
        "pagination":{
            "page":pagination.page,
            "per_page":pagination.per_page,
            "total":pagination.total,
            "pages":pagination.pages,
            "has_next":pagination.has_next,
            "has_prev":pagination.has_prev
        }
    }),200
    
    
#=== update profile ===
@api.route('/edit_profile', methods=['PATCH', 'PUT'])
@jwt_required()
def edit_profile():
    user_id = get_jwt_identity()
    profile = ProfileCard.query.filter_by(user_id=user_id).first()
    
    if not profile:
        return jsonify({"error": "profile not found"}), 404
    
    # Detect JSON vs form-data
    if request.is_json:
        body = request.get_json()
    else:
        body = request.form
    
    if not body:
        return jsonify({"error": "no data provided"}), 400
    
    updated = False
    
    # Update name 
    
    if 'name' in body:
        name = body.get('name', '').strip()
        if not name:
            return jsonify({"error": "name cannot be empty"}), 400
        profile.name = name
        updated = True
    
    
    # Update bio
    if 'bio' in body:
        profile.bio = body.get('bio')
        updated = True
    
    # JSON: base64 image string
    if request.is_json and 'image' in body and body['image']:
        try:
            b64 = body['image']
            if ',' in b64:  # strip data:image/png;base64, prefix if present
                b64 = b64.split(',')[1]
            profile.image = base64.b64decode(b64)
            profile.image_mini = body.get('image_mini', 'image/png')
            updated = True
        except Exception:
            return jsonify({"error": "invalid base64 image"}), 400
    
    # Form-data: file upload
    elif not request.is_json:
        file = request.files.get('image')
        if file and file.filename:
            file.seek(0, 2)
            size = file.tell()
            file.seek(0)
            if size > 2 * 1024 * 1024:
                return jsonify({"error": "image too large (max 2MB)"}), 400
            if not file.mimetype.startswith('image/'):
                return jsonify({"error": "file must be an image"}), 400
            profile.image = file.read()
            profile.image_mini = file.mimetype
            updated = True
    
    if updated:
        db.session.commit()
    
    return jsonify({
        "message": "profile updated" if updated else "no changes made",
        "data": profile.to_dict()
    }), 200


@api.route('/delete_user',methods=['DELETE'])
@jwt_required()
def delete_profile():
    user_id = get_jwt_identity()
    profile = ProfileCard.query.filter_by(user_id=user_id).first()
    
    if not profile:
        return jsonify({"message":"user Profile not found"}),404
    db.session.delete(profile)
    db.session.commit()
    
    return jsonify({
        "id":profile.id,
        "message":"User profile succsefully deleted.",
    }),201
    
    
    
@api.route('/', methods=['GET'])
def home():
    return jsonify({
        "message":"welcome to the de learner"  
    }),200
    
