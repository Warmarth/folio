from app.database import db
import uuid
import enum
from datetime import datetime,timezone


# ---------------------------------------------------------------------------
# Enums — using real enums instead of free-text strings prevents typos like
# "medum" silently breaking XP/level lookups, and lets Postgres index/query
# them efficiently.
# ---------------------------------------------------------------------------

class RoleEnum(str, enum.Enum):
    learner = "learner"
    mentor = "mentor"
    admin = "admin"


class LevelEnum(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
    expert = "expert"
    possible = "possible"


class ProgressStatusEnum(str, enum.Enum):
    picked = "picked"
    in_progress = "in_progress"
    submitted = "submitted"
    completed = "completed"


class SubmissionStatusEnum(str, enum.Enum):
    pending = "pending"       # queued, waiting for AI evaluation
    evaluating = "evaluating" # worker has picked it up
    completed = "completed"   # evaluation finished (passed or failed)
    failed = "failed"         # evaluator errored out (e.g. Groq call failed)


class MentorLearnerStatusEnum(str, enum.Enum):
    pending = "pending"
    active = "active"
    declined = "declined"
    ended = "ended"


class SuggestionStatusEnum(str, enum.Enum):
    suggested = "suggested"   # agent proposed it, gathering picks
    queued = "queued"         # pick_count hit the threshold (5), waiting on a mentor
    approved = "approved"     # mentor approved — a real Exercise now exists for it
    rejected = "rejected"     # mentor rejected it


# fixed threshold: once an ExerciseSuggestion reaches this many distinct
# learner picks, it flips to 'queued' and appears in the mentor approval
# queue. Kept as a constant here (not a DB column) so it can be bumped
# without a migration.
SUGGESTION_QUEUE_THRESHOLD = 5


class User(db.Model):

    __tablename__ = "user"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(200), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(RoleEnum), nullable=False, default=RoleEnum.learner)
    total_xp = db.Column(db.Integer, nullable=False, default=0)  # denormalized, updated on completion
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # relationships
    profile = db.relationship("Profile", back_populates="user", uselist=False)
    exercises_created = db.relationship("Exercise", back_populates="creator", lazy="dynamic")
    projects_created = db.relationship("Project", back_populates="creator", lazy="dynamic")
    submissions = db.relationship("Submit_Exercise", back_populates="user", lazy="dynamic")
    progress = db.relationship("ExerciseProgress", back_populates="user", lazy="dynamic")
    projects_picked = db.relationship("ProjectPick", back_populates="user", lazy="dynamic")
    project_submissions = db.relationship("ProjectSubmission", back_populates="user", lazy="dynamic")

    # mentor-side and learner-side of the MentorLearner relationship
    mentees = db.relationship(
        "MentorLearner",
        foreign_keys="MentorLearner.mentor_id",
        back_populates="mentor",
        lazy="dynamic",
    )
    mentors = db.relationship(
        "MentorLearner",
        foreign_keys="MentorLearner.learner_id",
        back_populates="learner",
        lazy="dynamic",
    )


class Profile(db.Model):
    """Single profile table for every user, regardless of role.

    Replaces the old ProfileCard/MentorCard split — role already lives on
    User, so there's no need for two near-identical tables. `expertise` is
    only meaningful for mentors and stays nullable for learners.
    """

    __tablename__ = "profile"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False, unique=True, index=True)
    name = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.String(500), nullable=True)
    expertise = db.Column(db.String(500), nullable=True)  # mentors only
    image_url = db.Column(db.String(500), nullable=True)  # points to S3/R2, not raw bytes
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="profile")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.user.email,
            "bio": self.bio,
            "expertise": self.expertise,
            "role": self.user.role.value,
            "total_xp": self.user.total_xp,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

