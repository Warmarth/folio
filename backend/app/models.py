from app.database import db
import base64
import uuid
from datetime import datetime,timezone


class ProfileCard(db.Model):
    __tablename__ = 'profile'
    
    id = db.Column(db.String(36),primary_key=True,default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200),nullable=False)
    email = db.Column(db.String(200),nullable=False,unique=True)
    bio = db.Column(db.String(500),nullable=True)
    image = db.Column(db.LargeBinary(500),nullable=True) 
    image_mini = db.Column(db.String(500),nullable=True) 
    created_at = db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))
    
    def to_dict(self):
        data = {
            "id":self.id,
            "name":self.name,
            "email":self.email,
            "bio":self.bio,
            "image":None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        if self.image:
            b64 = base64.b64encode(self.image).decode('utf-8')
            data["image"] = f"data:{self.image_mini}; base64,{b64}" if self.image_mini else b64
            
        return data


# This model hold the data for the different exercise and some infomation about them
class Exercise(db.Model):
    __tablename__ = 'exercises'
    
    id = db.Column(db.String(36),primary_key=True,default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200),nullable=False)
    description = db.Column(db.String(500),nullable=False)
    level = db.Column(db.String(10),nullable=False)
    xp_points = db.Column(db.Integer,nullable=False)
    created_at = db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))
    created_by = db.Column(db.String(36),db.ForeignKey('profile.id'))
    
    
    def to_dict(self):
        data = {
            "id":self.id,
            "title":self.title,
            "description":self.description,
            "level":self.level,
            "xp_points":self.xp_points,
            "created_by":self.created_by,
            "created_at":self.created_at.isoformat() if self.created_at else None
        }
        return data


#the table will keep track of the user and the exercises the are working on
class ExerciseProgress(db.Model):
    __tablename__ = "exercise_progress"

    id = db.Column(db.String(36),primary_key=True,default=lambda: str(uuid.uuid4()))
    exercise_id = db.Column(db.String(36),db.ForeignKey("exercises.id"),nullable=False)
    user_id = db.Column(db.String(36),db.ForeignKey("profile.id"),nullable=False)
    accessed_at = db.Column(db.DateTime,default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime,nullable=True)
    is_completed = db.Column(db.Boolean,default=False,nullable=False)
    
    def to_dict(self):
        data = {
            "id":self.id,
            "exercise_id": self.exercise_id,
            "user_id":self.user_id,
            'accessed_at':(self.accessed_at.isoformat() if self.accessed_at else None),
            "complete_at":(self.completed_isoformat() if self.completed_at else None),
            "is_completed":self.is_completed
            }
        
        return data