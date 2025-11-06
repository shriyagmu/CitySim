import os
import logging
from datetime import datetime
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
            cost = city.get_building_cost(zone_type)
            flash(f'Successfully zoned cell ({row}, {col}) as {zone_type} for ${cost}', 'success')
            
            # Check for new achievements
            recent_achievements = city.get_recent_achievements(1)
            if recent_achievements and recent_achievements[-1]['year'] == city.current_year:
                achievement = recent_achievements[-1]
                flash(f'🏆 Achievement Unlocked: {achievement["icon"]} {achievement["name"]} - {achievement["description"]}', 'info')
        else:
            if not city.can_afford(zone_type):
                cost = city.get_building_cost(zone_type)
                flash(f'Cannot zone cell ({row}, {col}) - insufficient funds! Need ${cost}, have ${city.money}', 'error')
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
            cost = city.get_building_cost(building_type)
            flash(f'Successfully built {building_type} at cell ({row}, {col}) for ${cost}', 'success')
            
            # Check for new achievements
            recent_achievements = city.get_recent_achievements(1)
            if recent_achievements and recent_achievements[-1]['year'] == city.current_year:
                achievement = recent_achievements[-1]
                flash(f'🏆 Achievement Unlocked: {achievement["icon"]} {achievement["name"]} - {achievement["description"]}', 'info')
        else:
            if not city.can_afford(building_type):
                cost = city.get_building_cost(building_type)
                flash(f'Cannot build {building_type} at cell ({row}, {col}) - insufficient funds! Need ${cost}, have ${city.money}', 'error')
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
    
    # Check for new achievements after advancing year
    recent_achievements = city.get_recent_achievements(1)
    if recent_achievements and recent_achievements[-1]['year'] == city.current_year:
        achievement = recent_achievements[-1]
        flash(f'🏆 Achievement Unlocked: {achievement["icon"]} {achievement["name"]} - {achievement["description"]}', 'info')
    
    save_city(city)
    flash(f'Advanced to year {city.current_year}', 'info')
    return redirect(url_for('index'))

@app.route('/reset', methods=['POST'])
def reset_city():
    """Reset the city to initial state"""
    session.pop('city_data', None)
    flash('City has been reset', 'info')
    return redirect(url_for('index'))

@app.route('/trigger_event', methods=['POST'])
def trigger_event():
    """Manually trigger a random event for testing"""
    city = get_city()
    event = city.trigger_random_event()
    if event:
        flash(f"Event: {event['name']} - {event['description']}", 'info')
    else:
        flash('No event triggered this time', 'info')
    save_city(city)
    return redirect(url_for('index'))

