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
