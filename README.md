# Sora LMS
A full-featured Learning Management System built with Django, designed for educational institutions to manage courses, assignments, quizzes, and track student progress.
## Features
- **Role-based Access Control** — Admin, Teacher (Guru), and Student (Siswa) roles
- **Course Management** — Hierarchical modules with video, documents, presentations, links, and text materials
- **Assignment System** — File/text submissions with grading and feedback
- **Quiz/Exam Engine** — Multiple choice, true/false, short answer, and essay questions with timer and attempt limits
- **Progress Tracking** — Automatic material completion and per-student progress reports
- **AI Chat Integration** — Gemini API-powered assistance
## Tech Stack
- Django 4.2.11
- MySQL 8.0+
- Python 3.10+
## Quick Start
### 1. Clone the repository
```bash
git clone <repository-url>
cd sora_lms
```
### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Configure environment variables
Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=sora_lms
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
```
### 5. Initialize the database
```bash
python manage.py migrate
python manage.py createsuperuser
```
### 6. Run the development server
```bash
python manage.py runserver
```
Visit `http://localhost:8000` to access the application.
## Project Structure
```
sora_lms/
├── apps/
│   ├── accounts/       # User authentication and profiles
│   ├── courses/        # Course and module management
│   ├── assignments/    # Assignment and submission system
│   ├── quizzes/       # Quiz and exam engine
│   ├── dashboard/     # Role-based dashboards
│   └── ai_chat/       # AI chat integration
├── sora_lms/          # Django project settings
├── templates/         # HTML templates
├── static/           # CSS, JavaScript, images
└── media/            # User-uploaded files
```
## License
This project is open source and available under the MIT License.
