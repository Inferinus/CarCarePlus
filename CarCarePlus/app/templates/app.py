import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carcareplus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define models (e.g., User, Car, MaintenanceLog)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Add additional fields/relationships

# Add other models (Car, MaintenanceLog, etc.) here

@app.route('/')
def home():
    return "Welcome to CarCare+!"

if __name__ == '__main__':
    db.create_all()  # Create database tables
    app.run(debug=True)