# This model hold the data for the different exercise and some infomation about them
class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    level = db.Column(db.Enum(LevelEnum), nullable=False)
    xp_points = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.String(36), db.ForeignKey('user.id'), index=True)

    creator = db.relationship('User', back_populates='exercises_created')
    progress = db.relationship("ExerciseProgress", back_populates="exercise", lazy="dynamic")
    submissions = db.relationship("Submit_Exercise", back_populates="exercise", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "level": self.level.value,
            "xp_points": self.xp_points,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# tracks a user's interaction with an exercise (picked, in progress, etc.)
class ExerciseProgress(db.Model):
    """Tracks user's interaction with exercises (started, last accessed)"""

    __tablename__ = "exercise_progress"
    __table_args__ = (
        db.UniqueConstraint("exercise_id", "user_id", name="uq_exercise_progress_user"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exercise_id = db.Column(db.String(36), db.ForeignKey("exercises.id"), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False, index=True)
    status = db.Column(db.Enum(ProgressStatusEnum), nullable=False, default=ProgressStatusEnum.picked)
    accessed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="progress")
    exercise = db.relationship("Exercise", back_populates="progress")

    def to_dict(self):
        return {
            "id": self.id,
            "exercise_id": self.exercise_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "accessed_at": self.accessed_at.isoformat() if self.accessed_at else None,
        }


# This model holds the data for bigger-scope projects (capstone-style work),
# distinct from single exercises.
class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    level = db.Column(db.Enum(LevelEnum), nullable=False)
    xp_points = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.String(36), db.ForeignKey("user.id"), index=True)

    creator = db.relationship("User", back_populates="projects_created")
    picks = db.relationship("ProjectPick", back_populates="project", lazy="dynamic")
    submissions = db.relationship("ProjectSubmission", back_populates="project", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "level": self.level.value,
            "xp_points": self.xp_points,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# tracks which projects a user has picked, and their progress on it
class ProjectPick(db.Model):
    __tablename__ = "project_pick"
    __table_args__ = (
        db.UniqueConstraint("project_id", "user_id", name="uq_project_pick_user"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.id"), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False, index=True)
    status = db.Column(db.Enum(ProgressStatusEnum), nullable=False, default=ProgressStatusEnum.picked)
    picked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="projects_picked")
    project = db.relationship("Project", back_populates="picks")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "picked_at": self.picked_at.isoformat() if self.picked_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


# tracks a mentor <-> learner relationship. A learner can request multiple
# mentors; a mentor must accept before it becomes active. Subscription/plan
# limits (e.g. "max active mentors") plug in later on top of this table
# without changing its shape — enforce those in a service layer, not here.
class MentorLearner(db.Model):
    __tablename__ = "mentor_learner"
    __table_args__ = (
        db.Index("ix_mentor_learner_mentor_status", "mentor_id", "status"),
        db.Index("ix_mentor_learner_learner_status", "learner_id", "status"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mentor_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False, index=True)
    learner_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False, index=True)
    status = db.Column(db.Enum(MentorLearnerStatusEnum), nullable=False, default=MentorLearnerStatusEnum.pending)
    requested_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    responded_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)

    mentor = db.relationship("User", foreign_keys=[mentor_id], back_populates="mentees")
    learner = db.relationship("User", foreign_keys=[learner_id], back_populates="mentors")

    def to_dict(self):
        return {
            "id": self.id,
            "mentor_id": self.mentor_id,
            "mentor_name": self.mentor.profile.name if self.mentor and self.mentor.profile else None,
            "learner_id": self.learner_id,
            "learner_name": self.learner.profile.name if self.learner and self.learner.profile else None,
            "status": self.status.value,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }


# an agent-proposed exercise that doesn't exist as a real Exercise yet.
# Learners "pick" (upvote) it; once pick_count crosses SUGGESTION_QUEUE_THRESHOLD
# it queues for a mentor to approve or reject. Approval creates the actual
# Exercise row and links back via resulting_exercise_id.
class ExerciseSuggestion(db.Model):
    __tablename__ = "exercise_suggestion"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    level = db.Column(db.Enum(LevelEnum), nullable=False)
    pick_count = db.Column(db.Integer, nullable=False, default=0)  # denormalized, like User.total_xp
    status = db.Column(db.Enum(SuggestionStatusEnum), nullable=False, default=SuggestionStatusEnum.suggested)
    queued_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    resulting_exercise_id = db.Column(db.String(36), db.ForeignKey("exercises.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    reviewer = db.relationship("User", foreign_keys=[reviewed_by])
    resulting_exercise = db.relationship("Exercise", foreign_keys=[resulting_exercise_id])
    picks = db.relationship("ExerciseSuggestionPick", back_populates="suggestion", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "level": self.level.value,
            "pick_count": self.pick_count,
            "status": self.status.value,
            "queued_at": self.queued_at.isoformat() if self.queued_at else None,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "resulting_exercise_id": self.resulting_exercise_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# one row per learner who picked a suggestion. The unique constraint makes
# pick_count reflect distinct learners, not repeated clicks from one person.
class ExerciseSuggestionPick(db.Model):
    __tablename__ = "exercise_suggestion_pick"
    __table_args__ = (
        db.UniqueConstraint("suggestion_id", "user_id", name="uq_suggestion_pick_user"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    suggestion_id = db.Column(db.String(36), db.ForeignKey("exercise_suggestion.id"), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False, index=True)
    picked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    suggestion = db.relationship("ExerciseSuggestion", back_populates="picks")
    user = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "suggestion_id": self.suggestion_id,
            "user_id": self.user_id,
            "picked_at": self.picked_at.isoformat() if self.picked_at else None,
        }



class SubmissionTypeEnum(str, enum.Enum):
    text = "text"
    file = "file"


class FileTypeEnum(str, enum.Enum):
    pdf = "pdf"
    docx = "docx"


class ProjectSubmission(db.Model):
    """Tracks actual project submissions and grading — mirrors
    Submit_Exercise, but a project can be submitted as typed text OR an
    uploaded file (pdf/docx).

    `extracted_text` is always populated at submission time regardless of
    `submission_type`: for text submissions it's just a copy of
    `text_content`; for file submissions it's the text pulled out of the
    pdf/docx at upload time (so a corrupt/unreadable file is caught
    immediately, not later when the async worker picks it up). The
    evaluator always reads `extracted_text` — it never needs to branch on
    submission_type — and attaches the learner's credentials (name,
    user_id) plus the project's requirements before calling Groq.
    """

    __tablename__ = "project_submission"
    __table_args__ = (
        db.Index(
            "uq_project_submission_user_completed",
            "user_id", "project_id",
            unique=True,
            sqlite_where=db.text("is_completed = 1"),
            postgresql_where=db.text("is_completed = true"),
        ),
        db.CheckConstraint(
            "(submission_type = 'text' AND text_content IS NOT NULL) OR "
            "(submission_type = 'file' AND file_url IS NOT NULL)",
            name="ck_project_submission_content_matches_type",
        ),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.id"), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False, index=True)

    submission_type = db.Column(db.Enum(SubmissionTypeEnum), nullable=False)
    text_content = db.Column(db.Text, nullable=True)       # set when submission_type = text
    file_url = db.Column(db.String(500), nullable=True)    # S3/R2 URL, set when submission_type = file
    file_name = db.Column(db.String(255), nullable=True)   # original filename
    file_type = db.Column(db.Enum(FileTypeEnum), nullable=True)
    extracted_text = db.Column(db.Text, nullable=True)     # always populated — what the evaluator reads

    status = db.Column(db.Enum(SubmissionStatusEnum), nullable=False, default=SubmissionStatusEnum.pending)
    score = db.Column(db.Integer, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship("User", back_populates="project_submissions")
    project = db.relationship("Project", back_populates="submissions")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "user_name": (self.user.profile.name if self.user and self.user.profile else None),
            "project_title": self.project.title,
            "submission_type": self.submission_type.value,
            "text_content": self.text_content,
            "file_url": self.file_url,
            "file_name": self.file_name,
            "file_type": self.file_type.value if self.file_type else None,
            "status": self.status.value,
            "score": self.score,
            "feedback": self.feedback,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_completed": self.is_completed,
        }


class Submit_Exercise(db.Model):
    """Tracks actual submissions and grading.

    `status` drives the async evaluation flow: a submission is created as
    `pending`, a worker flips it to `evaluating` while it calls Groq, then
    `completed` or `failed`. `is_completed` stays as a fast boolean flag
    specifically meaning "passed", since that's what the unique constraint
    and XP awarding key off of.
    """

    __tablename__ = "submit_exercise"
    __table_args__ = (
        # a user can only have ONE passed submission per exercise — enforced
        # at the DB level so concurrent requests can't both sneak through
        # the app-level "already completed" check.
        db.Index(
            "uq_submit_exercise_user_completed",
            "user_id", "exercise_id",
            unique=True,
            sqlite_where=db.text("is_completed = 1"),
            postgresql_where=db.text("is_completed = true"),
        ),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False, index=True)
    exercise_id = db.Column(db.String(36), db.ForeignKey("exercises.id"), nullable=False, index=True)
    answer = db.Column(db.String(500), nullable=False)
    status = db.Column(db.Enum(SubmissionStatusEnum), nullable=False, default=SubmissionStatusEnum.pending)
    score = db.Column(db.Integer, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship("User", back_populates="submissions")
    exercise = db.relationship("Exercise", back_populates="submissions")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": (self.user.profile.name if self.user and self.user.profile else None),
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise.title,
            "answer": self.answer,
            "status": self.status.value,
            "score": self.score,
            "feedback": self.feedback,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "complete_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_completed": self.is_completed,
        }