from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import csv
import os

app = Flask(__name__)

# Define the path to the templates directory
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))

# Function to create the database table if it doesn't exist
def create_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 email TEXT NOT NULL UNIQUE,
                 username TEXT NOT NULL,
                 password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

create_table()

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# Render the signup.html template for the sign-up page
@app.route('/signup', methods=['GET'])
def signup_form():
    return render_template('signup.html')

# Function to handle signup form submission
@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['signupEmail']
    username = request.form['signupUsername']
    password = request.form['signupPassword']
    repeat_password = request.form['signupRepeatPassword']

    # Check if passwords match
    if password != repeat_password:
        return "Passwords do not match. Please try again."

    # Check if email is already registered
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    if c.fetchone():
        conn.close()
        return "Email is already registered. Please use a different email."

    # Insert user data into the database
    c.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, password))
    conn.commit()
    conn.close()

    # Redirect to login page after successful signup
    return redirect(url_for('login_form'))

# Render the login.html template for the login page
@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')

# Function to handle login form submission
@app.route('/login', methods=['POST'])
def login():
    username = request.form['loginUsername']
    password = request.form['loginPassword']

    # Dummy authentication logic (replace with your actual authentication logic)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        # Redirect to index page with username if login is successful
        return redirect(url_for('index', username=username))
    else:
        # Redirect back to login page with an error message
        return redirect(url_for('login_form'))

# Route for the index page with username
@app.route('/index/<username>')
def index(username):
    return f'Welcome, {username}!'

# Function to create the database table if it doesn't exist
def create_admissions_table():
    # Using a context manager to handle database connection
    with sqlite3.connect('admissions.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS admissions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     mhcet_percentile FLOAT NOT NULL,
                     jee_percentile FLOAT NOT NULL,
                     category TEXT NOT NULL)''')
    conn.commit()

create_admissions_table()

# Route to render the admission form
@app.route('/admission', methods=['GET'])
def admission_form():
    return render_template('form.html')

# Route to handle admission form submission
@app.route('/submit', methods=['POST'])
def submit_admission():
    mhcet_percentile = request.form.get('mhcet_percentile')
    jee_percentile = request.form.get('jee_percentile')
    category = request.form.get('category')
    category += 'S' 

    # Insert form data into the admissions table
    conn = sqlite3.connect('admissions.db')
    c = conn.cursor()
    c.execute("INSERT INTO admissions (mhcet_percentile, jee_percentile, category) VALUES (?, ?, ?)",
              (mhcet_percentile, jee_percentile, category))
    conn.commit()
    conn.close()

    # Extract colleges based on user input
    if mhcet_percentile and jee_percentile:
        colleges = extract_colleges_mhcet('data.csv', float(mhcet_percentile), category)
        colleges.extend(extract_colleges_mhcet('data.csv', float(jee_percentile), category))
    elif mhcet_percentile:
        colleges = extract_colleges_mhcet('data.csv', float(mhcet_percentile), category)
    elif jee_percentile:
        colleges = extract_colleges_mhcet('data.csv', float(jee_percentile), category)
    else:
        # No percentiles provided
        return "Please provide MHCET or JEE percentile."

    # Render the result template with the extracted colleges and branches
    return render_template('result.html', colleges=colleges)

# Function to extract colleges based on user input
def extract_colleges_mhcet(csv_file, mhcet_percentile, category):
    colleges = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if float(row['min']) <= mhcet_percentile and row['seat_type'] == category:
                college = {
                    'college_name': row['college_name'],
                    'branch': row['branch']
                }
                colleges.append(college)
    return colleges

def extract_colleges_jee(csv_file, jee_percentile, category):
    colleges = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if float(row['min']) <= jee_percentile and row['seat_type'] == 'AI':
                college = {
                    'college_name': row['college_name'],
                    'branch': row['branch']
                }
                colleges.append(college)
    return colleges

if __name__ == '__main__':
    app.run(port=8000, debug=True)

