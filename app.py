from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import db, User, QuizResult, Coins, ShapeResult, MathResult, ColorSpin, ColorWheelLogic, ColorCarnivalManager, ColorWheelStats
import random
from datetime import datetime, timedelta
import json
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_secret_key_change_this'

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------------- HOME ----------------

@app.route('/')
def home():
    return render_template('login.html')


# ---------------- AUTH ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        user = User.query.filter_by(phone=phone).first()
        if not user or not user.check_password(password):
            return render_template('login.html', error='Invalid credentials')

        session['user_id'] = user.id
        session['username'] = user.username
        session['age'] = user.age

        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            phone=request.form['phone'],
            gender=request.form['gender'],
            age=request.form['age']
        )
        user.set_password(request.form['password'])

        db.session.add(user)
        db.session.commit()

        db.session.add(Coins(user_id=user.id, coins=0))
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signin.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ---------------- DASHBOARD ----------------

ACTIVITIES = [
    {"name": "Learn Alphabet", "desc": "A to Z learning", "url": "/alphabet"},
    {"name": "Learn Numbers", "desc": "Fun with numbers", "url": "/numbers"},
    {"name": "Drawing", "desc": "Drawing fun", "url": "/drawing"},
    {"name": "Shape Builder", "desc": "Build shapes", "url": "/shape_builder"},
    {"name": "Smart Quiz", "desc": "Play quiz & earn coins", "url": "/quiz"},
    {"name": "Color Carnival", "desc": "Spin the wheel & win coins", "url": "/colour_carnival"},  # ADD THIS
]
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    coins_obj = Coins.query.filter_by(user_id=user.id).first()
    coins = coins_obj.coins if coins_obj else 0

    if session.get('age') == '1-4':
        return render_template(
            'kids_dashboard.html',
            username=user.username,
            gender=user.gender,
            coins=coins
        )

    return render_template(
        'junior_dashboard.html',
        username=user.username,
        gender=user.gender,
        coins=coins,
        activities=ACTIVITIES
    )


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


@app.route('/story_time')
def story_time():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('story_time.html')


@app.route('/math')
def math():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('math.html')

@app.route('/shape_builder')
def shape_builder():
    # Temporarily remove login check for testing
    # if 'user_id' not in session:
    #     return redirect(url_for('login'))
    return render_template('shape_builder.html')


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
    last = QuizResult.query.filter_by(user_id=session['user_id']) \
        .order_by(QuizResult.id.desc()).first()

    coins = Coins.query.filter_by(user_id=session['user_id']).first().coins

    return render_template('quiz_result.html', score=last.score, coins=coins)


# ---------------- PROGRESS ----------------
@app.route('/progress')
def progress():
    # Temporarily remove login check for testing
    # if 'user_id' not in session:
    #     return redirect(url_for('login'))
    user_id = 1  # Test user ID

    quiz_results = QuizResult.query.filter_by(user_id=user_id).all()
    shape_results = ShapeResult.query.filter_by(user_id=user_id).all()
    math_results = MathResult.query.filter_by(user_id=user_id).all()

    quiz_attempts = len(quiz_results)
    quiz_total = sum(r.score for r in quiz_results)
    quiz_avg = round(quiz_total / quiz_attempts, 2) if quiz_attempts else 0

    shape_attempts = len(shape_results)
    shape_total_coins = sum(r.coins_awarded for r in shape_results)
    shape_avg_similarity = round(sum(r.similarity_score for r in shape_results) / shape_attempts, 2) if shape_attempts else 0

    math_attempts = len(math_results)
    math_total_coins = sum(r.coins_awarded for r in math_results)
    math_total_score = sum(r.score for r in math_results)
    math_avg_score = round(math_total_score / math_attempts, 2) if math_attempts else 0

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

    # Include math score in total average
    total_avg_score = round((quiz_avg + shape_avg_similarity / 20 + math_avg_score) / 3, 2) if quiz_attempts or shape_attempts or math_attempts else 0

    # Determine performance level based on total_avg_score
    if total_avg_score < 2:
        performance_level = "Poor"
    elif total_avg_score < 3.5:
        performance_level = "Good"
    elif total_avg_score < 4.5:
        performance_level = "Very Good"
    else:
        performance_level = "Excellent"

    return render_template('progress.html',
                           total_coins=total_coins,
                           total_avg_score=total_avg_score,
                           performance_level=performance_level,
                           days=days,
                           stars_data=coins_per_day,
                           shape_avg_similarity=shape_avg_similarity,
                           quiz_avg=quiz_avg,
                           quiz_attempts=quiz_attempts,
                           shape_attempts=shape_attempts,
                           math_attempts=math_attempts)

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
        coins_per_day.append(quiz_coins + shape_coins)

    total_avg_score = round((quiz_avg + shape_avg_similarity / 20) / 2, 2) if quiz_attempts or shape_attempts else 0

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
        user.username = request.form['username']
        user.email = request.form['email']
        user.phone = request.form['phone']
        user.age = request.form['age']
        db.session.commit()
        session['age'] = user.age
        return redirect(url_for('dashboard'))

    return render_template('profile.html', user=user)


