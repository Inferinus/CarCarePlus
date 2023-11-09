import requests
from flask import current_app

def get_maintenance_recommendations(vin=None, year=None, make=None, model=None, unit=None):
    try:
        api_key = current_app.config['CARMD_API_KEY']
        headers = {
            'content-type': 'application/json',
            'authorization': f"Basic {api_key}",
            'partner-token': current_app.config['CARMD_PARTNER_TOKEN']
        }
        
        if vin:
            url = f"http://api.carmd.com/v3.0/maintlist?vin={vin}"
            if unit:
                url += f"&unit={unit}"
        elif all([year, make, model]):
            url = f"http://api.carmd.com/v3.0/maintlist?year={year}&make={make}&model={model}"
            if unit:
                url += f"&unit={unit}"
        else:
            return None
        
        response = requests.get(url, headers=headers)
        
        if response.ok:
            return response.json()['data']
        else:
            current_app.logger.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        current_app.logger.exception("Failed to retrieve maintenance recommendations")
        return None


def get_vin_details(vin):
    headers = {
        'content-type': 'application/json',
        'authorization': current_app.config['CARMED_AUTHORIZATION_KEY'],
        'partner-token': current_app.config['CARMED_PARTNER_TOKEN']
    }
    
    # Define the URL for the request
    url = f"{current_app.config['CARMED_API_BASE_URL']}decode?vin={vin}"
    
    # Make the request and return the response
    return requests.get(url, headers=headers)

def calculate_costs(car_maintenance_data):
    total_parts_cost = 0
    total_labor_cost = 0

    for maintenance_item in car_maintenance_data:
        # Calculate parts cost
        parts = maintenance_item.get('parts', [])
        for part in parts:
            part_price = part.get('price', 0)
            total_parts_cost += part_price

        # Calculate labor cost
        labor = maintenance_item.get('labor', [])
        for labor_item in labor:
            labor_price = labor_item.get('price', 0)
            total_labor_cost += labor_price

    # Calculate the overall total cost
    overall_total_cost = total_parts_cost + total_labor_cost

    return total_parts_cost, total_labor_cost, overall_total_cost
