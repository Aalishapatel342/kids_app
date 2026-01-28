from flask import Flask, render_template, request, redirect, url_for, session
import requests
import re# Fixed YouTube API call
from googleapiclient.discovery import build
from models import db, User, QuizResult, Coins

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_secret_key_change_this'

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        user = User.query.filter_by(phone=phone).first()

        if not user:
            return render_template('login.html', error='User does not exist.')

        if not user.check_password(password):
            return render_template('login.html', error='Incorrect password.')

        # Save session
        session['user_id'] = user.id
        session['username'] = user.username
        session['age'] = user.age

        # Redirect by age
        if user.age == '1-4':
            return redirect(url_for('kids_dashboard'))
        else:
            return redirect(url_for('junior_dashboard'))

    return render_template('login.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        gender = request.form['gender']
        age = request.form['age']

        if not (phone.isdigit() and len(phone) == 10 and phone[0] in '6789'):
            return render_template('signin.html', error='Invalid phone number')

        existing_user = User.query.filter(
            (User.phone == phone) |
            (User.email == email) |
            (User.username == username)
        ).first()

        if existing_user:
            return render_template('signin.html', error='User with same phone, email, or username already exists')

        user = User(username=username, email=email, phone=phone, gender=gender, age=age)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()
            return render_template('signin.html', error='Registration failed')

        return redirect(url_for('login'))

    return render_template('signin.html')

@app.route('/kids-dashboard')
def kids_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('age') != '1-4':
        return redirect(url_for('junior_dashboard'))

    user = User.query.get_or_404(session['user_id'])

    return render_template('kids_dashboard.html', username=session.get('username'), gender=user.gender)

@app.route('/junior-dashboard')
def junior_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('age') != '5+':
        return redirect(url_for('kids_dashboard'))

    # Get coins
    coins_obj = Coins.query.filter_by(user_id=session['user_id']).first()
    coins = coins_obj.coins if coins_obj else 0

    user = User.query.get_or_404(session['user_id'])

    return render_template(
        'junior_dashboard.html',
        username=session.get('username'),
        coins=coins,
        gender=user.gender
    )

@app.route('/profile', methods=['GET','POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        user.username = request.form.get('username')
        user.age = request.form.get('age')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')

        db.session.commit()

        session['username'] = user.username
        session['age'] = user.age

        return redirect(url_for('profile'))  # prevent form resubmission

    return render_template('profile.html', user=user)

# Fallback dashboard route to fix old links
@app.route('/dashboard')
def dashboard():
    if 'age' not in session:
        return redirect(url_for('login'))
    if session['age'] == '1-4':
        return redirect(url_for('kids_dashboard'))
    else:
        return redirect(url_for('junior_dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/alphabet")
def alphabet():
    return render_template("alphabet.html")


@app.route("/numbers")
def numbers():
    return render_template("numbers.html")


@app.route("/drawing")
def drawing():
    return render_template("drawing.html")

YOUTUBE_API_KEY = "AIzaSyASa3ZD9H1LpOdVxFRjp4u_H9Xeqrrl7VY"
CHANNEL_ID = "UC4NALVCmcmL5ntpV0thoH6w"

@app.route("/kids_videos")
def kids_videos():
    query = request.args.get("q", "").strip()

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    main_video = None
    reference_videos = []

    if query:
        request_api = youtube.search().list(
            part="snippet",
            q=query,
            channelId=CHANNEL_ID,      # restrict to channel
            type="video",
            maxResults=20,             # fetch more for better filtering
            safeSearch="strict"
        )

        response = request_api.execute()
        items = response.get("items", [])

        # 🔍 Better title-based filtering
        filtered_items = [
            item for item in items
            if query.lower() in item["snippet"]["title"].lower()
        ]

        if filtered_items:
            main_video = filtered_items[0]
            reference_videos = filtered_items[1:]
        elif items:
            # fallback if no exact-ish title match
            main_video = items[0]
            reference_videos = items[1:]

    return render_template(
        "videos.html",
        main_video=main_video,
        reference_videos=reference_videos,
        query=query
    )
    
QUIZ_QUESTIONS = [
    {"question": "5 + 3 = ?", "answer": "8"},
    {"question": "10 - 4 = ?", "answer": "6"},
    {"question": "Spell APPLE", "answer": "apple"}
]

@app.route('/quiz', methods=['GET','POST'])
def quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        score = 0

        for i, q in enumerate(QUIZ_QUESTIONS):
            user_answer = request.form.get(f"q{i}", "").lower()
            if user_answer == q["answer"]:
                score += 1

        # Save score
        db.session.add(QuizResult(user_id=session['user_id'], score=score))

        # Reward coins
        coins = Coins.query.filter_by(user_id=session['user_id']).first()
        if not coins:
            coins = Coins(user_id=session['user_id'], coins=0)

        coins.coins += score * 10

        db.session.add(coins)
        db.session.commit()

        return redirect(url_for('quiz_result'))

    return render_template("quiz.html", questions=QUIZ_QUESTIONS)

@app.route('/quiz-result')
def quiz_result():
    last = QuizResult.query.filter_by(user_id=session['user_id']).order_by(QuizResult.id.desc()).first()
    coins = Coins.query.filter_by(user_id=session['user_id']).first()

    return render_template("quiz_result.html", score=last.score, coins=coins.coins)

@app.route('/progress')
def progress():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    results = QuizResult.query.filter_by(user_id=session['user_id']).all()

    attempts = len(results)
    total_score = sum(r.score for r in results)
    avg = round(total_score / attempts, 2) if attempts else 0

    return render_template("progress.html",
                           attempts=attempts,
                           total=total_score,
                           avg=avg)

CAREERS = [
    {"name": "Doctor", "desc": "Helps sick people"},
    {"name": "Pilot", "desc": "Flies airplanes"},
    {"name": "Engineer", "desc": "Builds machines"},
    {"name": "Teacher", "desc": "Teaches students"},
]

@app.route('/careers')
def careers():
    return render_template("careers.html", careers=CAREERS)

if __name__ == "__main__":
    app.run(debug=True)
