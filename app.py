import json
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__, static_folder='canva2/build')
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
admin = Admin(app, name='Admin Page', template_mode='bootstrap3')

app.config['SECRET_KEY'] = '9/11'

class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    isTeacher = db.Column(db.Boolean)

class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    courseID = db.Column(db.Integer, nullable=False)
    courseName = db.Column(db.String(80), nullable=False)
    teacherID = db.Column(db.Integer, nullable=False)
    courseTimes = db.Column(db.String(80), nullable=False)
    maxStudents = db.Column(db.Integer, nullable=False)
    currentStudents = db.Column(db.Integer, nullable=False)

class Grades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studentID = db.Column(db.Integer, nullable=False)
    courseID = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.Integer, nullable=True)

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studentID = db.Column(db.Integer, nullable=False)
    studentName = db.Column(db.String(80), nullable=True)


class Teachers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacherID = db.Column(db.Integer, nullable=False)
    teacherName = db.Column(db.String(80), nullable=False)


with app.app_context():
    db.create_all()


admin.add_view(ModelView(Login, db.session))
admin.add_view(ModelView(Courses, db.session))
admin.add_view(ModelView(Grades, db.session))
admin.add_view(ModelView(Students, db.session))
admin.add_view(ModelView(Teachers, db.session))


# @app.route('/')
# def home():
#     return "<h1>Welcome to the Admin Interface</h1><p>Go to <a href='/admin'>Admin Page</a> to manage the database.</p>"

# Serve the React app's index.html
@app.route('/')
def serve_react_app():
    return send_from_directory(app.static_folder, 'index.html')

# Serve other static files (JS, CSS, etc.)
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/student/add', methods=['POST'])
def add_student():
    data = request.json
    student_name = data.get('studentName')

    if not student_name:
        return jsonify({"message": "Student name is required"}), 400

    # Get the current maximum studentID and add 1 to it
    max_student = db.session.query(db.func.max(Students.studentID)).scalar()
    new_student_id = (max_student or 0) + 1

    # Create a new student
    new_student = Students(studentID=new_student_id, studentName=student_name)
    db.session.add(new_student)
    db.session.commit()
    
    return jsonify({"message": f"Student {student_name} added with ID {new_student_id}"}), 201

@app.route('/api/courses', methods=['GET'])
def get_all_courses():
    courses = Courses.query.all()
    course_list = [
        {
            "courseID": course.courseID,
            "courseName": course.courseName,
            "teacherName": Teachers.query.filter_by(teacherID=course.teacherID).first().teacherName,
            "courseTimes": course.courseTimes,
            "maxStudents": course.maxStudents,
            "currentStudents": course.currentStudents
        }
        for course in courses
    ]
    return jsonify(course_list), 200


@app.route('/api/student/<int:student_id>/courses', methods=['GET'])
def get_student_courses(student_id):
    # Query the Grades table to get all course IDs for the student
    student_courses = Grades.query.filter_by(studentID=student_id).all()
    
    # If the student is not enrolled in any courses, return an empty list
    if not student_courses:
        return jsonify([]), 200
    
    # Get course details for each course the student is enrolled in
    course_list = []
    for student_course in student_courses:
        course = Courses.query.filter_by(courseID=student_course.courseID).first()
        if course:
            course_list.append({
                "courseID": course.courseID,
                "courseName": course.courseName,
                "teacherName":  Teachers.query.filter_by(teacherID=course.teacherID).first().teacherName,
                "courseTimes": course.courseTimes,
                "maxStudents": course.maxStudents,
                "currentStudents": course.currentStudents
            })
    
    return jsonify(course_list), 200



@app.route('/api/student/<int:student_id>', methods=['GET'])
def getStudentName(student_id):
    studentName = Students.query.filter_by(studentID=student_id).first().studentName

    return jsonify({"studentName": studentName})
    

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('userID')
    password = data.get('password')
    #is_teacher = data.get('isTeacher')

    # Check if a user with the given userID and isTeacher status exists
    user = Login.query.filter_by(userID=user_id).first() #removed , isTeacher=is_teacher
    is_teacher = user.isTeacher

    # Validate password if user is found
    if user and user.password == password:
        return jsonify({"success": True, "userID": user_id, "isTeacher": is_teacher })
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401



