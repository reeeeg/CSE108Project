const teachingCoursesTbody = document.getElementById('teaching-courses-tbody');
const courseModal = document.getElementById('course-modal');
const courseNameElement = document.getElementById('course-name');
const courseStudentsTbody = document.getElementById('course-students-tbody');
const closeModalBtn = document.getElementById('close-modal');

// data for courses being teached
const teachingCourses = [
    
];

// Render teaching courses
teachingCourses.forEach((course) => {
    const row = document.createElement('TR');
    row.innerHTML = `
        <td><a href="#" data-course-name="${course.courseName}">${course.courseName}</a></td>
        <td>${course.teacher}</td>
        <td>${course.time}</td>
        <td>${course.studentsEnrolled}</td>
    `;
    teachingCoursesTbody.appendChild(row);
});

// Course click event listener
document.querySelectorAll('#teaching-courses-table a').forEach((link) => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const courseName = link.getAttribute('data-course-name');
        const course = teachingCourses.find((c) => c.courseName === courseName);
        showCourseDetails(course);
    });
});

// close 
closeModalBtn.addEventListener('click', () => {
    courseModal.style.display = 'none';
});

// course details
function showCourseDetails(course) {
    courseModal.style.display = 'block';
    courseNameElement.innerText = course.courseName;
    courseStudentsTbody.innerHTML = '';
    course.students.forEach((student) => {
        const row = document.createElement('TR');
        row.innerHTML = `
            <td>${student.name}</td>
            <td><input type="text" value="${student.grade}" /></td>
        `;
        courseStudentsTbody.appendChild(row);
    });
}

// edit grades
courseStudentsTbody.addEventListener('input', (e) => {
    if (e.target.tagName === 'INPUT') {
        const gradeInput = e.target;
        const studentName = gradeInput.closest('TR').children[0].innerText;
        const course = teachingCourses.find((c) =>
            c.students.some((s) => s.name === studentName)
        );
        const student = course.students.find((s) => s.name === studentName);
        student.grade = gradeInput.value;
        console.log(`Updated grade for ${studentName} to ${gradeInput.value}`);
    }
});