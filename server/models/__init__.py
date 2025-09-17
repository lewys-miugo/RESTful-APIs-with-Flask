# server/models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SerializerMixin:
    """Converts model instances to dictionary for easy JSON serialization."""
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# We import Course model so Flask-Migrate can detect it
from server.models.course import Course  
