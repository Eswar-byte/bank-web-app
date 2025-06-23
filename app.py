from flask import Flask, render_template, request, redirect, url_for, session
import json, os

app = Flask(__name__)
app.secret_key = 'change_this_to_a_secret_key'
DATA_FILE = 'accounts.json'

def load_users():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
    with open(DATA_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = load_users()
        name, pin = request.form['name'], request.form['pin']
        accNo = 1000 + len(users)
        users.append({"name": name, "pin": pin, "accNo": accNo, "balance": 0})
        save_users(users)
        return render_template('signup.html', message=f"Account created! Your account number is {accNo}")
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        accNo = int(request.form['accNo'])
        pin = request.form['pin']
        for u in load_users():
            if u["accNo"] == accNo and u["pin"] == pin:
                session['user'] = u
                return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials!")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        users = load_users()
        for u in users:
            if u['accNo'] == user['accNo']:
                action = request.form['action']
                amount = float(request.form['amount'])
                if action == 'deposit':
                    u['balance'] += amount
                elif action == 'withdraw':
                    if u['balance'] >= amount:
                        u['balance'] -= amount
                    else:
                        return render_template('dashboard.html', user=u, error="Insufficient funds")
                save_users(users)
                session['user'] = u
                break

    return render_template('dashboard.html', user=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
