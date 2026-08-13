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