from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from models import db, User, QuizResult, Coins, ShapeResult, MathResult 
import random
from datetime import datetime, timedelta
import json
from flask_cors import CORS
from flask_migrate import Migrate
import sqlite3

# After creating your Flask app and db
app = Flask(__name__)
CORS(app)
migrate = Migrate(app, db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_secret_key_change_this'

db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")

# ---------------- HELPER FUNCTIONS ----------------
def ensure_user_data():
    """Ensure the user has all required data in session"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            # Ensure avatar data is set
            if 'avatar_color' not in session or not session['avatar_color']:
                session['avatar_color'] = user.avatar_color or 'linear-gradient(135deg, #FFD166, #FFCC00)'
            if 'avatar_icon' not in session or not session['avatar_icon']:
                session['avatar_icon'] = user.avatar_icon or 'fa-user'
            
            # Ensure other required session data
            if 'age' not in session:
                session['age'] = user.age
            if 'username' not in session:
                session['username'] = user.username
            if 'gender' not in session:
                session['gender'] = user.gender
                
            return True
    return False

@app.route('/')
def home():
    return render_template('home.html')

# ---------------- AUTH ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        remember = request.form.get('remember')
        
        # Clean phone number (remove any non-digits)
        clean_phone = ''.join(filter(str.isdigit, phone))

        # First check if phone number exists
        user = User.query.filter_by(phone=clean_phone).first()
        
        if not user:
            # Phone number doesn't exist - redirect with error parameter
            return redirect(url_for('login', error='phone_not_found', phone=phone))
        
        # Phone exists, now check password
        if not user.check_password(password):
            # Password is incorrect - redirect with error parameter
            return redirect(url_for('login', error='wrong_password', phone=phone))

        # Set ALL required session variables
        session['user_id'] = user.id
        session['username'] = user.username
        session['age'] = user.age
        session['gender'] = user.gender
        
        # Set avatar data with defaults if not set
        session['avatar_color'] = user.avatar_color or 'linear-gradient(135deg, #FFD166, #FFCC00)'
        session['avatar_icon'] = user.avatar_icon or 'fa-user'
        
        # Set session permanent if remember me is checked
        if remember:
            session.permanent = True
        else:
            session.permanent = False
        
        # Update user's last active time
        user.update_last_active()
        
        print(f"User {user.username} logged in successfully. Age: {user.age}")

        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/api/check-phone-exists', methods=['GET'])
def check_phone_exists():
    """Check if phone number exists in database (for login page)"""
    phone = request.args.get('phone')
    if not phone:
        return jsonify({'error': 'Phone parameter required'}), 400
    
    # Clean phone number
    clean_phone = ''.join(filter(str.isdigit, phone))
    user = User.query.filter_by(phone=clean_phone).first()
    
    return jsonify({
        'exists': user is not None,
        'message': 'Phone number found' if user else 'Phone number not registered'
    })

@app.route('/api/check-email', methods=['GET'])
def check_email():
    """Check if email already exists"""
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email parameter required'}), 400
    
    user = User.query.filter_by(email=email).first()
    return jsonify({'exists': user is not None})

@app.route('/api/check-phone', methods=['GET'])
def check_phone():
    """Check if phone number already exists"""
    phone = request.args.get('phone')
    if not phone:
        return jsonify({'error': 'Phone parameter required'}), 400
    
    # Clean phone number (remove any non-digits)
    clean_phone = ''.join(filter(str.isdigit, phone))
    user = User.query.filter_by(phone=clean_phone).first()
    return jsonify({'exists': user is not None})

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form['username']
            email = request.form['email']
            phone = request.form['phone']
            gender = request.form['gender']
            age = request.form['age']
            password = request.form['password']
            
            # Clean phone number (remove any non-digits)
            clean_phone = ''.join(filter(str.isdigit, phone))
            
            # Server-side validation for duplicates
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                return render_template('signin.html', error='Email already registered. Please use a different email or login.')
            
            existing_phone = User.query.filter_by(phone=clean_phone).first()
            if existing_phone:
                return render_template('signin.html', error='Phone number already registered. Please use a different number or login.')
            
            # Password validation
            if len(password) < 6:
                return render_template('signin.html', error='Password must be at least 6 characters long.')
            
            if not any(c.isupper() for c in password):
                return render_template('signin.html', error='Password must contain at least one capital letter.')
            
            if not any(c.isdigit() for c in password):
                return render_template('signin.html', error='Password must contain at least one number.')
            
            # Create user
            user = User(
                username=username,
                email=email,
                phone=clean_phone,  # Store cleaned phone number
                gender=gender,
                age=age,
                # Set default avatar values
                avatar_color='linear-gradient(135deg, #FFD166, #FFCC00)',
                avatar_icon='fa-user',
                # Initialize stats
                drawings_created=0,
                favorites_count=0,
                days_active=1,
                last_active=datetime.utcnow()
            )
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            # Create coins entry
            coins = Coins(user_id=user.id, coins=0)
            db.session.add(coins)
            db.session.commit()
            
            print(f"User {user.username} created successfully with ID: {user.id}")
            
            # Flash success message
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
            
        except KeyError as e:
            db.session.rollback()
            print(f"Missing form field: {e}")
            return render_template('signin.html', error='Please fill in all required fields.')
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating user: {e}")
            return render_template('signin.html', error='Error creating account. Please try again.')

    return render_template('signin.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/clear-session')
def clear_session():
    """Clear session for testing"""
    session.clear()
    return "Session cleared. <a href='/'>Go home</a>"

@app.route('/test-db')
def test_db():
    """Test database connection and user data"""
    users = User.query.all()
    result = f"Total users: {len(users)}<br>"
    for user in users:
        result += f"User: {user.username}, Age: {user.age}, Avatar: {user.avatar_color}<br>"
    return result


# ---------------- DASHBOARD ----------------

ACTIVITIES = [
    {"name": "Learn Alphabet", "desc": "A to Z learning", "url": "/alphabet"},
    {"name": "Learn Numbers", "desc": "Fun with numbers", "url": "/numbers"},
    {"name": "Drawing", "desc": "Drawing fun", "url": "/drawing"},
    {"name": "Shape Builder", "desc": "Build shapes", "url": "/shape_builder"},
    {"name": "Smart Quiz", "desc": "Play quiz & earn coins", "url": "/quiz"},
    {"name": "Color Carnival", "desc": "Spin the wheel & win coins", "url": "/colour_carnival"},
]

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        print("No user_id in session, redirecting to login")
        return render_template('kids_dashboard.html', logged_in=False)

    user = User.query.get(session['user_id'])
    
    # If user not found, clear session and redirect to login
    if not user:
        session.clear()
        print("User not found in database, clearing session")
        return redirect(url_for('login'))
    
    # Ensure session has all required data
    if 'age' not in session:
        session['age'] = user.age
    if 'username' not in session:
        session['username'] = user.username
    if 'gender' not in session:
        session['gender'] = user.gender
    if 'avatar_color' not in session:
        session['avatar_color'] = user.avatar_color or 'linear-gradient(135deg, #FFD166, #FFCC00)'
    if 'avatar_icon' not in session:
        session['avatar_icon'] = user.avatar_icon or 'fa-user'
    
    # Get coins with error handling
    coins_obj = Coins.query.filter_by(user_id=user.id).first()
    coins = coins_obj.coins if coins_obj else 0
    
    # Update user's last active
    user.update_last_active()

    print(f"Showing dashboard for user: {user.username}, Age: {user.age}, Coins: {coins}")

    # Determine which dashboard to show based on age
    if session.get('age') == '1-4':
        print("Showing kids dashboard")
        return render_template(
            'kids_dashboard.html',
            username=session.get('username', 'User'),
            gender=session.get('gender', ''),
            coins=coins,
            logged_in=True
        )
    else:
        print("Showing junior dashboard")
        return render_template(
            'junior_dashboard.html',
            username=session.get('username', 'User'),
            gender=session.get('gender', ''),
            coins=coins,
            activities=ACTIVITIES,
            logged_in=True
        )

# ---------------- ACTIVITIES PAGE ----------------
@app.route('/activities')
def activities():
    """Activities page showing all available activities"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('activities.html', activities=ACTIVITIES)


@app.route('/alphabet')
def alphabet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('alphabet.html')


@app.route('/numbers')
def numbers():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('numbers.html')


@app.route('/drawing')
def drawing():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('drawing.html')


@app.route('/math')
def math():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('math.html')


@app.route('/careers')
def careers():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Sample careers data
    careers = [
        {"name": "Doctor", "desc": "Helps people when they are sick"},
        {"name": "Teacher", "desc": "Teaches children in school"},
        {"name": "Firefighter", "desc": "Puts out fires and saves people"},
        {"name": "Police Officer", "desc": "Keeps everyone safe"},
        {"name": "Chef", "desc": "Cooks delicious food"},
        {"name": "Astronaut", "desc": "Travels to space"},
        {"name": "Artist", "desc": "Creates beautiful paintings"},
        {"name": "Scientist", "desc": "Discovers new things"}
    ]
    return render_template('career_explorer.html', careers=careers)


# ---------------- QUIZ DATA ----------------

QUIZ_QUESTIONS = [
    # Numeric (5 questions)
    {"question": "5 + 3 = ?", "answer": "8", "category": "numeric"},
    {"question": "10 - 4 = ?", "answer": "6", "category": "numeric"},
    {"question": "What is 2 + 2?", "answer": "4", "category": "numeric"},
    {"question": "How many days are in a week?", "answer": "7", "category": "numeric"},
    {"question": "What is 10 + 5?", "answer": "15", "category": "numeric"},

    # General (5 questions)
    {"question": "What animal is known as man's best friend?", "answer": "dog", "category": "general"},
    {"question": "What do you call a baby dog?", "answer": "puppy", "category": "general"},
    {"question": "What is the capital of India?", "answer": "delhi", "category": "general"},
    {"question": "What do cows drink?", "answer": "water", "category": "general"},
    {"question": "What is the color of snow?", "answer": "white", "category": "general"},

    # Geography (5 questions)
    {"question": "What color is the sky on a clear day?", "answer": "blue", "category": "geography"},
    {"question": "What is the color of grass?", "answer": "green", "category": "geography"},
    {"question": "What color are bananas?", "answer": "yellow", "category": "geography"},
    {"question": "What is the color of the ocean?", "answer": "blue", "category": "geography"},
    {"question": "What is the largest continent?", "answer": "asia", "category": "geography"},

    # Science (5 questions)
    {"question": "How many legs does a spider have?", "answer": "8", "category": "science"},
    {"question": "How many fingers do you have on one hand?", "answer": "5", "category": "science"},
    {"question": "What do bees make?", "answer": "honey", "category": "science"},
    {"question": "How many wheels does a bicycle have?", "answer": "2", "category": "science"},
    {"question": "What is the opposite of hot?", "answer": "cold", "category": "science"},

    # History (5 questions)
    {"question": "Who was the first President of India?", "answer": "rajendra prasad", "category": "history"},
    {"question": "In which year did India gain independence?", "answer": "1947", "category": "history"},
    {"question": "Who discovered America?", "answer": "christopher columbus", "category": "history"},
    {"question": "What was the name of the ship that carried the Pilgrims to America?", "answer": "mayflower", "category": "history"},
    {"question": "Who was the first man to walk on the moon?", "answer": "neil armstrong", "category": "history"},

    # Sports (5 questions)
    {"question": "How many players are there in a cricket team?", "answer": "11", "category": "sports"},
    {"question": "What sport is known as the 'king of sports'?", "answer": "football", "category": "sports"},
    {"question": "In which sport do you use a racket and shuttlecock?", "answer": "badminton", "category": "sports"},
    {"question": "How many points is a touchdown worth in American football?", "answer": "6", "category": "sports"},
    {"question": "What is the highest score possible in ten-pin bowling?", "answer": "300", "category": "sports"}
]


# ---------------- QUIZ ----------------
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.args.get('clear') == '1':
        session.pop('selected_questions', None)
        return redirect(url_for('quiz'))

    if request.method == 'POST':

        if 'category' in request.form:
            category = request.form['category']
            questions = [q for q in QUIZ_QUESTIONS if q['category'] == category]
            selected = random.sample(questions, min(5, len(questions)))
            session['selected_questions'] = selected
            return render_template('quiz.html', questions=selected)

        score = 0
        questions = session.get('selected_questions', [])

        for i, q in enumerate(questions):
            if request.form.get(f"q{i}", "").lower() == q['answer']:
                score += 1

        db.session.add(QuizResult(
            user_id=session['user_id'],
            score=score,
            date_taken=datetime.now()
        ))
        db.session.commit()

        coins_obj = Coins.query.filter_by(user_id=session['user_id']).first()
        if not coins_obj:
            coins_obj = Coins(user_id=session['user_id'], coins=0)
            db.session.add(coins_obj)

        coins_obj.coins += score
        db.session.commit()

        return redirect(url_for('quiz_result'))

    return render_template('quiz_category.html')


@app.route('/quiz-result')
def quiz_result():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    last = QuizResult.query.filter_by(user_id=session['user_id']) \
        .order_by(QuizResult.id.desc()).first()

    coins = Coins.query.filter_by(user_id=session['user_id']).first()
    coins_amount = coins.coins if coins else 0

    return render_template('quiz_result.html', score=last.score, coins=coins_amount)


# ---------------- PROGRESS ----------------
@app.route('/progress')
def progress():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']

    # Fetch all results (removed RhythmResult)
    quiz_results = QuizResult.query.filter_by(user_id=user_id).all()
    shape_results = ShapeResult.query.filter_by(user_id=user_id).all()
    math_results = MathResult.query.filter_by(user_id=user_id).all()

    # Get total coins from Coins table (this is the current balance)
    coins_obj = Coins.query.filter_by(user_id=user_id).first()
    total_coins = coins_obj.coins if coins_obj else 0
    
    # Calculate coins earned from each activity
    quiz_total_coins = sum(r.score for r in quiz_results) if quiz_results else 0
    shape_total_coins = sum(r.coins_awarded for r in shape_results) if shape_results else 0
    math_total_coins = sum(r.coins_awarded for r in math_results) if math_results else 0
    
    # Calculate total earned all time
    total_earned_coins = quiz_total_coins + shape_total_coins + math_total_coins

    # Number of attempts
    quiz_attempts = len(quiz_results)
    shape_attempts = len(shape_results)
    math_attempts = len(math_results)

    # Calculate average scores
    quiz_avg = round(sum(r.score for r in quiz_results) / quiz_attempts, 1) if quiz_attempts else 0
    shape_avg_similarity = round(sum(r.similarity_score for r in shape_results) / shape_attempts, 1) if shape_attempts else 0
    math_avg_score = round(sum(r.score for r in math_results) / math_attempts, 1) if math_attempts else 0
    
    # Calculate TOTAL AVERAGE SCORE (all activities combined, normalized to 0-5 scale)
    normalized_scores = []
    
    if quiz_attempts > 0:
        normalized_scores.append(quiz_avg)  # Already 0-5
    if shape_attempts > 0:
        normalized_scores.append(shape_avg_similarity / 20)  # Convert 0-100 to 0-5
    if math_attempts > 0:
        normalized_scores.append(math_avg_score / 2)  # Convert 0-10 to 0-5
    
    # Calculate total average score across all activities
    if normalized_scores:
        total_avg_score = round(sum(normalized_scores) / len(normalized_scores), 1)
    else:
        total_avg_score = 0

    # Performance level based on total average score
    if total_avg_score < 2:
        performance_level = "Beginner"
    elif total_avg_score < 3:
        performance_level = "Good"
    elif total_avg_score < 4:
        performance_level = "Very Good"
    else:
        performance_level = "Excellent"

    # Weekly data for the last 7 days
    today = datetime.now().date()
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    start_of_week = today - timedelta(days=today.weekday())
    
    coins_per_day = []
    quiz_coins_per_day = []
    shape_coins_per_day = []
    math_coins_per_day = []

    # Calculate coins for each day of the week
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        day_coins = 0
        day_quiz_coins = 0
        day_shape_coins = 0
        day_math_coins = 0
        
        # Quiz coins for this day
        for r in quiz_results:
            if hasattr(r, 'date_taken') and r.date_taken:
                if day_start <= r.date_taken <= day_end:
                    day_coins += r.score
                    day_quiz_coins += r.score
        
        # Shape coins for this day
        for r in shape_results:
            if hasattr(r, 'created_at') and r.created_at:
                if day_start <= r.created_at <= day_end:
                    day_coins += r.coins_awarded
                    day_shape_coins += r.coins_awarded
        
        # Math coins for this day
        for r in math_results:
            if hasattr(r, 'created_at') and r.created_at:
                if day_start <= r.created_at <= day_end:
                    day_coins += r.coins_awarded
                    day_math_coins += r.coins_awarded
        
        coins_per_day.append(day_coins)
        quiz_coins_per_day.append(day_quiz_coins)
        shape_coins_per_day.append(day_shape_coins)
        math_coins_per_day.append(day_math_coins)

    return render_template('progress.html',
                           total_coins=total_coins,
                           total_earned_coins=total_earned_coins,
                           quiz_total_coins=quiz_total_coins,
                           shape_total_coins=shape_total_coins,
                           math_total_coins=math_total_coins,
                           total_avg_score=total_avg_score,
                           performance_level=performance_level,
                           quiz_attempts=quiz_attempts,
                           shape_attempts=shape_attempts,
                           math_attempts=math_attempts,
                           quiz_avg=quiz_avg,
                           shape_avg_similarity=shape_avg_similarity,
                           math_avg_score=math_avg_score,
                           days=days,
                           coins_per_day=coins_per_day,
                           quiz_coins_per_day=quiz_coins_per_day,
                           shape_coins_per_day=shape_coins_per_day,
                           math_coins_per_day=math_coins_per_day)  
            
@app.route('/progress-data')
def progress_data():
    if 'user_id' not in session:
        return {"error": "Not logged in"}, 401

    quiz_results = QuizResult.query.filter_by(user_id=session['user_id']).all()
    shape_results = ShapeResult.query.filter_by(user_id=session['user_id']).all()
    math_results = MathResult.query.filter_by(user_id=session['user_id']).all()

    quiz_attempts = len(quiz_results)
    quiz_total = sum(r.score for r in quiz_results)
    quiz_avg = round(quiz_total / quiz_attempts, 2) if quiz_attempts else 0

    shape_attempts = len(shape_results)
    shape_total_coins = sum(r.coins_awarded for r in shape_results)
    shape_avg_similarity = round(sum(r.similarity_score for r in shape_results) / shape_attempts, 2) if shape_attempts else 0

    math_attempts = len(math_results)
    math_total_coins = sum(r.coins_awarded for r in math_results)
    math_avg_score = round(sum(r.score for r in math_results) / math_attempts, 1) if math_attempts else 0

    total_coins = quiz_total + shape_total_coins + math_total_coins

    # Calculate performance level based on quiz and shape
    combined_avg = (quiz_avg + shape_avg_similarity / 20) / 2 if quiz_attempts or shape_attempts else 0
    if combined_avg < 2:
        performance_level = "Beginner"
    elif combined_avg < 4:
        performance_level = "Intermediate"
    else:
        performance_level = "Advanced"

    today = datetime.now().date()
    start = today - timedelta(days=today.weekday())
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    coins_per_day = []

    for i in range(7):
        day = start + timedelta(days=i)
        quiz_coins = sum(r.score for r in quiz_results if r.date_taken.date() == day)
        shape_coins = sum(r.coins_awarded for r in shape_results if r.created_at.date() == day)
        math_coins = sum(r.coins_awarded for r in math_results if r.created_at.date() == day)
        coins_per_day.append(quiz_coins + shape_coins + math_coins)

    total_avg_score = round((quiz_avg + shape_avg_similarity / 20 + math_avg_score / 2) / 3, 2) if (quiz_attempts or shape_attempts or math_attempts) else 0

    # Determine performance level based on total_avg_score
    if total_avg_score < 2:
        performance_level = "Poor"
    elif total_avg_score < 3.5:
        performance_level = "Good"
    elif total_avg_score < 4.5:
        performance_level = "Very Good"
    else:
        performance_level = "Excellent"

    return {
        'quiz_attempts': quiz_attempts,
        'shape_attempts': shape_attempts,
        'math_attempts': math_attempts,
        'total_coins': total_coins,
        'total_avg_score': total_avg_score,
        'performance_level': performance_level,
        'days': days,
        'coins_per_day': coins_per_day
    }
    
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        try:
            # Update basic profile info
            user.username = request.form['username']
            user.email = request.form['email']
            user.phone = request.form['phone']
            user.age = request.form['age']
            
            # Update avatar if provided
            if 'avatar_color' in request.form:
                user.avatar_color = request.form['avatar_color']
            if 'avatar_icon' in request.form:
                user.avatar_icon = request.form['avatar_icon']
            
            db.session.commit()
            
            # Update session data
            session['age'] = user.age
            session['username'] = user.username
            session['avatar_color'] = user.avatar_color if user.avatar_color else 'linear-gradient(135deg, #FFD166, #FFCC00)'
            session['avatar_icon'] = user.avatar_icon if user.avatar_icon else 'fa-user'
            
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')
            return redirect(url_for('profile'))

    if hasattr(user, 'update_days_active'):
        user.update_days_active()
    else:
        # Fallback: Update last_active field
        user.last_active = datetime.utcnow()
        db.session.commit()
    
    return render_template('profile.html', user=user)

# Store user progress and coins
users = {}

# Store active calls (in-memory for now)
active_calls = {}

# Shape tasks database
shape_tasks = [
    {
        "id": 1,
        "name": "Ice Cream",
        "description": "Build an ice cream cone",
        "shapes": [
            {"type": "triangle", "color": "#FFD700", "position": "50% 20%", "size": "100px"},
            {"type": "circle", "color": "#FFB6C1", "position": "50% 5%", "size": "60px"}
        ],
        "validation_rules": {
            "min_shapes": 2,
            "required_shapes": ["triangle", "circle"],
            "position_tolerance": 50
        }
    },
    {
        "id": 2,
        "name": "Sun",
        "description": "Build a sunny day scene",
        "shapes": [
            {"type": "circle", "color": "#FFD700", "position": "50% 50%", "size": "80px"},
            {"type": "triangle", "color": "#FFA500", "position": "50% 20%", "size": "40px", "rotation": "0deg"}
        ],
        "validation_rules": {
            "min_shapes": 2,
            "required_shapes": ["circle"],
            "position_tolerance": 25
        }
    },
    {
        "id": 3,
        "name": "House",
        "description": "Build a simple house",
        "shapes": [
            {"type": "square", "color": "#8B4513", "position": "50% 60%", "size": "100px"},
            {"type": "triangle", "color": "#B22222", "position": "50% 40%", "size": "120px"}
        ],
        "validation_rules": {
            "min_shapes": 2,
            "required_shapes": ["square", "triangle"],
            "position_tolerance": 30
        }
    },
    {
        "id": 4,
        "name": "Tree",
        "description": "Build a green tree",
        "shapes": [
            {"type": "triangle", "color": "#228B22", "position": "50% 30%", "size": "100px"},
            {"type": "rectangle", "color": "#8B4513", "position": "50% 60%", "size": "30px 60px"}
        ],
        "validation_rules": {
            "min_shapes": 2,
            "required_shapes": ["triangle", "rectangle"],
            "position_tolerance": 25
        }
    }
]


@app.route('/shape_builder')
def shape_builder():
    """Shape builder game page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('shape_builder.html')

@app.route('/api/get_task', methods=['GET'])
def get_task():
    """Get a random shape task"""
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session['user_id']

    # Initialize user data if not exists
    if user_id not in users:
        users[user_id] = {
            "coins": 0,
            "completed_tasks": [],
            "current_task": None
        }

    # Get a task that hasn't been completed
    available_tasks = [task for task in shape_tasks if task['id'] not in users[user_id]['completed_tasks']]

    if not available_tasks:
        # Reset if all tasks completed
        users[user_id]['completed_tasks'] = []
        available_tasks = shape_tasks

    task = random.choice(available_tasks)
    users[user_id]['current_task'] = task['id']

    # Send only necessary info to client
    task_info = {
        "id": task["id"],
        "name": task["name"],
        "description": task["description"],
        "target_shapes": task["shapes"]
    }

    return jsonify(task_info)

@app.route('/api/validate_shape', methods=['POST'])
def validate_shape():
    """Validate user's shape against the task"""
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    user_id = session['user_id']
    user_shapes = data.get('shapes', [])
    task_id = data.get('task_id')

    # Find the current task
    current_task = None
    for task in shape_tasks:
        if task['id'] == task_id:
            current_task = task
            break

    if not current_task:
        return jsonify({"error": "Task not found"}), 404

    # Get validation rules
    rules = current_task['validation_rules']

    # Basic validation
    if len(user_shapes) < rules['min_shapes']:
        return jsonify({
            "valid": False,
            "message": f"Need at least {rules['min_shapes']} shapes"
        })

    # Check required shape types
    user_shape_types = [shape['type'] for shape in user_shapes]
    for required in rules['required_shapes']:
        if required not in user_shape_types:
            return jsonify({
                "valid": False,
                "message": f"Missing required shape: {required}"
            })

    # Award coins
    coins_obj = Coins.query.filter_by(user_id=user_id).first()
    if not coins_obj:
        coins_obj = Coins(user_id=user_id, coins=0)
        db.session.add(coins_obj)

    coins_awarded = 10
    coins_obj.coins += coins_awarded
    
    # Record shape result
    shape_result = ShapeResult(
        user_id=user_id,
        similarity_score=100,
        coins_awarded=coins_awarded
    )
    db.session.add(shape_result)
    db.session.commit()

    # Update in-memory storage
    if user_id not in users:
        users[user_id] = {
            "coins": 0,
            "completed_tasks": [],
            "current_task": None
        }
    users[user_id]['coins'] = coins_obj.coins
    users[user_id]['completed_tasks'].append(task_id)

    return jsonify({
        "valid": True,
        "message": "Great job! Shape matches!",
        "coins": coins_obj.coins,
        "award": coins_awarded
    })

@app.route('/api/user_stats', methods=['GET'])
def user_stats():
    """Get user statistics"""
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    user_id = session['user_id']

    # Get coins from database
    coins_obj = Coins.query.filter_by(user_id=user_id).first()
    coins = coins_obj.coins if coins_obj else 0

    # Get completed tasks from database
    completed_tasks = ShapeResult.query.filter_by(user_id=user_id).count()

    return jsonify({
        "coins": coins,
        "completed_tasks": completed_tasks,
        "total_tasks": len(shape_tasks)
    })
        
@app.route('/api/math/complete', methods=['POST'])
def record_math_result():
    """API endpoint for recording math game completion"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    try:
        data = request.get_json()
        level_completed = data.get('level', 1)
        score = data.get('score', 0)
        coins_earned = data.get('coins_earned', 0)

        # Update user's coins
        coins_obj = Coins.query.filter_by(user_id=session['user_id']).first()
        if not coins_obj:
            coins_obj = Coins(user_id=session['user_id'], coins=0)
            db.session.add(coins_obj)

        coins_obj.coins += coins_earned
        db.session.commit()

        # Record math result
        db.session.add(MathResult(
            user_id=session['user_id'],
            level_completed=level_completed,
            score=score,
            coins_awarded=coins_earned
        ))
        db.session.commit()

        return jsonify({
            'success': True,
            'total_coins': coins_obj.coins,
            'message': f'Level {level_completed} completed! Earned {coins_earned} coins.'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_time_ago(dt):
    """Helper function to get time ago string"""
    now = datetime.utcnow()
    diff = now - dt

    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"

# List of colors with their names
COLORS = [
    {"name": "Red", "code": "#FF0000"},
    {"name": "Green", "code": "#00FF00"},
    {"name": "Blue", "code": "#0000FF"},
    {"name": "Yellow", "code": "#FFFF00"},
    {"name": "Purple", "code": "#800080"},
    {"name": "Orange", "code": "#FFA500"},
    {"name": "Pink", "code": "#FFC0CB"},
    {"name": "Cyan", "code": "#00FFFF"},
    {"name": "Magenta", "code": "#FF00FF"},
    {"name": "Lime", "code": "#00FF00"},
    {"name": "Brown", "code": "#A52A2A"},
    {"name": "Teal", "code": "#008080"},
    {"name": "Navy", "code": "#000080"},
    {"name": "Gold", "code": "#FFD700"},
    {"name": "Silver", "code": "#C0C0C0"}
]

@app.route('/colour_carnival')
def colour_carnival():
    """Color Carnival page - spin wheel and learn colors"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get user's coins
    coins_obj = Coins.query.filter_by(user_id=session['user_id']).first()
    coins = coins_obj.coins if coins_obj else 0
    
    return render_template('colour_carnival.html', colors=COLORS, coins=coins)

@app.route('/api/colour_carnival/spin', methods=['POST'])
def colour_carnival_spin():
    """Handle color carnival spin and award coins"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    try:
        data = request.get_json()
        color_name = data.get('color')
        color_code = data.get('code')
        
        # Award coins (5 coins per spin)
        coins_earned = 5
        
        # Update user's coins
        coins_obj = Coins.query.filter_by(user_id=session['user_id']).first()
        if not coins_obj:
            coins_obj = Coins(user_id=session['user_id'], coins=0)
            db.session.add(coins_obj)

        coins_obj.coins += coins_earned
        db.session.commit()

        return jsonify({
            'success': True,
            'coins_earned': coins_earned,
            'total_coins': coins_obj.coins,
            'message': f'You won {coins_earned} coins!'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/api/colors', methods=['GET'])
def get_colors():
    """API endpoint to get colors list"""
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    # Return the existing COLORS list
    return jsonify(COLORS)

if __name__ == '__main__':
    app.run(debug=True, port=5000)  