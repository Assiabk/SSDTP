from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/flask_auth'
mongo = PyMongo(app)

def generate_post_id():
    return len(list(mongo.db.posts.find())) + 1

def generate_comment_id():
    return len(list(mongo.db.comments.find())) + 1

@app.route('/')
def home():
    return render_template('register.html')

@app.route('/profile')
def profile():
    user_id = session.get('user_id')

    if user_id:
        db = mongo.db.users
        user_info = db.find_one({"_id": ObjectId(user_id)})

        if user_info:
            return render_template('profile.html', user_info=user_info)
        else:
            flash('User not found.', 'error')
    else:
        flash('You need to log in to view your profile.', 'error')

    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        birthdate = request.form.get('birthdate')
        location = request.form.get('location')
        is_admin = request.form.get('is_admin') == 'on'

        db = mongo.db.users

        existing_user = db.find_one({"$or": [{"username": username}, {"email": email}]})
        if existing_user:
            flash('Username or email is already taken.', 'error')
            return redirect(url_for('home'))

        hashed_password = generate_password_hash(password)
        new_user = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "birthdate": datetime.strptime(birthdate, "%Y-%m-%d"),
            "location": location,
            "is_admin": is_admin
        }

        db.insert_one(new_user)
        flash('Registration successful. You can now log in.', 'success')

        if is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    posts = mongo.db.posts.find()
    users = mongo.db.users.find()
    return render_template('admin_dashboard.html', posts=posts, users=users)

@app.route('/admin_dashboard/create_user', methods=['POST'])
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        birthdate = request.form.get('birthdate')
        location = request.form.get('location')
        is_admin = 'is_admin' in request.form

        db = mongo.db.users

        existing_user = db.find_one({"$or": [{"username": username}, {"email": email}]})
        if existing_user:
            flash('Username or email is already taken.', 'error')
        else:
            hashed_password = generate_password_hash(password)
            new_user = {
                "username": username,
                "email": email,
                "password": hashed_password,
                "birthdate": datetime.strptime(birthdate, "%Y-%m-%d"),
                "location": location,
                "is_admin": is_admin
            }

            db.insert_one(new_user)
            flash('User created successfully!', 'success')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard/update_user/<user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    db = mongo.db.users
    user_info = db.find_one({"_id": ObjectId(user_id)})

    if request.method == 'POST':
        new_username = request.form.get('new_username')
        new_email = request.form.get('new_email')

        db.update_one({"_id": ObjectId(user_id)}, {"$set": {"username": new_username, "email": new_email}})
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_dashboard_update_user.html', user_info=user_info)

@app.route('/admin_dashboard/delete_user/<user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    db = mongo.db.users
    user_info = db.find_one({"_id": ObjectId(user_id)})

    if request.method == 'POST':
        db.delete_one({"_id": ObjectId(user_id)})
        flash('User deleted successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_dashboard_delete_user.html', user_info=user_info)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        db = mongo.db.users

        user = db.find_one({"email": email})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            
            if user.get('is_admin', False):
                flash('Login successful. Welcome Admin!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Login successful. Welcome!', 'success')
                return redirect(url_for('main_page'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/main_page', methods=['GET', 'POST'])
def main_page():
    if 'user_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_posts_cursor = mongo.db.posts.find({"user_id": user_id})
    user_posts = list(user_posts_cursor)

    comments = {}

    if request.method == 'POST':
        if 'add_post' in request.form:
            post_title = request.form.get('post_title')
            post_content = request.form.get('post_content')

            post_id = generate_post_id()
            mongo.db.posts.insert_one({'id': post_id, 'user_id': user_id, 'title': post_title, 'content': post_content})

            flash('Post created successfully!', 'success')
            return redirect(url_for('main_page'))

        elif 'add_comment' in request.form:
            post_id = request.form.get('post_id')
            comment_text = request.form.get('comment_text')

            comment_id = generate_comment_id()

            # Insert the new comment into the 'comments' collection
            mongo.db.comments.insert_one({
                'id': comment_id,
                'post_id': post_id,
                'user_id': user_id,
                'text': comment_text
            })

            flash('Comment added successfully!', 'success')
            return redirect(url_for('main_page'))

    return render_template('main_page.html', user_posts=user_posts, comments=comments)

@app.route('/admin_dashboard/create_post', methods=['POST'])
def create_post():
    if request.method == 'POST':
        user_id = session.get('user_id')
        post_title = request.form.get('post_title')
        post_content = request.form.get('post_content')

        post_id = generate_post_id()

        mongo.db.posts.insert_one({
            'id': post_id,
            'user_id': user_id,
            'title': post_title,
            'content': post_content
        })

        flash('Post created successfully!', 'success')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard/update_post/<post_id>', methods=['GET', 'POST'])
def update_post(post_id):
    db = mongo.db.posts
    post_info = db.find_one({"id": int(post_id)})

    if request.method == 'POST':
        new_title = request.form.get('new_title')
        new_content = request.form.get('new_content')

        db.update_one({"id": int(post_id)}, {"$set": {"title": new_title, "content": new_content}})
        flash('Post updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_dashboard_update_post.html', post_info=post_info)

@app.route('/admin_dashboard/delete_post/<post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    db = mongo.db.posts
    post_info = db.find_one({"id": int(post_id)})

    if request.method == 'POST':
        db.delete_one({"id": int(post_id)})
        flash('Post deleted successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_dashboard_delete_post.html', post_info=post_info)

if __name__ == '__main__':
    app.run(debug=True)