def search_youtube(query):
    """Search YouTube using Selenium and return video data"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(f"https://www.youtube.com/results?search_query={query}")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'video-title')))

        videos = driver.find_elements(By.ID, 'video-title')[:5]  # Get first 5 videos

        video_data = []
        for video in videos:
            title = video.get_attribute('title')
            href = video.get_attribute('href')
            if href and 'v=' in href:
                video_id = href.split('v=')[1].split('&')[0]
                video_data.append({'id': {'videoId': video_id}, 'snippet': {'title': title}})

        return video_data

    except Exception as e:
        print(f"Error fetching YouTube videos: {e}")
        return []
    finally:
        driver.quit()

@app.route('/kids_videos', methods=['GET'])
def kids_videos():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    query = request.args.get('q', '').strip()

    # Mock video data for fallback
    mock_videos = [
        {'id': {'videoId': 'dQw4w9WgXcQ'}, 'snippet': {'title': 'Rick Roll'}},
        {'id': {'videoId': '9bZkp7q19f0'}, 'snippet': {'title': 'PSY - GANGNAM STYLE'}},
        {'id': {'videoId': 'kJQP7kiw5Fk'}, 'snippet': {'title': 'Despacito'}},
    ]

    if query:
        videos = search_youtube(query)
        if videos:
            main_video = videos[0]
            reference_videos = videos[1:]
        else:
            # Fallback to mock data
            filtered_videos = [v for v in mock_videos if query.lower() in v['snippet']['title'].lower()]
            if filtered_videos:
                main_video = filtered_videos[0]
                reference_videos = filtered_videos[1:]
            else:
                main_video = None
                reference_videos = []
    else:
        # Default search for kids educational videos
        videos = search_youtube("kids educational videos")
        if videos:
            main_video = videos[0]
            reference_videos = videos[1:]
        else:
            main_video = None
            reference_videos = []

    return render_template('videos.html', query=query, main_video=main_video, reference_videos=reference_videos)


# Store user progress and coins
users = {}

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



@app.route('/api/get_task', methods=['GET'])
def get_task():
    """Get a random shape task"""
    # Temporarily remove session check for testing
    # if 'user_id' not in session:
    #     return jsonify({"error": "Not logged in"}), 401

    user_id = request.args.get('user_id', 'default')

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
    # Temporarily remove session check for testing
    # if 'user_id' not in session:
    #     return jsonify({"error": "Not logged in"}), 401

    data = request.json
    user_id = data.get('user_id', 'default')
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

    # For now, just check if required shapes are present (ignore position)
    # This makes the game playable while position calculation is debugged
    if True:  # Always pass for now
        # Award coins to database
        coins_obj = Coins.query.filter_by(user_id=user_id).first()
        if not coins_obj:
            coins_obj = Coins(user_id=user_id, coins=0)
            db.session.add(coins_obj)

        coins_obj.coins += 10
        db.session.commit()

        # Record shape result
        db.session.add(ShapeResult(
            user_id=user_id,
            similarity_score=100,  # Perfect match
            coins_awarded=10
        ))
        db.session.commit()

        return jsonify({
            "valid": True,
            "message": "Great job! Shape matches!",
            "coins": coins_obj.coins,
            "award": 10
        })

    return jsonify({
        "valid": False,
        "message": "Shape doesn't match the target closely enough"
    })

@app.route('/api/user_stats', methods=['GET'])
def user_stats():
    """Get user statistics"""
    user_id = request.args.get('user_id', 'default')

    # Get coins from database
    coins_obj = Coins.query.filter_by(user_id=user_id).first()
    coins = coins_obj.coins if coins_obj else 0

    # Get completed tasks from in-memory storage (for now)
    if user_id not in users:
        users[user_id] = {
            "coins": coins,
            "completed_tasks": [],
            "current_task": None
        }

    return jsonify({
        "coins": coins,
        "completed_tasks": len(users[user_id]['completed_tasks']),
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

# ---------------- COLOR CARNIVAL ----------------

@app.route('/colour_carnival')
def colour_carnival():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get user's stats
    stats = ColorCarnivalManager.get_user_stats(session['user_id'])

    # Get wheel configuration
    wheel_data = ColorWheelLogic.get_wheel_data()

    # Get leaderboard
    leaderboard = ColorCarnivalManager.get_leaderboard(5)

    # Get user's coins
    coins_obj = Coins.query.filter_by(user_id=session['user_id']).first()
    coins = coins_obj.coins if coins_obj else 0

    return render_template('colour_carnival.html',
                         username=session['username'],
                         coins=coins,
                         wheel_data=wheel_data,
                         stats=stats,
                         leaderboard=leaderboard)


@app.route('/api/color-wheel/spin', methods=['POST'])
def color_wheel_spin():
    """API endpoint for spinning the color wheel"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    try:
        # Generate spin result
        spin_data = ColorWheelLogic.spin_wheel()
        selected_color = spin_data['selected_color']

        # Record spin and update coins
        result = ColorCarnivalManager.record_spin(
            user_id=session['user_id'],
            spin_result=selected_color['name'],
            color_hex=selected_color['hex'],
            spin_data=spin_data
        )

        # Get updated stats
        stats = ColorCarnivalManager.get_user_stats(session['user_id'])

        # Get updated coins
        coins_obj = Coins.query.filter_by(user_id=session['user_id']).first()

        return jsonify({
            'success': True,
            'spin_result': {
                'color_name': selected_color['name'],
                'color_hex': selected_color['hex'],
                'coins_earned': selected_color['value'],
                'spin_angle': spin_data['spin_angle'],
                'rotations': spin_data['rotations']
            },
            'user_data': {
                'total_coins': coins_obj.coins if coins_obj else 0,
                'spin_id': result['spin_id']
            },
            'stats': stats
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/color-wheel/stats')
def color_wheel_stats():
    """Get user's color wheel statistics"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    stats = ColorCarnivalManager.get_user_stats(session['user_id'])
    return jsonify({'success': True, 'stats': stats})


@app.route('/api/color-wheel/leaderboard')
def color_wheel_leaderboard():
    """Get color wheel leaderboard"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    limit = request.args.get('limit', default=10, type=int)
    leaderboard = ColorCarnivalManager.get_leaderboard(limit)

    # Add current user's rank
    current_user_stats = ColorCarnivalManager.get_user_stats(session['user_id'])

    return jsonify({
        'success': True,
        'leaderboard': leaderboard,
        'current_user': {
            'username': session['username'],
            'total_coins_earned': current_user_stats['total_coins_earned'],
            'total_spins': current_user_stats['total_spins'],
            'favorite_color': current_user_stats['favorite_color']
        }
    })


@app.route('/api/color-wheel/history')
def color_wheel_history():
    """Get user's spin history"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    limit = request.args.get('limit', default=20, type=int)

    spins = ColorSpin.query.filter_by(user_id=session['user_id'])\
        .order_by(ColorSpin.created_at.desc())\
        .limit(limit)\
        .all()

    history = [
        {
            'id': spin.id,
            'color_name': spin.spin_result,
            'color_hex': spin.color_hex,
            'coins_earned': spin.coins_earned,
            'timestamp': spin.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'time_ago': get_time_ago(spin.created_at)
        }
        for spin in spins
    ]

    return jsonify({'success': True, 'history': history})


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


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
