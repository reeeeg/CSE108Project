const currentCoursesTbody = document.getElementById('current-courses-tbody');
const allCoursesTbody = document.getElementById('all-courses-tbody');

// data for courses being taken
const currentCourses = [
    
];

// data for all courses
const allCourses = [
    
];

// show current courses
currentCourses.forEach((course) => {
    const row = document.createElement('TR');
    row.innerHTML = `
        <td>${course.courseName}</td>
        <td>${course.teacher}</td>
        <td>${course.dayTime}</td>
        <td>${course.studentsEnrolled}</td>
    `;
    currentCoursesTbody.appendChild(row);
});

// show all courses
allCourses.forEach((course) => {
    const row = document.createElement('TR');
    row.innerHTML = `
        <td>${course.courseName}</td>
        <td>${course.teacher}</td>
        <td>${course.time}</td>
        <td>${course.studentsEnrolled}</td>
        <td>
            <button class="add-drop-btn">Add</button>
            <button class="add-drop-btn" style="display: none;">Drop</button>
        </td>
    `;
    allCoursesTbody.appendChild(row);
});

// add/drop classes (need to fix this)
document.querySelectorAll('.add-drop-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
        
        btn.style.display = 'none';
        btn.nextElementSibling ? btn.nextElementSibling.style.display = 'inline' : btn.previousElementSibling.style.display = 'inline';
        
        console.log('Add/Drop button clicked');
    });
});