@app.route('/save_city', methods=['POST'])
def save_city_to_file():
    """Save current city to a file"""
    city = get_city()
    save_name = request.form.get('save_name', 'My City')
    
    # Create saves directory if it doesn't exist
    import os
    saves_dir = 'saves'
    if not os.path.exists(saves_dir):
        os.makedirs(saves_dir)
    
    # Save city data to file
    import json
    save_data = city.to_dict()
    save_data['save_name'] = save_name
    save_data['save_date'] = str(datetime.now())
    
    filename = f"{save_name.replace(' ', '_')}.json"
    filepath = os.path.join(saves_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(save_data, f, indent=2)
    
    flash(f'City saved as "{save_name}"', 'success')
    return redirect(url_for('index'))

@app.route('/load_city', methods=['POST'])
def load_city_from_file():
    """Load a city from a file"""
    save_name = request.form.get('save_name')
    
    if not save_name:
        flash('Please select a save file', 'error')
        return redirect(url_for('index'))
    
    import os
    import json
    from datetime import datetime
    
    filename = f"{save_name.replace(' ', '_')}.json"
    filepath = os.path.join('saves', filename)
    
    if not os.path.exists(filepath):
        flash(f'Save file "{save_name}" not found', 'error')
        return redirect(url_for('index'))
    
    try:
        with open(filepath, 'r') as f:
            save_data = json.load(f)
        
        # Load city data
        city = CitySimulation.from_dict(save_data)
        session['city_data'] = city.to_dict()
        session.modified = True
        
        flash(f'City "{save_name}" loaded successfully', 'success')
    except Exception as e:
        flash(f'Error loading city: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/list_saves')
def list_saves():
    """Get list of available save files"""
    import os
    import json
    from datetime import datetime
    
    saves_dir = 'saves'
    if not os.path.exists(saves_dir):
        return {'saves': []}
    
    saves = []
    for filename in os.listdir(saves_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(saves_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    save_data = json.load(f)
                
                saves.append({
                    'name': save_data.get('save_name', filename.replace('.json', '')),
                    'date': save_data.get('save_date', 'Unknown'),
                    'year': save_data.get('current_year', 1),
                    'population': save_data.get('population', 0),
                    'money': save_data.get('money', 0)
                })
            except:
                continue
    
    return {'saves': saves}

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

# Advanced Features Routes

@app.route('/zone_2x2', methods=['POST'])
def zone_2x2_block():
    """Zone a 2x2 block of land"""
    city = get_city()
    
    try:
        row = int(request.form.get('row'))
        col = int(request.form.get('col'))
        zone_type = request.form.get('zone_type')
        
        if city.zone_2x2_block(row, col, zone_type):
            cost = city.get_building_cost(zone_type) * 4
            flash(f'Successfully zoned 2x2 block at ({row}, {col}) as {zone_type} for ${cost}', 'success')
        else:
            if not city.can_afford(zone_type):
                cost = city.get_building_cost(zone_type) * 4
                flash(f'Cannot zone 2x2 block - insufficient funds! Need ${cost}, have ${city.money}', 'error')
            else:
                flash(f'Cannot zone 2x2 block at ({row}, {col}) - area may be occupied', 'error')
            
        save_city(city)
    except (ValueError, TypeError) as e:
        flash('Invalid zoning parameters', 'error')
    
    return redirect(url_for('index'))

@app.route('/build_road', methods=['POST'])
def build_road_tile():
    """Build a road tile"""
    city = get_city()
    
    try:
        row = int(request.form.get('row'))
        col = int(request.form.get('col'))
        
        if city.build_road_tile(row, col):
            cost = city.get_building_cost(city.ROAD)
            flash(f'Successfully built road at ({row}, {col}) for ${cost}', 'success')
        else:
            if not city.can_afford(city.ROAD):
                cost = city.get_building_cost(city.ROAD)
                flash(f'Cannot build road - insufficient funds! Need ${cost}, have ${city.money}', 'error')
            else:
                flash(f'Cannot build road at ({row}, {col}) - cell may be occupied', 'error')
            
        save_city(city)
    except (ValueError, TypeError) as e:
        flash('Invalid road building parameters', 'error')
    
    return redirect(url_for('index'))

@app.route('/build_power_line', methods=['POST'])
def build_power_line():
    """Build a power line tile"""
    city = get_city()
    
    try:
        row = int(request.form.get('row'))
        col = int(request.form.get('col'))
        
        if city.build_power_line(row, col):
            flash(f'Successfully built power line at ({row}, {col}) for $100', 'success')
        else:
            if city.money < 100:
                flash(f'Cannot build power line - insufficient funds! Need $100, have ${city.money}', 'error')
            else:
                flash(f'Cannot build power line at ({row}, {col}) - cell may be occupied', 'error')
            
        save_city(city)
    except (ValueError, TypeError) as e:
        flash('Invalid power line building parameters', 'error')
    
    return redirect(url_for('index'))

@app.route('/trigger_disaster', methods=['POST'])
def trigger_disaster():
    """Trigger a disaster at a specific location"""
    city = get_city()
    
    try:
        row = int(request.form.get('row'))
        col = int(request.form.get('col'))
        disaster_type = request.form.get('disaster_type', 'fire')
        
        if city.trigger_disaster(disaster_type, row, col):
            flash(f'Disaster triggered: {disaster_type} at ({row}, {col})', 'warning')
        else:
            flash(f'Cannot trigger disaster at ({row}, {col}) - invalid location', 'error')
            
        save_city(city)
    except (ValueError, TypeError) as e:
        flash('Invalid disaster parameters', 'error')
    
    return redirect(url_for('index'))

@app.route('/update_systems', methods=['POST'])
def update_systems():
    """Update all city systems (building states, traffic, etc.)"""
    city = get_city()
    
    # Update all systems
    city.update_building_states()
    city.calculate_traffic()
    city.calculate_daily_economy()
    city.update_power_distribution()
    
    save_city(city)
    flash('City systems updated', 'info')
    return redirect(url_for('index'))

@app.route('/get_cell_info/<int:row>/<int:col>')
def get_cell_info(row, col):
    """Get detailed information about a cell"""
    city = get_city()
    
    if not city.is_valid_position(row, col):
        return {'error': 'Invalid position'}
    
    cell_type = city.grid[row][col]
    cell_name = city.get_cell_name(row, col)
    
    info = {
        'row': row,
        'col': col,
        'type': cell_type,
        'name': cell_name,
        'display': city.get_cell_display(row, col)
    }
    
    # Add building state info for zoned buildings
    if cell_type in [city.RESIDENTIAL, city.COMMERCIAL, city.INDUSTRIAL]:
        state = city.building_states.get((row, col), city.ZONED_EMPTY)
        desirability = city.desirability_scores.get((row, col), 0)
        has_road = (row, col) in city.road_network
        has_power = (row, col) in city.power_network
        traffic = city.traffic_levels.get((row, col), 0)
        
        info.update({
            'state': state,
            'desirability': desirability,
            'has_road': has_road,
            'has_power': has_power,
            'traffic_level': traffic
        })
    
    return info
