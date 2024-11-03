import json
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
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


@app.route('/')
def home():
    return "<h1>Welcome to the Admin Interface</h1><p>Go to <a href='/admin'>Admin Page</a> to manage the database.</p>"


if __name__ == '__main__':
    app.run(debug=True)