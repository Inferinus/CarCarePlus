from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, current_app, session, abort, send_from_directory
import requests
from ..Models.models import db, User, Car, MaintenanceLog, VehicleRepair
from .carAPI import get_maintenance_recommendations, get_vin_details, calculate_costs

# Blueprint for the api part of the application
views_blueprint = Blueprint('views', __name__)


@views_blueprint.route('/maintenance_info')
def maintenance_info():
    vin = request.args.get('vin')
    mileage = request.args.get('mileage')

    user_id = session.get('user_id')  # This retrieves the user ID from the session
    if user_id is None:
        # If there's no user_id in session, it means the user is not logged in
        return jsonify({"error": "User not logged in"}), 401

    # Use user_id directly since it is an integer
    car = Car.query.filter_by(user_id=user_id, vin=vin).first()
    if car is None:
        return jsonify({"error": "Vehicle not found or does not belong to user"}), 404
    
    # Future work: Perform a check if mileage is within a reasonable range if needed
    
    api_key = current_app.config['CARMD_API_KEY']
    headers = {
            'content-type': 'application/json',
            'authorization': f"Basic {api_key}",
            'partner-token': current_app.config['CARMD_PARTNER_TOKEN']
        }

    try:
        response = requests.get(f"http://api.carmd.com/v3.0/maint?vin={vin}&mileage={mileage}", headers=headers)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
        return jsonify({"error": "HTTP Error"}), errh.response.status_code
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
        return jsonify({"error": "Error Connecting"}), 503
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
        return jsonify({"error": "Timeout Error"}), 504
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
        return jsonify({"error": "Error"}), 500

    # If everything goes well, return the JSON from the API
    return jsonify(response.json())

@views_blueprint.route('/decode_vin', methods=['POST'])
def decode_vin():
    vin = request.form['vin']
    owner_id = request.form['owner_id']  # assuming the owner_id is sent in the form

    # Find the car by VIN and owner_id
    car = Car.query.filter_by(vin=vin, owner_id=owner_id).first()

    response = get_vin_details(vin)

    if response.status_code == 200:
        data = response.json()['data']

        if car:
            # The car exists, update its attributes
            car.year = data['year']
            car.make = data['make']
            car.model = data['model']
            car.manufacturer = data['manufacturer']
            car.engine = data['engine']
            car.trim = data['trim']
            car.transmission = data['transmission']
            action = 'updated'
        else:
            # No car found, create a new car object
            car = Car(
                vin=vin,
                year=data['year'],
                make=data['make'],
                model=data['model'],
                manufacturer=data['manufacturer'],
                engine=data['engine'],
                trim=data['trim'],
                transmission=data['transmission'],
                owner_id=owner_id
            )
            db.session.add(car)
            action = 'created'

        try:
            db.session.commit()
            return jsonify({'success': f'Car {action} successfully.', 'data': data}), 200
        except Exception as e:  # Catch any exception that may occur
            db.session.rollback()
            flash('An error occurred while decoding the VIN. Please try again.', 'error')
    else:
        return jsonify({'error': 'Failed to decode VIN'}), response.status_code

