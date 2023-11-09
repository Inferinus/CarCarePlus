import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models.models import db, User, Car, MaintenanceLog
from flask_migrate import Migrate

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carcareplus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'capstone2023'

db.init_app(app)

migrate = Migrate(app, db) # initializes Flask-Migrate and links it to the app and database.

with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        error_message = None

         # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # Notify user that email is already in use.
            flash('Email already in use. Please choose another email or log in.', 'error')
            return redirect(url_for('register'))
        
        if not username or not email or not password:
            error_message = 'Username, Email, and Password are required!'
        elif User.query.filter_by(username=username).first():
            error_message = f"User {username} is already registered."

        if error_message is None:
            new_user = User(username=username, email=email)
            new_user.password = password
            db.session.add(new_user)
            db.session.commit()
            flash("You have successfully registered!", "success")
            return redirect(url_for('login'))

        flash(error_message, "error")

    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.verify_password(password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))

        flash('Invalid Credentials. Please try again.', 'error')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)
    if user is None:
        session.clear()
        return redirect(url_for('login'))

    cars = Car.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', user=user, cars=cars)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        make = request.form.get('make')
        model = request.form.get('model')
        year = request.form.get('year')
        user_id = session['user_id']

        new_car = Car(make=make, model=model, year=year, user_id=session['user_id'])
        db.session.add(new_car)
        db.session.commit()

        flash('Your car has been added successfully.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_car.html')

@app.route('/edit_car/<int:id>', methods=['GET', 'POST'])
def edit_car(id):
    car = Car.query.get_or_404(id)

    if car.user_id != session.get('user_id'):
        abort(403)

    if request.method == 'POST':
        car.make = request.form['make']
        car.model = request.form['model']
        car.year = request.form['year']
        car.vin = request.form['vin']

        db.session.commit()
        flash('Car updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_car.html', car=car)

@app.route('/delete_car/<int:id>', methods=['POST'])
def delete_car(id):
    car = Car.query.get_or_404(id)

    if car.user_id != session.get('user_id'):
        abort(403)

    db.session.delete(car)
    db.session.commit()
    flash('Car deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
