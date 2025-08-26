import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_login import LoginManager
from flask_cors import CORS
from src.models import db, User, Post, Vote, MonthlyWinner
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.posts import posts_bp
from src.routes.admin import admin_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'school_forum_secret_key_2024'

# Enable CORS for all routes
CORS(app, supports_credentials=True)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(posts_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create default admin user if it doesn't exist
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@school.edu',
            role='admin',
            grade_level='senior',
            first_name='System',
            last_name='Administrator'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # Create sample users for testing
        sample_users = [
            {
                'username': 'teacher_lang',
                'email': 'lang.teacher@school.edu',
                'role': 'language_teacher',
                'grade_level': 'senior',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'password': 'teacher123'
            },
            {
                'username': 'teacher_math',
                'email': 'math.teacher@school.edu',
                'role': 'teacher',
                'grade_level': 'middle',
                'first_name': 'Mike',
                'last_name': 'Davis',
                'password': 'teacher123'
            },
            {
                'username': 'student1',
                'email': 'student1@school.edu',
                'role': 'student',
                'grade_level': 'senior',
                'first_name': 'Emma',
                'last_name': 'Wilson',
                'password': 'student123'
            },
            {
                'username': 'parent1',
                'email': 'parent1@school.edu',
                'role': 'parent',
                'grade_level': 'junior',
                'first_name': 'Robert',
                'last_name': 'Brown',
                'password': 'parent123'
            }
        ]
        
        for user_data in sample_users:
            if not User.query.filter_by(username=user_data['username']).first():
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    role=user_data['role'],
                    grade_level=user_data['grade_level'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
        
        # Create sample principal's note
        principal_note = Post(
            title="Welcome to the New School Year!",
            content="Dear students, parents, and faculty,\n\nWelcome to another exciting school year! We are thrilled to have you all back and look forward to a year filled with learning, growth, and achievement.\n\nThis year, we have implemented several new programs and initiatives designed to enhance your educational experience. Please stay tuned for more updates and announcements.\n\nBest regards,\nDr. Principal",
            post_type="principal_note",
            grade_level="all",
            author_id=1  # admin user
        )
        db.session.add(principal_note)
        
        # Create sample announcement
        announcement = Post(
            title="Parent-Teacher Conference Schedule",
            content="Parent-teacher conferences will be held next week from October 15-19. Please check your email for your scheduled appointment time. If you need to reschedule, please contact the main office.",
            post_type="announcement",
            grade_level="all",
            author_id=1
        )
        db.session.add(announcement)
        
        # Create sample reminder
        reminder = Post(
            title="Library Books Due",
            content="Reminder: All library books are due by Friday, October 12th. Please return them to avoid late fees.",
            post_type="reminder",
            grade_level="all",
            author_id=1
        )
        db.session.add(reminder)
        
        db.session.commit()
        print("Default users and sample content created successfully!")
        print("Admin: username='admin', password='admin123'")
        print("Language Teacher: username='teacher_lang', password='teacher123'")
        print("Regular Teacher: username='teacher_math', password='teacher123'")
        print("Student: username='student1', password='student123'")
        print("Parent: username='parent1', password='parent123'")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

