from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for,
)
app = Flask(__name__)

# Dummy database for demonstration purposes
users = {'admin': 'admin_password', 'visitor': 'visitor_password'}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username contains only letters
        if username.isalpha():
            if username in users and users[username] == password:
                return redirect(url_for('visitor_home'))
            else:
                return render_template('login.html', error='Invalid credentials for visitor.')
        # Check if the username contains both letters and numbers
        elif username.isalnum():
            if username in users and users[username] == password:
                return redirect(url_for('admin_home'))
            else:
                return render_template('login.html', error='Invalid credentials for admin.')
        else:
            return render_template('login.html', error='Invalid username format.')

    return render_template('login.html', error=None)

@app.route('/visitor_home')
def visitor_home():
    return jsonify({'msg': 'Welcome, Visitor!'}) 

@app.route('/admin_home')
def admin_home():
    return jsonify({'msg': 'Welcome, Admin!'}) 

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)