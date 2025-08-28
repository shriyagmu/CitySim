import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash
from game_logic import CitySimulation

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key_change_in_production")

def get_city():
    """Get or create city simulation from session"""
    if 'city_data' not in session:
        # Initialize new city
        city = CitySimulation()
        session['city_data'] = city.to_dict()
    else:
        # Load existing city
        city = CitySimulation.from_dict(session['city_data'])
    return city

def save_city(city):
    """Save city simulation to session"""
    session['city_data'] = city.to_dict()
    session.modified = True

@app.route('/')
def index():
    """Main game page"""
    city = get_city()
    return render_template('index.html', city=city)

@app.route('/zone', methods=['POST'])
def zone_land():
    """Zone a specific cell"""
    city = get_city()
    
    try:
        row = int(request.form.get('row'))
        col = int(request.form.get('col'))
        zone_type = request.form.get('zone_type')
        
        if city.zone_land(row, col, zone_type):
            flash(f'Successfully zoned cell ({row}, {col}) as {zone_type}', 'success')
        else:
            flash(f'Cannot zone cell ({row}, {col}) - cell may already be occupied', 'error')
            
        save_city(city)
    except (ValueError, TypeError) as e:
        flash('Invalid zoning parameters', 'error')
    
    return redirect(url_for('index'))

@app.route('/build', methods=['POST'])
def build_structure():
    """Build a structure on a specific cell"""
    city = get_city()
    
    try:
        row = int(request.form.get('row'))
        col = int(request.form.get('col'))
        building_type = request.form.get('building_type')
        
        if city.build_structure(row, col, building_type):
            flash(f'Successfully built {building_type} at cell ({row}, {col})', 'success')
        else:
            flash(f'Cannot build {building_type} at cell ({row}, {col}) - cell may already be occupied', 'error')
            
        save_city(city)
    except (ValueError, TypeError) as e:
        flash('Invalid building parameters', 'error')
    
    return redirect(url_for('index'))

@app.route('/advance_time', methods=['POST'])
def advance_time():
    """Advance the city by one year"""
    city = get_city()
    city.advance_year()
    save_city(city)
    flash(f'Advanced to year {city.current_year}', 'info')
    return redirect(url_for('index'))

@app.route('/reset', methods=['POST'])
def reset_city():
    """Reset the city to initial state"""
    session.pop('city_data', None)
    flash('City has been reset', 'info')
    return redirect(url_for('index'))

@app.route('/clear_cell', methods=['POST'])
def clear_cell():
    """Clear a specific cell"""
    city = get_city()
    
    try:
        row = int(request.form.get('row'))
        col = int(request.form.get('col'))
        
        if city.clear_cell(row, col):
            flash(f'Successfully cleared cell ({row}, {col})', 'success')
        else:
            flash(f'Cell ({row}, {col}) is already empty', 'info')
            
        save_city(city)
    except (ValueError, TypeError) as e:
        flash('Invalid cell parameters', 'error')
    
    return redirect(url_for('index'))