@views_blueprint.route('/maintenance', methods=['GET', 'POST'])
def maintenance():
    if request.method == 'POST':
        vin = request.form.get('vin')
        year = request.form.get('year')
        make = request.form.get('make')
        model = request.form.get('model')
        unit = request.form.get('unit')  # Optional, based on user's preference or your application requirement

        # Check if the necessary information is provided
        if not vin and not all([year, make, model]):
            # Respond with an error if neither VIN nor year/make/model are provided
            return jsonify({'error': 'Please provide VIN or year, make, and model information.'}), 400
        
        # Get maintenance recommendations using the provided details
        recommendations = get_maintenance_recommendations(vin=vin, year=year, make=make, model=model, unit=unit)

        if recommendations is not None:
            # Parse the recommendations to include detailed information
            detailed_recommendations = []
            for item in recommendations:
                # Initialize parts_cost to 0, this will also cover the scenario where item['parts'] is None
                parts_cost = 0
                # Check if 'parts' is in the item and it is not None
                if item.get('parts'):
                    parts_cost = sum(part['price'] * part['qty'] for part in item['parts'])
                
                # Combine it with other costs
                total_cost = parts_cost + item['repair']['labor_cost'] + item['repair']['misc_cost']
                parsed_item = {
                    'description': item['desc'],
                    'due_mileage': item['due_mileage'],
                    'parts': item.get('parts', []),
                    'repair_difficulty': item['repair']['repair_difficulty'],
                    'repair_hours': item['repair']['repair_hours'],
                    'labor_rate_per_hour': item['repair']['labor_rate_per_hour'],
                    'total_parts_cost': parts_cost,
                    'labor_cost': item['repair']['labor_cost'],
                    'misc_cost': item['repair']['misc_cost'],
                    'total_cost': total_cost
                }
                detailed_recommendations.append(parsed_item)

            # If data is retrieved successfully, render the maintenance recommendations template
            return render_template('maintenance_recommendations.html', recommendations=detailed_recommendations)
        else:
            # If there was an error or no data could be retrieved, respond with an error
            return jsonify({'error': 'Failed to retrieve maintenance recommendations.'}), 500
    else:  # GET request
        # Render the maintenance form template (or whatever template you use to collect the VIN/year/make/model)
        return render_template('maintenance_form.html')

@views_blueprint.route('/get_car_maintenance', methods=['GET'])
def get_car_maintenance():
    # Extract query parameters from the request
    vin = request.args.get('vin')
    year = request.args.get('year')
    make = request.args.get('make')
    model = request.args.get('model')
    unit = request.args.get('unit')

    # Get the maintenance recommendations data from CarMD API
    car_maintenance_data = get_maintenance_recommendations(vin=vin, year=year, make=make, model=model, unit=unit)

    if car_maintenance_data:
        # Assuming `car_maintenance_data` is the variable that has the JSON response from CarMD API
        # Calculate costs
        total_parts_cost, total_labor_cost, overall_total_cost = calculate_costs(car_maintenance_data)

        # Build the response object
        response = {
            "total_parts_cost": total_parts_cost,
            "total_labor_cost": total_labor_cost,
            "overall_total_cost": overall_total_cost,
            # You can add the original car maintenance data or any other additional data here if needed
            "car_maintenance_data": car_maintenance_data  
        }
    else:
        # Handle the case where no data is returned
        response = {
            "error": "Could not retrieve car maintenance data.",
            "total_parts_cost": 0,
            "total_labor_cost": 0,
            "overall_total_cost": 0,
        }

    # Send JSON response
    return jsonify(response)

