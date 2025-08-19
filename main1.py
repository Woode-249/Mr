# app.py
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os, json, time, re

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret-in-production')

USERS_FILE = 'users.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except ValueError:
            return []

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

EMAIL_RE = re.compile(r'^[^@]+@[^@]+\.[^@]+$')

@app.route('/')
def auth():
    return render_template('auth.html')

@app.route('/index')
def index():
    user_email = session.get('user')
    user = None
    if user_email:
        users = load_users()
        user = next((u for u in users if u.get('email','').lower()==user_email.lower()), None)
    return render_template('index.html', user=user)

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/plan')
def plan():
    return render_template('plan.html')

@app.route('/profile')
def profile():
    user_email = session.get('user')
    user = None
    if user_email:
        users = load_users()
        user = next((u for u in users if u.get('email','').lower()==user_email.lower()), None)
    return render_template('profile.html', user=user)

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth'))

# ---- API: register/login ----
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    phone = (data.get('phone') or '').strip()
    password = data.get('password') or ''

    if not name:
        return jsonify({'success': False, 'message': 'Name required.'}), 400
    if not EMAIL_RE.match(email):
        return jsonify({'success': False, 'message': 'Invalid email.'}), 400
    if not phone:
        return jsonify({'success': False, 'message': 'Phone required.'}), 400
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password too short.'}), 400

    users = load_users()
    if any(u.get('email','').lower() == email for u in users):
        return jsonify({'success': False, 'message': 'Email already registered.'}), 400

    hashed = generate_password_hash(password)
    user = {
        'id': int(time.time() * 1000),
        'name': name,
        'email': email,
        'phone': phone,
        'password': hashed,
        'created': int(time.time())
    }
    users.append(user)
    save_users(users)

    session['user'] = email
    return jsonify({'success': True, 'redirect': url_for('index')}), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not EMAIL_RE.match(email):
        return jsonify({'success': False, 'message': 'Invalid email.'}), 400
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password too short.'}), 400

    users = load_users()
    user = next((u for u in users if u.get('email','').lower() == email), None)
    if not user or not check_password_hash(user.get('password',''), password):
        return jsonify({'success': False, 'message': 'Invalid credentials.'}), 401

    session['user'] = user['email']
    return jsonify({'success': True, 'redirect': url_for('index')}), 200

if __name__ == '__main__':
    # debug=True فقط أثناء التطوير
    app.run(host='0.0.0.0', port=5000, debug=True)