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
    grade = db.Column(db.Integer, nullable=False)

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


#getting teacher name
def get_teacher_name(teacher_id):
    teacher = Teachers.query.filter_by(teacherID=teacher_id).first()
    
    if not teacher:
        return jsonify({"message": "Teacher not found"}), 404
    
    return jsonify({"teacherID": teacher.teacherID, "teacherName": teacher.teacherName}), 200


#getting student name

@app.route('/student/<int:student_id>', methods=['GET'])
def get_student_name(student_id):
    student = Students.query.filter_by(studentID=student_id).first()
    
    if not student:
        return jsonify({"message": "Student not found"}), 404
    
    return jsonify({"studentID": student.studentID, "studentName": student.studentName}), 200




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

@app.route('/courses', methods=['GET'])
def get_all_courses():
    courses = Courses.query.all()
    course_list = [
        {
            "courseID": course.courseID,
            "courseName": course.courseName,
            "teacherID": course.teacherID,
            "courseTimes": course.courseTimes,
            "maxStudents": course.maxStudents,
            "currentStudents": course.currentStudents
        }
        for course in courses
    ]
    return jsonify(course_list), 200


@app.route('/student/<int:student_id>/courses', methods=['GET'])
def get_student_courses(student_id):
    # Query the Grades table to get all course IDs for the student
    student_courses = Grades.query.filter_by(studentID=student_id).all()
    
    # If the student is not enrolled in any courses, return an empty list
    if not student_courses:
        return jsonify({"message": f"No courses found for student with ID {student_id}"}), 404
    
    # Get course details for each course the student is enrolled in
    course_list = []
    for student_course in student_courses:
        course = Courses.query.filter_by(courseID=student_course.courseID).first()
        if course:
            teacher = Teachers.query.filter_by(teacherID=course.teacherID)
            course_list.append({
                "courseID": course.courseID,
                "courseName": course.courseName,
                "teacherID": course.teacherID,
                "teacherName": teacher.teacherName if teacher else "Unknown",
                "courseTimes": course.courseTimes,
                "maxStudents": course.maxStudents,
                "currentStudents": course.currentStudents
            })
    
    return jsonify(course_list), 200


#student enrollment
@app.route('/student/<int:student_id>/enroll', methods=['POST'])
def enroll_in_course(student_id):
    data = request.json
    course_id = data.get('courseID')
    
    if not course_id:
        return jsonify({"message": "Course ID is required to enroll"}), 400

    # Check if course exists and has space
    course = Courses.query.filter_by(courseID=course_id).first()
    if not course:
        return jsonify({"message": "Course not found"}), 404
    if course.currentStudents >= course.maxStudents:
        return jsonify({"message": "Course is full"}), 400
    
    # Check if student is already enrolled
    existing_enrollment = Grades.query.filter_by(studentID=student_id, courseID=course_id).first()
    if existing_enrollment:
        return jsonify({"message": "Student is already enrolled in this course"}), 400

    # Enroll student
    new_grade = Grades(studentID=student_id, courseID=course_id, grade=0)
    course.currentStudents += 1
    db.session.add(new_grade)
    db.session.commit()
    
    return jsonify({"message": "Enrollment successful"}), 201

#student unenrollment

@app.route('/student/<int:student_id>/unenroll', methods=['DELETE'])
def unenroll_from_course(student_id):
    data = request.json
    course_id = data.get('courseID')
    
    if not course_id:
        return jsonify({"message": "Course ID is required to unenroll"}), 400

    # Check if enrollment exists
    enrollment = Grades.query.filter_by(studentID=student_id, courseID=course_id).first()
    if not enrollment:
        return jsonify({"message": "Student is not enrolled in this course"}), 404

    # Unenroll student
    db.session.delete(enrollment)
    course = Courses.query.filter_by(courseID=course_id).first()
    if course:
        course.currentStudents -= 1
    db.session.commit()
    
    return jsonify({"message": "Unenrollment successful"}), 200


#teacher primary view

@app.route('/courses/<int:teacher_id>/courses', methods=['GET'])
def get_teacher_courses(teacher_id):

    teacher = Teachers.query.filter_by(teacherID=teacher_id).first()
    if not teacher:
        return jsonify({"message": "Teacher not found"}), 404

    teacher_courses = Courses.query.filter_by(teacherID=teacher_id).all()
    
    course_list = [
        {
            "courseID": course.courseID,
            "courseName": course.courseName,
            "teacherID": course.teacherID,
            "courseTimes": course.courseTimes,
            "maxStudents": course.maxStudents,
            "currentStudents": course.currentStudents
        }
        for course in teacher_courses
    ]
    
    return jsonify(course_list), 200
#teacher specific course view

@app.route('/grades/<int:course_id>/students', methods=['GET'])
def get_students_in_course(course_id):
    # Get all students and their grades in the course
    students_in_course = Grades.query.filter_by(courseID=course_id).all()
    
    student_list = []
    for enrollment in students_in_course:
        student = Students.query.filter_by(studentID=enrollment.studentID).first()
        student_list.append({
            "studentID": enrollment.studentID,
            "studentName": student.studentName if student else "Unknown",
            "courseID": enrollment.courseID,
            "grade": enrollment.grade
        })
        
    
    return jsonify(student_list), 200

@app.route('/grades/<int:course_id>/students/<int:student_id>', methods=['POST'])
def update_student_grade(course_id, student_id):
    
    data = request.json
    new_grade = data.get('grade')

    if new_grade is None:
        return jsonify({"message": "Grade is required"}), 400

    # Find enrollment and update grade
    enrollment = Grades.query.filter_by(courseID=course_id, studentID=student_id).first()
    if not enrollment:
        return jsonify({"message": "Student not found in this course"}), 404

    enrollment.grade = new_grade
    db.session.commit()
    
    return jsonify({"message": "Grade updated successfully"}), 200




if __name__ == '__main__':
    app.run(debug=True, port=5001)