import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TeacherDashboard.css';

function TeacherDashboard({ teacherID, onLogout }) {
    const [courses, setCourses] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [students, setStudents] = useState([]);
    const [error, setError] = useState(null);

    let [teacherName, setTeacherName] = useState('Instructor');


    // Fetch courses taught by the teacher
    useEffect(() => {
        axios.get(`/api/teacher/${teacherID}/courses`)
            .then(response => setCourses(response.data))
            .catch(() => setError('Error fetching your courses. Please try again.'));
    }, [teacherID]);

    useEffect(() => {
        if (courses.length > 0) {
            setTeacherName(courses[0].teacherName);
        }
    }, [courses]);

    // Fetch students for the selected course
    const fetchStudents = (courseID) => {
        axios.get(`/api/course/${courseID}/students`)
            .then(response => {
                setStudents(response.data);
                setSelectedCourse(courseID);
            })
            .catch(() => setError('Error fetching students. Please try again.'));
    };

    // Grade update
    const handleGradeChange = (studentID, newGrade) => {
        axios.post(`/api/course/${selectedCourse}/student/${studentID}/grade`, { grade: newGrade })
            .then(() => {
                setStudents(prevStudents =>
                    prevStudents.map(student =>
                        student.studentID === studentID ? { ...student, grade: newGrade } : student
                    )
                );
                setError(null);
            })
            .catch(() => setError('Error updating grade. Please try again.'));
    };


    // Course list
    const renderCourseList = () => (
        <div className="course-list">
            <h2>Your Courses</h2>
            <table className="course-table">
                <thead>
                    <tr>
                        <th>Course Name</th>
                        <th>Teacher</th>
                        <th>Time</th>
                        <th>Students Enrolled</th>
                    </tr>
                </thead>
                <tbody>
                    {courses.map(course => (
                        <tr key={course.courseID}>
                            <td>
                                <button className="course-link" onClick={() => fetchStudents(course.courseID)}>
                                    {course.courseName}
                                </button>
                            </td>
                            <td>{course.teacherName}</td>
                            <td>{course.courseTimes}</td>
                            <td>{course.currentStudents}/{course.maxStudents}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );

    // Student list for the selected course
    const renderStudentList = () => (
        <div className="student-list">
            <button className="back-button" onClick={() => setSelectedCourse(null)}>&larr; Back</button>
            <h2>Course: {courses.find(course => course.courseID === selectedCourse)?.courseName}</h2>
            <table className="student-table">
                <thead>
                    <tr>
                        <th>Student Name</th>
                        <th>Grade</th>
                    </tr>
                </thead>
                <tbody>
                    {students.map(student => (
                        <tr key={student.studentID}>
                            <td>{student.studentName}</td>
                            <td>
                                <input
                                    type="number"
                                    value={student.grade}
                                    onChange={(e) => handleGradeChange(student.studentID, parseInt(e.target.value))}
                                    className="grade-input"
                                />
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );

    return (
        <div className="dashboard">
            <div className="header">
                <h2>Welcome, {teacherName}!</h2>
                <button onClick={() => {console.log("Sign out button clicked"); onLogout();}} className="logout-link">Sign out</button>
            </div>
            <h1>UC Merced</h1>
            {error && <p className="error">{error}</p>}
            {selectedCourse ? renderStudentList() : renderCourseList()}
        </div>
    );
}

export default TeacherDashboard;
