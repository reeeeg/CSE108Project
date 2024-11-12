import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './StudentDashboard.css';

function StudentDashboard({ studentID, onLogout }) {
    const [myCourses, setMyCourses] = useState([]);
    const [availableCourses, setAvailableCourses] = useState([]);
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [tab, setTab] = useState('yourCourses');

    useEffect(() => {
        if (isLoading) {
            // fetch student's courses
            axios.get(`/api/student/${studentID}/courses`)
                .then(response => {
                    setMyCourses(response.data);
                    setError(null);
                })
                .catch(() => setError('Error fetching your courses. Please try again.'));

            // fetch all available courses
            axios.get('/api/courses')
                .then(response => {
                    setAvailableCourses(response.data);
                    setError(null);
                })
                .catch(() => setError('Error fetching available courses. Please try again.'))
                .finally(() => {
                    setIsLoading(false);
                });
        }
    }, [studentID, isLoading]);

    useEffect(() => {
        if (availableCourses.length > 0 && myCourses.length > 0) {
            // filter out courses that the student is already enrolled in
            const enrolledCourseIDs = new Set(myCourses.map(course => course.courseID));
            const filteredAvailableCourses = availableCourses.filter(course => !enrolledCourseIDs.has(course.courseID));
            setAvailableCourses(filteredAvailableCourses);
        }
    }, [myCourses, availableCourses]);

    const handleAddCourse = (courseID) => {
        axios.post(`/api/student/${studentID}/courses/add`, { courseID })
            .then((response) => {
                const updatedCourse = response.data.updatedCourse;
                setMyCourses(prev => [...prev, updatedCourse]);
                setAvailableCourses(prev => prev.filter(course => course.courseID !== courseID));
                setError(null);
            })
            .catch(() => setError('Error adding course. Please try again.'));
    };

    const handleDropCourse = (courseID) => {
        axios.post(`/api/student/${studentID}/courses/drop`, { courseID })
            .then((response) => {
                const updatedCourse = response.data.updatedCourse;
                setAvailableCourses(prev => [...prev, updatedCourse]);
                setMyCourses(prev => prev.filter(course => course.courseID !== courseID));
                setError(null);
            })
            .catch(() => setError('Error dropping course. Please try again.'));
    };

    const renderCourseList = () => (
        <div className="course-container">
            <table className="course-table">
                <thead>
                    <tr>
                        <th>Course Name</th>
                        <th>Teacher</th>
                        <th>Time</th>
                        <th>Students Enrolled</th>
                        <th>Add/Drop</th>
                    </tr>
                </thead>
                <tbody>
                    {myCourses.map(course => (
                        <tr key={course.courseID}>
                            <td>{course.courseName}</td>
                            <td>{course.teacherName}</td>
                            <td>{course.courseTimes}</td>
                            <td>{course.currentStudents}/{course.maxStudents}</td>
                            <td>
                                <button onClick={() => handleDropCourse(course.courseID)} className="drop-button">-</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );

    const renderAddCoursesList = () => (
        <div className="course-container">
            <table className="course-table">
                <thead>
                    <tr>
                        <th>Course Name</th>
                        <th>Teacher</th>
                        <th>Time</th>
                        <th>Students Enrolled</th>
                        <th>Add</th>
                    </tr>
                </thead>
                <tbody>
                    {availableCourses.map(course => (
                        <tr key={course.courseID}>
                            <td>{course.courseName}</td>
                            <td>{course.teacherName}</td>
                            <td>{course.courseTimes}</td>
                            <td>{course.currentStudents}/{course.maxStudents}</td>
                            <td>
                                <button onClick={() => handleAddCourse(course.courseID)} className="add-button">+</button>
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
                <h2>Welcome, Student!</h2>
                <button onClick={onLogout} className="logout-link">Sign out</button>
            </div>
            <h1>UC Merced</h1>
            {error && <p className="error">{error}</p>}
            <div className="course-tabs">
                <div
                    className={`tab ${tab === 'yourCourses' ? 'active-tab' : ''}`}
                    onClick={() => setTab('yourCourses')}
                >
                    Your Courses
                </div>
                <div
                    className={`tab ${tab === 'addCourses' ? 'active-tab' : ''}`}
                    onClick={() => setTab('addCourses')}
                >
                    Add Courses
                </div>
            </div>
            {tab === 'yourCourses' ? renderCourseList() : renderAddCoursesList()}
        </div>
    );
}

export default StudentDashboard;
