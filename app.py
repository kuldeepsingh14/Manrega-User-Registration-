from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import hashlib
import secrets
import smtplib
from flask_migrate import Migrate 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)


# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_db.sqlite'  # Replace with your database file
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)
# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(15))
    address = db.Column(db.String(200))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(64))

# Email configuration
EMAIL_ADDRESS = 'zolomolokolomolo@gmail.com'  # Sender's email address
EMAIL_PASSWORD = 'ggbd opsm zrby grfg'  # Sender's email password
 
# Function to send registration email
def send_registration_email(username, email, password):
    subject = 'Welcome to Your App'
    message = f'Your login credentials:\nUsername: {username}\nPassword: {password}'
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
    server.quit()

# Welcome route
@app.route('/')
def welcome():
    return "Welcome to the User Registration API"

# Registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    age = data['age']
    email = data['email']
    phone_number = data['phone_number']
    address = data['address']

    # Generate a random username and password
    username = secrets.token_urlsafe(10)
    password = secrets.token_urlsafe(12)

    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Insert the user into the database
    new_user = User(name=name, age=age, email=email, phone_number=phone_number, address=address, username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # Send the registration email
    send_registration_email(username, email, password)

    return jsonify({"message": "Registration successful. Check your email for login credentials."})

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Hash the provided password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Check if the user exists in the database
    user = User.query.filter_by(username=username, password=hashed_password).first()

    if user:
        return jsonify({"message": "Login successful."})
    else:
        return jsonify({"message": "Invalid credentials."})

if __name__ == '__main__':
    app.run(debug=True)
