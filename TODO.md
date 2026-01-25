# TODO List for User Database Integration

## Completed Tasks
- [x] Install required packages (flask-sqlalchemy, werkzeug)
- [x] Create models.py with User model (username, email, phone, password_hash, gender, age)
- [x] Update app.py to integrate SQLAlchemy database
- [x] Modify login route: Check if phone exists, if not say "User does not exist. Please sign up first."; if password wrong, say "Incorrect password."
- [x] Modify signin route: Check if phone already exists, if yes say "User already exists. Please login instead."; if not, create user and redirect to login

## Followup Steps
- [ ] Test the application by running it and trying sign up and login scenarios
- [ ] Ensure database file 'users.db' is created in the project directory
