# server/models/course.py
from server.models import db, SerializerMixin

class Course(db.Model, SerializerMixin):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    credits = db.Column(db.Integer, nullable=False, default=3)

    def __repr__(self):
        return f"<Course id={self.id} name={self.name!r}>"
