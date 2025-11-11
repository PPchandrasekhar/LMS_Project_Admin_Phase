# Learning Management System (LMS)

A comprehensive Learning Management System built with Django that includes admin, instructor, and student panels.

## Features

### Admin Panel
- Dashboard with analytics and statistics
- Course management (CRUD operations)
- Student and instructor management
- Category management
- Material and video management
- Enrollment management
- Analytics and reporting

### Instructor Panel
- Dashboard with course statistics
- Course management
- Student progress tracking
- Material and video upload
- Assignment creation and grading
- Schedule management
- Messaging system

### Student Panel
- Dashboard with personal metrics
- Course enrollment and management
- Assignment submission and tracking
- Material and video access
- Schedule viewing
- Progress tracking

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/PPchandrasekhar/LMS_Project_Admin_Phase.git
   ```

2. Navigate to the project directory:
   ```
   cd lms
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

## Usage

### Login Credentials

- **Admin**: 
  - Username: admin
  - Password: admin123

- **Instructors**: 
  - Login with instructor ID, name, and password
  - Default password: trainer123

- **Students**: 
  - Login with student ID, name, and password
  - Default password: student123

### User Roles

1. **Admin**: Has full access to all system features
2. **Instructor**: Can manage their courses, students, materials, and assignments
3. **Student**: Can access enrolled courses, submit assignments, and view materials

## Project Structure

```
lms/
├── admin_panel/          # Admin panel application
├── courses/              # Course management application
├── instructors/          # Instructor panel application
├── students/             # Student panel application
├── templates/            # HTML templates
├── static/               # CSS, JavaScript, and images
├── manage.py             # Django management script
└── lms/                  # Main project settings
    ├── settings.py       # Configuration settings
    └── urls.py           # URL routing
```

## Key Components

### Models
- **Course**: Course information and metadata
- **Category**: Course categories
- **Module**: Course modules/sections
- **Lesson**: Individual lessons within modules
- **Material**: Course materials (PDFs, documents)
- **Video**: Course videos
- **Student**: Student profiles and information
- **Instructor**: Instructor profiles and information
- **Enrollment**: Student course enrollments
- **Assignment**: Course assignments
- **AssignmentSubmission**: Student assignment submissions
- **ScheduleEvent**: Course schedule events

### Authentication
- Role-based authentication system
- Separate login for admin, instructors, and students
- Automatic user account creation for instructors and students

## Management Commands

- `python manage.py fix_student_accounts` - Create missing user accounts for students
- `python manage.py populate_courses` - Populate sample course data (if available)

## Development

### Technologies Used
- Python 3.x
- Django 5.0.2
- SQLite (default database)
- Bootstrap 5
- HTML/CSS/JavaScript

### Customization
To customize the system:
1. Modify templates in the `templates/` directory
2. Update styles in `static/css/`
3. Add new features by extending the existing Django apps

## Deployment

For production deployment:
1. Update `settings.py` with production settings
2. Use a production database (PostgreSQL, MySQL)
3. Configure static file serving
4. Set up a proper web server (nginx, Apache)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License.