@app.route('/api/student/<int:student_id>/courses/add', methods=['POST'])
def add_course(student_id):
    data = request.json
    course_id = data.get('courseID')

    # Check if the course exists
    course = Courses.query.filter_by(courseID=course_id).first()
    if not course:
        return jsonify({"message": "Course not found"}), 404

    # Check if the course is full
    if course.currentStudents >= course.maxStudents:
        return jsonify({"message": "Course is full"}), 400

    # Check if the student is already enrolled
    enrollment = Grades.query.filter_by(studentID=student_id, courseID=course_id).first()
    if enrollment:
        return jsonify({"message": "Student already enrolled"}), 400

    # Add student to the course
    new_enrollment = Grades(studentID=student_id, courseID=course_id, grade=0)  # Default grade is set to 0
    db.session.add(new_enrollment)
    
    # Update the current student count in the course
    course.currentStudents = Grades.query.filter_by(courseID=course_id).count()
    db.session.commit()

    return jsonify({"message": "Course added successfully", "updatedCourse": {
        "courseID": course.courseID,
        "courseName": course.courseName,
        "teacherID": course.teacherID,
        "courseTimes": course.courseTimes,
        "maxStudents": course.maxStudents,
        "currentStudents": course.currentStudents
    }}), 201



@app.route('/api/student/<int:student_id>/courses/drop', methods=['POST'])
def drop_course(student_id):
    data = request.json
    course_id = data.get('courseID')

    # Find the enrollment to remove
    enrollment = Grades.query.filter_by(studentID=student_id, courseID=course_id).first()
    if not enrollment:
        return jsonify({"message": "Enrollment not found"}), 404

    # Remove the student from the course
    db.session.delete(enrollment)
    
    # Update the current student count in the course
    course = Courses.query.filter_by(courseID=course_id).first()
    if course:
        course.currentStudents = max(0, course.currentStudents - 1)
    db.session.commit()

    return jsonify({"message": "Course dropped successfully", "updatedCourse": {
        "courseID": course.courseID,
        "courseName": course.courseName,
        "teacherID": course.teacherID,
        "courseTimes": course.courseTimes,
        "maxStudents": course.maxStudents,
        "currentStudents": course.currentStudents
    }}), 200


#teacher
@app.route('/api/teacher/<int:teacher_id>/courses', methods=['GET'])
def get_teacher_courses(teacher_id):
    courses = Courses.query.filter_by(teacherID=teacher_id).all()
    course_list = [
        {
            "courseID": course.courseID,
            "courseName": course.courseName,
            "teacherName": Teachers.query.filter_by(teacherID=course.teacherID).first().teacherName,
            "courseTimes": course.courseTimes,
            "maxStudents": course.maxStudents,
            "currentStudents": course.currentStudents
        }
        for course in courses
    ]
    return jsonify(course_list), 200


#get students in courses
@app.route('/api/course/<int:course_id>/students', methods=['GET'])
def get_course_students(course_id):
    enrollments = Grades.query.filter_by(courseID=course_id).all()
    student_list = [
        {
            "studentID": enrollment.studentID,
            "studentName": Students.query.filter_by(studentID=enrollment.studentID).first().studentName,
            "grade": enrollment.grade
        }
        for enrollment in enrollments
    ]
    return jsonify(student_list), 200


#Update student grade
@app.route('/api/course/<int:course_id>/student/<int:student_id>/grade', methods=['POST'])
def update_student_grade(course_id, student_id):
    data = request.json
    new_grade = data.get('grade')

    enrollment = Grades.query.filter_by(courseID=course_id, studentID=student_id).first()
    if not enrollment:
        return jsonify({"message": "Enrollment not found"}), 404

    enrollment.grade = new_grade
    db.session.commit()
    
    return jsonify({"message": "Grade updated successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=3000)