from flask import Flask, render_template, request, redirect, session
from datetime import timedelta
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Set session timeout to 30 minutes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['flask_auth_example']
users_collection = db['users']

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        
        # Check if username already exists
        if users_collection.find_one({'username': username}):
            return "Username already exists!"
        
        # Insert new user into database
        users_collection.insert_one({'username': username, 'password': hashed_password})
        return redirect('/login')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        
        user = users_collection.find_one({'username': username})
        
        if user and bcrypt.checkpw(password, user['password']):
            session['username'] = username
            return redirect('/home')
        else:
            return "Invalid username or password"
    
    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
