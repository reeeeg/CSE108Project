import React, { useState } from 'react';
import Login from './components/Login';
import StudentDashboard from './components/StudentDashboard';
import TeacherDashboard from './components/TeacherDashboard';

function App() {
    const [currentPage, setCurrentPage] = useState('login');
    const [userType, setUserType] = useState(null);
    const [userID, setUserID] = useState(null);

    const handleLogin = (id, isTeacher) => {
        console.log(isTeacher, id);
        setUserType(isTeacher ? 'teacher' : 'student');
        setUserID(id);
        setCurrentPage(isTeacher ? 'teacherDashboard' : 'studentDashboard');
    };

    const handleLogout = () => {
        setUserID(null);
        setUserType(null);
        setCurrentPage('login');
    };

    return (
        <div>
            {currentPage === 'login' && <Login onLogin={handleLogin} />}
            {currentPage === 'studentDashboard' && (
                <StudentDashboard studentID={userID} onLogout={handleLogout} />
            )}
            {currentPage === 'teacherDashboard' && (
                <TeacherDashboard teacherID={userID} onLogout={handleLogout} />
            )}
        </div>
    );

}

export default App;