@views_blueprint.route('/upcoming_repairs', methods=['GET'])
def get_upcoming_repairs():
    vin = request.args.get('vin')
    mileage = request.args.get('mileage')
    unit = request.args.get('unit')

    if not vin or not mileage:
        return jsonify({'error': 'VIN and Mileage are required parameters'}), 400

    # Construct the URL and include the unit if it's provided
    url = f"http://api.carmd.com/v3.0/upcoming?vin={vin}&mileage={mileage}"
    if unit:
        url += f"&unit={unit}"

    headers = {
        'content-type': "application/json",
        'authorization': current_app.config['CARMED_AUTHORIZATION_KEY'],
        'partner-token': current_app.config['CARMED_PARTNER_TOKEN']
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        upcoming_repairs = response.json().get('data', [])
        return jsonify(upcoming_repairs), 200
    else:
        return jsonify({'error': 'Failed to get upcoming repairs', 'message': response.text}), response.status_code

@views_blueprint.route('/repair', methods=['GET'])
def get_repair():
    vin = request.args.get('vin')
    mileage = request.args.get('mileage')
    dtc = request.args.get('dtc')
    unit = request.args.get('unit', 'mi')  # Default unit is 'mi' for miles

    if not vin or not mileage or not dtc:
        return jsonify({'error': 'VIN, Mileage, and DTC are required parameters'}), 400

    headers = {
        'content-type': "application/json",
        'authorization': current_app.config['CARMED_AUTHORIZATION_KEY'],
        'partner-token': current_app.config['CARMED_PARTNER_TOKEN']
    }

    # Construct the URL with the parameters
    url = f"http://api.carmd.com/v3.0/repair?vin={vin}&mileage={mileage}&dtc={dtc}"
    if unit:  # Include the unit if it's provided
        url += f"&unit={unit}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        repair_data = response.json().get('data', [])
        return jsonify(repair_data), 200
    else:
        return jsonify({'error': 'Failed to get repair information', 'message': response.text}), response.status_code
    
@views_blueprint.route('/add-repair-info', methods=['POST'])
def add_repair_info():
    data = request.json
    car_id = data.get('car_id')
    dtc_code = data.get('dtc_code')
    description = data.get('description')
    repair_urgency = data.get('repair_urgency')
    repair_difficulty = data.get('repair_difficulty')
    parts_needed = data.get('parts_needed')
    labor_hours = data.get('labor_hours')
    total_cost = data.get('total_cost')

    # Verify that the car exists
    car = Car.query.get(car_id)
    if car is None:
        return jsonify({'error': 'Car not found'}), 404

    # Create a new VehicleRepair instance
    vehicle_repair = VehicleRepair(
        car_id=car_id,
        dtc_code=dtc_code,
        description=description,
        repair_urgency=repair_urgency,
        repair_difficulty=repair_difficulty,
        parts_needed=parts_needed,
        labor_hours=labor_hours,
        total_cost=total_cost,
    )

    # Add to the session and commit to the database
    db.session.add(vehicle_repair)
    db.session.commit()

    return jsonify({'message': 'Repair information added successfully'}), 201

@views_blueprint.route('/get_diagnostics', methods=['GET'])
def get_diagnostics():
    # Get parameters from the query string
    vin = request.args.get('vin')
    mileage = request.args.get('mileage')
    dtc = request.args.get('dtc')  # Make sure this is required by the API
    unit = request.args.get('unit', 'mi')  # Default unit is 'mi' for miles

    # Validate required parameters
    if not vin or not mileage or not dtc:
        return jsonify({'error': 'VIN, Mileage, and DTC are required parameters'}), 400

    # Setup the headers with your API keys and content type
    headers = {
        'content-type': 'application/json',
        'authorization': f"Basic {current_app.config['CARMD_API_KEY']}",
        'partner-token': current_app.config['CARMD_PARTNER_TOKEN']
    }

    # CarMD API endpoint
    url = "http://api.carmd.com/v3.0/diag"
    
    # Setup the parameters for the GET request
    params = {
        'vin': vin,
        'mileage': mileage,
        'dtc': dtc,
        'unit': unit
    }

    # Output the final request URL and headers for debugging
    print(f"Requesting URL: {url}")
    print(f"Request Headers: {headers}")
    print(f"Request Parameters: {params}")

    try:
        # Make the GET request with parameters and headers
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        
        # Parse and return the JSON response
        diagnostic_data = response.json().get('data', [])
        return jsonify(diagnostic_data), 200

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
        print(f"Response Text: {errh.response.text}")
        return jsonify({'error': 'HTTP Error', 'message': errh.response.text}), errh.response.status_code
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
        return jsonify({'error': 'Error Connecting'}), 503
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
        return jsonify({'error': 'Timeout Error'}), 504
    except requests.exceptions.RequestException as err:
        print(f"Oops: Something Else: {err}")
        return jsonify({'error': 'Error'}), 500
    finally:
        # Outputting response headers and content if available
        if response:
            print(f"Response Headers: {response.headers}")
            print(f"API Response: {response.text}")