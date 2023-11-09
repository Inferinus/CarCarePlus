import requests, logging
from flask import render_template, request, redirect, url_for, flash, session, abort, Blueprint, current_app, Response, send_from_directory, jsonify
from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError
from ..Models.models import db, User, Car
from .carAPI import get_vin_details, get_maintenance_recommendations


app_blueprint = Blueprint('app_blueprint', __name__)

@app_blueprint.route('/engineCheck')
def engine_check():
    return render_template('engine_check.html')

@app_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        error_message = None

        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already in use. Please choose another email or log in.', 'error')
            return redirect(url_for('app_blueprint.register'))
        
        if not username or not email or not password:
            error_message = 'Username, Email, and Password are required!'
        elif User.query.filter_by(username=username).first():
            error_message = f"User {username} is already registered."

        if error_message is None:
            new_user = User(username=username, email=email)
            new_user.password = password  # This will call the setter method
            db.session.add(new_user)
            db.session.commit()
            flash("You have successfully registered!", "success")
            return redirect(url_for('app_blueprint.login'))

        flash(error_message, "error")

    return render_template('register.html')


@app_blueprint.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('app_blueprint.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        # Use the verify_password method instead of directly accessing the password
        if user and user.verify_password(password):
            session['user_id'] = user.id
            session['username'] = username
            return redirect(url_for('app_blueprint.dashboard'))

        flash('Invalid Credentials. Please try again.', 'error')

    return render_template('login.html')
    


@app_blueprint.route('/dashboard')
def dashboard():
    # Check if user_id is in session, redirect if not
    if 'user_id' not in session:
        return redirect(url_for('app_blueprint.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    username = session.get('username')
    
    # If either user or username is None, clear the session and redirect to login
    if not user or not username:
        session.clear()
        return redirect(url_for('app_blueprint.login'))

    cars = Car.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', user=user, cars=cars, username=username)

@app_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('app_blueprint.login'))

@app_blueprint.route('/add_car', methods=['GET', 'POST'])
def add_car():
    if 'user_id' not in session:
        return redirect(url_for('app_blueprint.login'))

    if request.method == 'POST':
        # Retrieve form data
        make = request.form.get('make')
        model = request.form.get('model')
        year = request.form.get('year')
        mileage = request.form.get('mileage')
        vin = request.form.get('vin')
        user_id = session['user_id']

        # Create a new car object (assuming you have a Car model defined)
        new_car = Car(make=make, model=model, year=year, mileage=mileage, vin=vin, user_id=user_id)

        # Add and commit the new car to the database
        try:
            db.session.add(new_car)
            db.session.commit()
            flash('Your car has been added successfully.', 'success')
            return redirect(url_for('app_blueprint.dashboard'))
        except Exception as e:
            # Log the exception and roll back the session in case of an error
            current_app.logger.error(f'Error adding car: {e}')
            db.session.rollback()
            flash('An error occurred while adding the car. Please check your input.', 'error')

    # Render the add_car page for GET requests or failed POST requests
    return render_template('add_car.html')


@app_blueprint.route('/edit_car/<int:id>', methods=['GET', 'POST'])
def edit_car(id):
    car = Car.query.get_or_404(id)

    if car.user_id != session.get('user_id'):
        abort(403)

    if request.method == 'POST':
        car.make = request.form['make']
        car.model = request.form['model']
        car.year = request.form['year']
        car.mileage = request.form['mileage']
        car.vin = request.form['vin']

        db.session.commit()
        flash('Car updated successfully!', 'success')
        return redirect(url_for('app_blueprint.dashboard'))

    return render_template('edit_car.html', car=car)

@app_blueprint.route('/delete_car/<int:id>', methods=['POST'])
def delete_car(id):
    car = Car.query.get_or_404(id)

    if car.user_id != session.get('user_id'):
        abort(403)

    db.session.delete(car)
    db.session.commit()
    flash('Car deleted successfully!', 'success')
    return redirect(url_for('app_blueprint.dashboard'))

@app_blueprint.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('You need to login first.', 'error')
        return redirect(url_for('app_blueprint.login'))

    user_id = session['user_id']
    user = User.query.get(user_id)
    if user is None:
        flash('User not found.', 'error')
        return redirect(url_for('app_blueprint.login'))

    return render_template('profile.html', user=user)

@app_blueprint.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        flash('You need to be logged in to update your profile.', 'error')
        return redirect(url_for('app_blueprint.login'))

    user_id = session['user_id']
    user = User.query.get(user_id)
    if user is None:
        flash('User not found.', 'error')
        return redirect(url_for('app_blueprint.login'))

    current_password = request.form['current_password']
    new_password = request.form['new_password']

    if not user.verify_password(current_password):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('app_blueprint.profile'))

    if not new_password:
        flash('New password must not be empty.', 'error')
        return redirect(url_for('app_blueprint.profile'))
    
    user.password = new_password
    db.session.commit()

    flash('Your password has been updated.', 'success')
    return redirect(url_for('app_blueprint.profile'))

#@app_blueprint.route('/vehicles')
#def vehicles():
    if 'user_id' not in session:
        return redirect(url_for('app_blueprint.login'))

    user_id = session['user_id']
    # Assuming you have a User model with a one-to-many relationship to a Car model
    user = User.query.get(user_id)
    if user is None:
        # handle user not found, maybe logout and redirect to login
        flash('User not found.', 'error')
        return redirect(url_for('app_blueprint.login'))

    cars = user.cars  # This will get all the cars related to the user
    # Now, you would render a template, passing in the cars
    return render_template('vehicle_detail.html', cars=cars)

@app_blueprint.route('/api/vehicles')
def api_vehicles():
    if 'user_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401  # or some other appropriate response

    user_id = session['user_id']
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    cars = user.cars  # Assuming user.cars returns the list of cars
    car_list = [{
        'make': car.make,
        'model': car.model,
        'year': car.year,
        'vin': car.vin
        # include other car details as necessary
    } for car in cars]

    return jsonify(car_list)

logging.basicConfig(level=logging.DEBUG)

@app_blueprint.route('/vehicle_image/<vin>')
def vehicle_image(vin):
    logging.debug(f"Fetching image for VIN: {vin}")

    # API endpoint with the provided VIN
    api_url = f"http://api.carmd.com/v3.0/image?vin={vin}"

    # Headers including API key and partner token from the Flask app config
    headers = {
        'content-type': 'application/json',
        'authorization': f"Basic {current_app.config['CARMD_API_KEY']}",
        'partner-token': current_app.config['CARMD_PARTNER_TOKEN']
    }

    try:
        # Making a GET request to the API
        response = requests.get(api_url, headers=headers)
        
        # If the response has an HTTP 200 status code, an image was successfully fetched
        if response.status_code == 200:
            response_json = response.json()
            # Check if the 'data' field is in the JSON response and it has an 'image' field
            if 'data' in response_json and 'image' in response_json['data'][0]:
                image_url = response_json['data'][0]['image']
                logging.debug(f"Image URL fetched for VIN {vin}: {image_url}")
                # Return the image URL in a JSON response
                return jsonify({'image_url': image_url})
            else:
                # If the 'data' or 'image' field is not present, log the failure and return an error message
                logging.error(f"No image URL in response for VIN: {vin}")
                return jsonify({'error': 'No image found in response'}), 404
        else:
            # If the response code is not 200, log the failure and return an error message
            logging.error(f"Failed to fetch image for VIN: {vin}, Status Code: {response.status_code}")
            return jsonify({'error': 'Failed to fetch image from CarMD'}), response.status_code

    # Handling exceptions that may occur during the request to the external API
    except Exception as e:
        logging.error(f"Exception occurred while fetching image for VIN: {vin}, Error: {str(e)}")
        # Return a server error status code (500) since this is an unexpected condition
        return jsonify({'error': 'An error occurred while fetching the image'}), 500