from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, QuizResult, Coins, ShapeResult
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_secret_key_change_this'

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------------- HOME ----------------

@app.route('/')
def home():
    return redirect(url_for('login'))


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
    return redirect(url_for('login'))


# ---------------- DASHBOARD ----------------

ACTIVITIES = [
    {"name": "Learn Alphabet", "desc": "A to Z learning", "url": "/alphabet"},
    {"name": "Learn Numbers", "desc": "Fun with numbers", "url": "/numbers"},
    {"name": "Drawing", "desc": "Drawing fun", "url": "/drawing"},
    {"name": "Shape Builder", "desc": "Build shapes", "url": "/shape_builder"},
    {"name": "Smart Quiz", "desc": "Play quiz & earn coins", "url": "/quiz"},
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
    if 'user_id' not in session:
        return redirect(url_for('login'))

    quiz_results = QuizResult.query.filter_by(user_id=session['user_id']).all()
    shape_results = ShapeResult.query.filter_by(user_id=session['user_id']).all()

    quiz_attempts = len(quiz_results)
    quiz_total = sum(r.score for r in quiz_results)
    quiz_avg = round(quiz_total / quiz_attempts, 2) if quiz_attempts else 0

    shape_attempts = len(shape_results)
    shape_total_coins = sum(r.coins_awarded for r in shape_results)
    shape_avg_similarity = round(sum(r.similarity_score for r in shape_results) / shape_attempts, 2) if shape_attempts else 0

    total_coins = quiz_total + shape_total_coins

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

    return render_template('progress.html',
                           total_coins=total_coins,
                           total_avg_score=total_avg_score,
                           performance_level=performance_level,
                           days=days,
                           stars_data=coins_per_day,
                           shape_avg_similarity=shape_avg_similarity,
                           quiz_avg=quiz_avg,
                           quiz_attempts=quiz_attempts,
                           shape_attempts=shape_attempts)

@app.route('/progress-data')
def progress_data():
    if 'user_id' not in session:
        return {"error": "Not logged in"}, 401

    quiz_results = QuizResult.query.filter_by(user_id=session['user_id']).all()
    shape_results = ShapeResult.query.filter_by(user_id=session['user_id']).all()

    quiz_attempts = len(quiz_results)
    quiz_total = sum(r.score for r in quiz_results)
    quiz_avg = round(quiz_total / quiz_attempts, 2) if quiz_attempts else 0

    shape_attempts = len(shape_results)
    shape_total_coins = sum(r.coins_awarded for r in shape_results)
    shape_avg_similarity = round(sum(r.similarity_score for r in shape_results) / shape_attempts, 2) if shape_attempts else 0

    total_coins = quiz_total + shape_total_coins

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


@app.route('/kids_videos', methods=['GET'])
def kids_videos():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    query = request.args.get('q', '').strip()

    # Mock video data for demonstration (replace with actual YouTube API integration)
    mock_videos = [
        {'id': {'videoId': 'dQw4w9WgXcQ'}, 'snippet': {'title': 'Rick Roll'}},
        {'id': {'videoId': '9bZkp7q19f0'}, 'snippet': {'title': 'PSY - GANGNAM STYLE'}},
        {'id': {'videoId': 'kJQP7kiw5Fk'}, 'snippet': {'title': 'Despacito'}},
    ]

    if query:
        # Simple search filter (case-insensitive)
        filtered_videos = [v for v in mock_videos if query.lower() in v['snippet']['title'].lower()]
        if filtered_videos:
            main_video = filtered_videos[0]
            reference_videos = filtered_videos[1:]
        else:
            main_video = None
            reference_videos = []
    else:
        main_video = None
        reference_videos = []

    return render_template('videos.html', query=query, main_video=main_video, reference_videos=reference_videos)

TARGET_SHAPES = {
    "house": {"name": "House 🏠", "required": ["square", "triangle"]},
    "sun": {"name": "Sun ☀️", "required": ["circle", "triangle"]},
    "robot": {"name": "Robot 🤖", "required": ["square", "circle"]},
    "tree": {"name": "Tree 🌳", "required": ["triangle", "square"]},
    "car": {"name": "Car 🚗", "required": ["square", "circle"]}
}

@app.route("/shape_builder", methods=['GET'])
def shape_builder():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    target_key = random.choice(list(TARGET_SHAPES.keys()))
    target = TARGET_SHAPES[target_key]
    return render_template('shape_builder.html', target=target, target_key=target_key)

@app.route("/check_shape", methods=['POST'])
def check_shape():
    if 'user_id' not in session:
        return {"message": "Not logged in"}, 401

    data = request.get_json()
    shapes = data.get('shapes', [])
    target_key = data.get('target', '')

    if target_key  not in TARGET_SHAPES:
        return {"message": "Invalid target", "success": False}

    required = TARGET_SHAPES[target_key]['required']

    if all(r in shapes for r in required):
        # Award 10 coins
        coins_obj = Coins.query.filter_by(user_id=session['user_id']).first()
        if not coins_obj:
            coins_obj = Coins(user_id=session['user_id'], coins=0)
            db.session.add(coins_obj)
        coins_obj.coins += 10
        db.session.commit()

        # Record shape result
        db.session.add(ShapeResult(
            user_id=session['user_id'],
            similarity_score=100,
            coins_awarded=10
        ))
        db.session.commit()

        return {"message": f"Great job! You built the {TARGET_SHAPES[target_key]['name']} and earned 10 coins!", "success": True}
    else:
        # Record failed attempt
        db.session.add(ShapeResult(
            user_id=session['user_id'],
            similarity_score=0,
            coins_awarded=0
        ))
        db.session.commit()

        return {"message": "Not quite right. Try again!", "success": False}

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
