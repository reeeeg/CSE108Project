import json
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Login(db.Model):
    studentIDteacherID = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(80), nullable=False)
    isTeacher = db.Column(db.Boolean)

class Courses(db.Model):
    courseID = db.Column(db.Integer, primary_key=True)
    courseName = db.Column(db.String(80), nullable=False)
    teacherID = db.Column(db.Integer, nullable=False)
    daysTime = db.Column(db.String(80), nullable=False)
    maxStudents = db.Column(db.Integer, nullable=False)
    currentStudents = db.Column(db.Integer, nullable=False)

class Grades(db.Model):
    studentID = db.Column(db.Integer, primary_key=True)
    courseID = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.Integer, nullable=False)

class Students(db.Model):
    studentID = db.Column(db.Integer, primary_key=True)
    studentName = db.Column(db.String(80), nullable=True)
    courseID = db.Column(db.Integer, nullable=False)


class Teachers(db.Model):
    teacherID = db.Column(db.Integer, primary_key=True)
    teacherName = db.Column(db.String(80), nullable=False)
    courseID = db.Column(db.Integer, nullable=False)


with app.app_context():
    db.create_all()


