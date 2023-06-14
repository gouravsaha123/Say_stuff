from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set your own secret key

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('messages', lazy=True))


# Home page
@app.route('/')
def home():
    if 'username' in session:
        return redirect('/chat')
    return render_template('index.html')


# Sign up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return render_template('signup.html', error='Username already exists')
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
    return render_template('signup.html')


# Log in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect('/chat')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


# Log out
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


# Chat page
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        message_content = request.form['message']
        if message_content:
            user_id = session['user_id']
            user = User.query.get(user_id)
            new_message = Message(content=message_content, user=user)
            db.session.add(new_message)
            db.session.commit()
        return redirect('/chat')
    messages = Message.query.order_by(Message.id.asc()).all()
    return render_template('chat.html', messages=messages)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
