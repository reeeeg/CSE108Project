import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';

const Login = ({ onLogin }) => {
    const [userID, setUserID] = useState('');
    const [password, setPassword] = useState('');
    const [is_Teacher, setIsTeacher] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('/api/login', { userID, password}); //removed isTeacher from bar
            
            if (response.data.success) {
                // Pass both user type and ID to the App component
                console.log(response.data.isTeacher);
                onLogin(userID, response.data.isTeacher);
            } else {
                setError('Invalid credentials');
            }
        } catch (error) {
            setError('Login failed. Please try again.');
        }
    };

    return (
        <div className="login-container">
            <h2>Login</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <form onSubmit={handleLogin}>
                <div>
                    <label>User ID:</label>
                    <input
                        type="text"
                        value={userID}
                        onChange={(e) => setUserID(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Password:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                
                {/* <div>
                    <label>Are you a teacher?</label>
                    <input
                        type="checkbox"
                        checked={isTeacher}
                        onChange={(e) => setIsTeacher(e.target.checked)}
                    />
                </div> */}
                <button type="submit">Login</button>
            </form>
        </div>
    );
};

export default Login;
