1. Create and enter the directory
```bash
mkdir course_api_flask
cd courses_api_flask
```
2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```
3. Install flask and its dependencies
```bash
pip install flask flask_sqlalchemy flask_migrate
```
4. Freeze rquirements
```bash
pip freeze > requirements.txt
```
5. Make the necessary directories
```bash
mkdir server
mkdir server/models server/routes
touch server/__init__.py server/app.py server/models/__init__.py server/routes/__init__.py
touch server/models/course.py server/routes/course_routes.py
```
6. Fill in the above files with initial data:
`server/app.py` :
```python
# server/app.py
from flask import Flask
from flask_migrate import Migrate
from server.models import db  # <-- FIXED IMPORT

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    Migrate(app, db)

    @app.route("/")
    def home():
        return {"message": "Flask is working!"}

    return app
```
Then on `server/models/__init__.py`
```python
# server/models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

7. Re-export the FLASK_APP variable
```bash
export FLASK_APP=server.app:create_app
```

8. Now try running flask
```bash
flask run
```

9. Initialize Flask-Migrate

Once Flask runs without errors, stop the server (CTRL+C) and run:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade head
```

10. We now add SerializerMixin and Course model

Edit `server/models/__init__.py` to include a simple serializer mixin and to make sure Course will be imported later:

```python
# server/models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SerializerMixin:
    """Converts model instances to dictionary for easy JSON serialization."""
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Import Course model so Flask-Migrate can detect it
from server.models.course import Course  
```
Now edit `server/models/course.py` to define the model:
```python
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
```
11. We now Generate and Apply Migration

```bash
flask db migrate -m "Create courses table"
flask db upgrade
```
You should now have a courses table in app.db

12. Now lets create RESTful Routes
Edit `server/routes/course_routes.py`:

```python
# server/routes/course_routes.py
from flask import Blueprint, jsonify, request
from server.models import db
from server.models.course import Course
from sqlalchemy.exc import IntegrityError

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")

# GET /courses → return all courses
@courses_bp.route("/", methods=["GET"])
def get_courses():
    courses = Course.query.all()
    return jsonify([c.to_dict() for c in courses]), 200

# GET /courses/<id> → return one course
@courses_bp.route("/<int:id>", methods=["GET"])
def get_course(id):
    course = Course.query.get_or_404(id)
    return jsonify(course.to_dict()), 200

# POST /courses → create a new course
@courses_bp.route("/", methods=["POST"])
def create_course():
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400

    course = Course(
        name=name,
        description=data.get("description"),
        credits=data.get("credits", 3)
    )

    db.session.add(course)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "course with that name already exists"}), 409

    return jsonify(course.to_dict()), 201

# PUT /courses/<id> → update a course
@courses_bp.route("/<int:id>", methods=["PUT"])
def update_course(id):
    data = request.get_json() or {}
    course = Course.query.get_or_404(id)

    if "name" in data:
        course.name = data["name"]
    if "description" in data:
        course.description = data["description"]
    if "credits" in data:
        try:
            course.credits = int(data["credits"])
        except (TypeError, ValueError):
            return jsonify({"error": "credits must be an integer"}), 400

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "course with that name already exists"}), 409

    return jsonify(course.to_dict()), 200

# DELETE /courses/<id> → delete a course
@courses_bp.route("/<int:id>", methods=["DELETE"])
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "course deleted"}), 200
```

13. We register Blueprint
edit `server/app.py` to register the `courses_bp`
```python
# server/app.py
from flask import Flask
from flask_migrate import Migrate
from server.models import db
from server.routes.course_routes import courses_bp  # <-- import blueprint

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    Migrate(app, db)

    app.register_blueprint(courses_bp)  # <-- register blueprint

    @app.route("/")
    def home():
        return {"message": "Flask is working!"}

    return app
```

14. We can no run the app
```bash
flask run
```

15. TEsting the endpoints
we will use `curl` open a new terminal tab:
`CREATE` To add a course use`POST`:
```bash
curl -X POST http://127.0.0.1:5000/courses/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Python I","description":"Intro to python","credits":3}'
```
`READ` To get one course based on our routes design its
```bash
curl http://127.0.0.1:5000/courses/1
```

`UPDATE` To update a course:
```bash
curl -X PUT http://127.0.0.1:5000/courses/1 \
  -H "Content-Type: application/json" \
  -d '{"credits":5}'
```
`DELETE` To delete a course
```bash
curl -X DELETE http://127.0.0.1:5000/courses/1
```