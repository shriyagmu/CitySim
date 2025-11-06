import logging

class CitySimulation:
    """Main city simulation game logic"""
    
    # Zone types
    RESIDENTIAL = 'R'
    COMMERCIAL = 'C'
    INDUSTRIAL = 'I'
    PARK = 'P'
    
    # Building types
    SCHOOL = 'School'
    HOSPITAL = 'Hospital'
    POWER_PLANT = 'Power'
    ROAD = 'Road'
    POLICE_STATION = 'Police'
    FIRE_STATION = 'Fire'
    AIRPORT = 'Airport'
    STADIUM = 'Stadium'
    MALL = 'Mall'
    UNIVERSITY = 'University'
    
    # Advanced building states
    ZONED_EMPTY = 'Zoned_Empty'
    ZONED_DEVELOPING = 'Zoned_Developing'
    ZONED_OPERATING = 'Zoned_Operating'
    ZONED_ABANDONED = 'Zoned_Abandoned'
    
    # Road connection types
    ROAD_NONE = 'Road_None'
    ROAD_HORIZONTAL = 'Road_H'
    ROAD_VERTICAL = 'Road_V'
    ROAD_CROSS = 'Road_Cross'
    ROAD_T_UP = 'Road_T_Up'
    ROAD_T_DOWN = 'Road_T_Down'
    ROAD_T_LEFT = 'Road_T_Left'
    ROAD_T_RIGHT = 'Road_T_Right'
    ROAD_CORNER_UL = 'Road_Corner_UL'
    ROAD_CORNER_UR = 'Road_Corner_UR'
    ROAD_CORNER_DL = 'Road_Corner_DL'
    ROAD_CORNER_DR = 'Road_Corner_DR'
    
    # Grid size
    GRID_SIZE = 5
    
    # Building costs
    BUILDING_COSTS = {
        RESIDENTIAL: 500,
        COMMERCIAL: 800,
        INDUSTRIAL: 1000,
        PARK: 300,
        SCHOOL: 2000,
        HOSPITAL: 3000,
        POWER_PLANT: 2500,
        ROAD: 200,
        POLICE_STATION: 4000,
        FIRE_STATION: 3500,
        AIRPORT: 15000,
        STADIUM: 8000,
        MALL: 6000,
        UNIVERSITY: 10000
    }
    
    # Maintenance costs per year
    MAINTENANCE_COSTS = {
        RESIDENTIAL: 50,
        COMMERCIAL: 100,
        INDUSTRIAL: 150,
        PARK: 30,
        SCHOOL: 200,
        HOSPITAL: 300,
        POWER_PLANT: 250,
        ROAD: 20,
        POLICE_STATION: 400,
        FIRE_STATION: 350,
        AIRPORT: 1500,
        STADIUM: 800,
        MALL: 600,
        UNIVERSITY: 1000
    }
    
    def __init__(self):
        """Initialize a new city simulation"""
        self.grid = [[None for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.current_year = 1
        self.population = 0
        self.happiness = 50  # Start at neutral happiness
        self.money = 10000  # Starting budget
        self.tax_rate = 0.05  # 5% tax rate
        self.income = 0  # Monthly income
        self.expenses = 0  # Monthly expenses
        self.events = []  # List of active events
        self.event_history = []  # History of past events
        self.achievements = []  # List of unlocked achievements
        self.achievement_history = []  # History of achievement unlocks
        
        # Advanced systems
        self.building_states = {}  # Track building states (row,col) -> state
        self.desirability_scores = {}  # Track desirability scores (row,col) -> score
        self.power_network = set()  # Set of powered cells
        self.road_network = set()  # Set of road cells
        self.traffic_levels = {}  # Track traffic levels (row,col) -> level
        self.disasters = []  # Active disasters
        self.daily_revenue = 0  # Daily revenue from operating buildings
        self.daily_maintenance = 0  # Daily maintenance costs
        
    def to_dict(self):
        """Convert city state to dictionary for session storage"""
        return {
            'grid': self.grid,
            'current_year': self.current_year,
            'population': self.population,
            'happiness': self.happiness,
            'money': self.money,
            'tax_rate': self.tax_rate,
            'income': self.income,
            'expenses': self.expenses,
            'events': self.events,
            'event_history': self.event_history,
            'achievements': self.achievements,
            'achievement_history': self.achievement_history,
            'building_states': {f"{row},{col}": value for (row, col), value in self.building_states.items()},
            'desirability_scores': {f"{row},{col}": value for (row, col), value in self.desirability_scores.items()},
            'power_network': list(self.power_network),
            'road_network': list(self.road_network),
            'traffic_levels': {f"{row},{col}": value for (row, col), value in self.traffic_levels.items()},
            'disasters': self.disasters,
            'daily_revenue': self.daily_revenue,
            'daily_maintenance': self.daily_maintenance
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create city from dictionary data"""
        city = cls()
        city.grid = data.get('grid', [[None for _ in range(cls.GRID_SIZE)] for _ in range(cls.GRID_SIZE)])
        city.current_year = data.get('current_year', 1)
        city.population = data.get('population', 0)
        city.happiness = data.get('happiness', 50)
        city.money = data.get('money', 10000)
        city.tax_rate = data.get('tax_rate', 0.05)
        city.income = data.get('income', 0)
        city.expenses = data.get('expenses', 0)
        city.events = data.get('events', [])
        city.event_history = data.get('event_history', [])
        city.achievements = data.get('achievements', [])
        city.achievement_history = data.get('achievement_history', [])
        
        # Convert string keys back to tuple keys
        building_states = data.get('building_states', {})
        city.building_states = {tuple(map(int, key.split(','))): value for key, value in building_states.items()}
        
        desirability_scores = data.get('desirability_scores', {})
        city.desirability_scores = {tuple(map(int, key.split(','))): value for key, value in desirability_scores.items()}
        
        city.power_network = set(data.get('power_network', []))
        city.road_network = set(data.get('road_network', []))
        
        traffic_levels = data.get('traffic_levels', {})
        city.traffic_levels = {tuple(map(int, key.split(','))): value for key, value in traffic_levels.items()}
        
        city.disasters = data.get('disasters', [])
        city.daily_revenue = data.get('daily_revenue', 0)
        city.daily_maintenance = data.get('daily_maintenance', 0)
        return city
    
    def is_valid_position(self, row, col):
        """Check if position is within grid bounds"""
        return 0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE
    
    def is_cell_empty(self, row, col):
        """Check if a cell is empty"""
        if not self.is_valid_position(row, col):
            return False
        return self.grid[row][col] is None
    
    def zone_land(self, row, col, zone_type):
        """Zone a piece of land"""
        if not self.is_valid_position(row, col):
            logging.warning(f"Invalid position: ({row}, {col})")
            return False
            
        if not self.is_cell_empty(row, col):
            logging.warning(f"Cell ({row}, {col}) is already occupied")
            return False
        
        valid_zones = [self.RESIDENTIAL, self.COMMERCIAL, self.INDUSTRIAL, self.PARK]
        if zone_type not in valid_zones:
            logging.warning(f"Invalid zone type: {zone_type}")
            return False
        
        # Check if player has enough money
        cost = self.BUILDING_COSTS.get(zone_type, 0)
        if self.money < cost:
            logging.warning(f"Insufficient funds. Need ${cost}, have ${self.money}")
            return False
        
        # Deduct cost and build
        self.money -= cost
        self.grid[row][col] = zone_type
        logging.info(f"Zoned cell ({row}, {col}) as {zone_type} for ${cost}")
        
        # Check for achievements after building
        self.check_achievements()
        return True
    
    def build_structure(self, row, col, building_type):
        """Build a structure"""
        if not self.is_valid_position(row, col):
            logging.warning(f"Invalid position: ({row}, {col})")
            return False
            
        if not self.is_cell_empty(row, col):
            logging.warning(f"Cell ({row}, {col}) is already occupied")
            return False
        
        valid_buildings = [self.SCHOOL, self.HOSPITAL, self.POWER_PLANT, self.ROAD, 
                          self.POLICE_STATION, self.FIRE_STATION, self.AIRPORT, 
                          self.STADIUM, self.MALL, self.UNIVERSITY]
        if building_type not in valid_buildings:
            logging.warning(f"Invalid building type: {building_type}")
            return False
        
        # Check if player has enough money
        cost = self.BUILDING_COSTS.get(building_type, 0)
        if self.money < cost:
            logging.warning(f"Insufficient funds. Need ${cost}, have ${self.money}")
            return False
        
        # Deduct cost and build
        self.money -= cost
        self.grid[row][col] = building_type
        logging.info(f"Built {building_type} at cell ({row}, {col}) for ${cost}")
        
        # Check for achievements after building
        self.check_achievements()
        return True
    
    def clear_cell(self, row, col):
        """Clear a cell"""
        if not self.is_valid_position(row, col):
            return False
            
        if self.is_cell_empty(row, col):
            return False
        
        self.grid[row][col] = None
        logging.info(f"Cleared cell ({row}, {col})")
        return True
    
    def count_cell_type(self, cell_type):
        """Count occurrences of a specific cell type"""
        count = 0
        for row in self.grid:
            for cell in row:
                if cell == cell_type:
                    count += 1
        return count
    
    def calculate_population(self):
        """Calculate population based on residential zones and available jobs"""
        # Base residential capacity
        residential_zones = self.count_cell_type(self.RESIDENTIAL)
        base_capacity = residential_zones * 100  # 100 people per residential zone
        
        # Job availability from commercial and industrial zones
        commercial_jobs = self.count_cell_type(self.COMMERCIAL) * 50
        industrial_jobs = self.count_cell_type(self.INDUSTRIAL) * 75
        total_jobs = commercial_jobs + industrial_jobs
        
        # Population is limited by both capacity and jobs
        # But can't exceed residential capacity
        if total_jobs == 0 and residential_zones == 0:
            return 0
        elif total_jobs == 0:
            return min(base_capacity // 4, base_capacity)  # Some unemployment is ok
        else:
            return min(base_capacity, total_jobs)
    
    def calculate_happiness(self):
        """Calculate city happiness based on various factors"""
        if self.population == 0:
            return 50  # Neutral happiness for empty city
        
        happiness = 50  # Base happiness
        
        # Positive factors
        schools = self.count_cell_type(self.SCHOOL)
        hospitals = self.count_cell_type(self.HOSPITAL)
        parks = self.count_cell_type(self.PARK)
        power_plants = self.count_cell_type(self.POWER_PLANT)
        
        # Boosts for amenities
        happiness += schools * 10  # Schools boost happiness
        happiness += hospitals * 8  # Hospitals boost happiness
        happiness += parks * 12  # Parks provide significant happiness boost
        happiness += power_plants * 5  # Power provides basic happiness
        
        # Negative factors
        industrial = self.count_cell_type(self.INDUSTRIAL)
        happiness -= industrial * 3  # Small penalty for industrial pollution
        
        # Population density effect (overcrowding penalty)
        residential_zones = self.count_cell_type(self.RESIDENTIAL)
        if residential_zones > 0:
            density = self.population / (residential_zones * 100)
            if density > 0.8:  # If over 80% capacity
                happiness -= int((density - 0.8) * 20)  # Overcrowding penalty
        
        # Ensure happiness stays within reasonable bounds
        happiness = max(0, min(100, happiness))
        return int(happiness)
    
    def calculate_income(self):
        """Calculate monthly income from taxes and commercial activity"""
        # Tax income from population
        tax_income = self.population * self.tax_rate * 10  # $10 per person per month
        
        # Commercial activity income
        commercial_zones = self.count_cell_type(self.COMMERCIAL)
        commercial_income = commercial_zones * 200  # $200 per commercial zone per month
        
        # Industrial activity income
        industrial_zones = self.count_cell_type(self.INDUSTRIAL)
        industrial_income = industrial_zones * 300  # $300 per industrial zone per month
        
        self.income = tax_income + commercial_income + industrial_income
        return self.income
    
    def calculate_expenses(self):
        """Calculate monthly maintenance expenses"""
        total_expenses = 0
        
        # Count all buildings and their maintenance costs
        for row in self.grid:
            for cell in row:
                if cell:
                    maintenance_cost = self.MAINTENANCE_COSTS.get(cell, 0)
                    total_expenses += maintenance_cost / 12  # Monthly cost
        
        self.expenses = total_expenses
        return self.expenses
    
    def advance_year(self):
        """Advance the city by one year and recalculate stats"""
        self.current_year += 1
        
        # Process daily systems for 365 days
        for day in range(365):
            # Update building states based on conditions
            self.update_building_states()
            
            # Calculate traffic
            self.calculate_traffic()
            
            # Calculate daily economy
            self.calculate_daily_economy()
            
            # Process disasters
            self.process_disasters()
            
            # Update power distribution
            self.update_power_distribution()
        
        # Recalculate yearly stats
        self.population = self.calculate_population()
        self.happiness = self.calculate_happiness()
        
        # Process ongoing events
        self.process_events()
        
        # Calculate and apply economic changes
        monthly_income = self.calculate_income()
        monthly_expenses = self.calculate_expenses()
        
        # Apply income multipliers from active events
        income_multiplier = 1.0
        for event in self.get_active_events():
            if 'income_multiplier' in event.get('effects', {}):
                income_multiplier *= event['effects']['income_multiplier']
        
        monthly_income *= income_multiplier
        net_monthly = monthly_income - monthly_expenses
        
        # Apply 12 months of economic changes
        self.money += (monthly_income * 12) - (monthly_expenses * 12)
        
        # Ensure money doesn't go below 0
        self.money = max(0, self.money)
        
        # Trigger random event (30% chance per year)
        import random
        if random.random() < 0.3:
            event = self.trigger_random_event()
            if event:
                logging.info(f"Random event: {event['name']}")
        
        # Check for new achievements
        self.check_achievements()
        
        logging.info(f"Advanced to year {self.current_year}, Population: {self.population}, Happiness: {self.happiness}, Money: ${self.money:.0f}")
    
    def get_cell_display(self, row, col):
        """Get display string for a cell"""
        if not self.is_valid_position(row, col):
            return '?'
        
        cell = self.grid[row][col]
        if cell is None:
            return '.'
        elif cell in [self.RESIDENTIAL, self.COMMERCIAL, self.INDUSTRIAL, self.PARK]:
            # Check building state for zoned buildings
            if cell in [self.RESIDENTIAL, self.COMMERCIAL, self.INDUSTRIAL]:
                state = self.building_states.get((row, col), self.ZONED_EMPTY)
                if state == self.ZONED_OPERATING:
                    return cell.lower()  # Lowercase for operating
                elif state == self.ZONED_DEVELOPING:
                    return cell + 'd'  # Add 'd' for developing
                elif state == self.ZONED_ABANDONED:
                    return cell + 'a'  # Add 'a' for abandoned
            return cell
        elif cell == self.SCHOOL:
            return 'S'
        elif cell == self.HOSPITAL:
            return 'H'
        elif cell == self.POWER_PLANT:
            return 'E'  # E for Energy/Electricity
        elif cell == 'Power_Line':
            return '|'  # Power line symbol
        elif cell == self.POLICE_STATION:
            return 'L'  # L for Police (Law enforcement)
        elif cell == self.FIRE_STATION:
            return 'F'  # F for Fire
        elif cell == self.AIRPORT:
            return 'A'  # A for Airport
        elif cell == self.STADIUM:
            return 'T'  # T for Stadium
        elif cell == self.MALL:
            return 'M'  # M for Mall
        elif cell == self.UNIVERSITY:
            return 'U'  # U for University
        # Road types
        elif cell == self.ROAD_HORIZONTAL:
            return '─'
        elif cell == self.ROAD_VERTICAL:
            return '│'
        elif cell == self.ROAD_CROSS:
            return '┼'
        elif cell == self.ROAD_T_UP:
            return '┴'
        elif cell == self.ROAD_T_DOWN:
            return '┬'
        elif cell == self.ROAD_T_LEFT:
            return '┤'
        elif cell == self.ROAD_T_RIGHT:
            return '├'
        elif cell == self.ROAD_CORNER_UL:
            return '┘'
        elif cell == self.ROAD_CORNER_UR:
            return '└'
        elif cell == self.ROAD_CORNER_DL:
            return '┐'
        elif cell == self.ROAD_CORNER_DR:
            return '┌'
        elif cell == self.ROAD_NONE:
            return '#'
        else:
            return '?'
    
    def get_cell_name(self, row, col):
        """Get full name for a cell"""
        if not self.is_valid_position(row, col):
            return 'Invalid'
        
        cell = self.grid[row][col]
        if cell is None:
            return 'Empty'
        elif cell == self.RESIDENTIAL:
            return 'Residential'
        elif cell == self.COMMERCIAL:
            return 'Commercial'
        elif cell == self.INDUSTRIAL:
            return 'Industrial'
        elif cell == self.PARK:
            return 'Park'
        elif cell in [self.SCHOOL, self.HOSPITAL, self.POWER_PLANT, self.ROAD, 
                     self.POLICE_STATION, self.FIRE_STATION, self.AIRPORT, 
                     self.STADIUM, self.MALL, self.UNIVERSITY]:
            return cell
        else:
            return 'Unknown'
    
    def get_statistics(self):
        """Get city statistics"""
        return {
            'residential': self.count_cell_type(self.RESIDENTIAL),
            'commercial': self.count_cell_type(self.COMMERCIAL),
            'industrial': self.count_cell_type(self.INDUSTRIAL),
            'parks': self.count_cell_type(self.PARK),
            'schools': self.count_cell_type(self.SCHOOL),
            'hospitals': self.count_cell_type(self.HOSPITAL),
            'power_plants': self.count_cell_type(self.POWER_PLANT),
            'roads': self.count_cell_type(self.ROAD),
            'police_stations': self.count_cell_type(self.POLICE_STATION),
            'fire_stations': self.count_cell_type(self.FIRE_STATION),
            'airports': self.count_cell_type(self.AIRPORT),
            'stadiums': self.count_cell_type(self.STADIUM),
            'malls': self.count_cell_type(self.MALL),
            'universities': self.count_cell_type(self.UNIVERSITY),
            'empty_cells': sum(row.count(None) for row in self.grid)
        }
    
    def get_building_cost(self, building_type):
        """Get the cost of a building type"""
        return self.BUILDING_COSTS.get(building_type, 0)
    
    def can_afford(self, building_type):
        """Check if player can afford a building"""
        cost = self.get_building_cost(building_type)
        return self.money >= cost
    
    def trigger_random_event(self):
        """Trigger a random event"""
        import random
        
        # Event probabilities (higher = more likely)
        events = [
            # Positive events
            {'name': 'Tourism Boom', 'probability': 0.15, 'type': 'positive', 'description': 'Tourists flock to your city!', 'effects': {'money': 2000, 'happiness': 10}},
            {'name': 'Tech Company', 'probability': 0.10, 'type': 'positive', 'description': 'A major tech company opens offices!', 'effects': {'money': 3000, 'income_multiplier': 1.2}},
            {'name': 'Festival', 'probability': 0.20, 'type': 'positive', 'description': 'Annual city festival brings joy!', 'effects': {'happiness': 15, 'money': 500}},
            {'name': 'Green Initiative', 'probability': 0.12, 'type': 'positive', 'description': 'Environmental grants boost your city!', 'effects': {'money': 1500, 'happiness': 8}},
            
            # Negative events
            {'name': 'Fire', 'probability': 0.08, 'type': 'disaster', 'description': 'A fire breaks out in the city!', 'effects': {'money': -1000, 'happiness': -10}},
            {'name': 'Economic Recession', 'probability': 0.10, 'type': 'negative', 'description': 'Economic downturn affects the city!', 'effects': {'income_multiplier': 0.7, 'happiness': -5}},
            {'name': 'Flood', 'probability': 0.06, 'type': 'disaster', 'description': 'Heavy flooding damages infrastructure!', 'effects': {'money': -2000, 'happiness': -15}},
            {'name': 'Power Outage', 'probability': 0.12, 'type': 'negative', 'description': 'City-wide power outage!', 'effects': {'happiness': -8, 'money': -500}},
            {'name': 'Traffic Jam', 'probability': 0.15, 'type': 'negative', 'description': 'Major traffic congestion!', 'effects': {'happiness': -5, 'money': -300}},
        ]
        
        # Calculate total probability
        total_prob = sum(event['probability'] for event in events)
        
        # Roll for event
        roll = random.random() * total_prob
        current_prob = 0
        
        for event in events:
            current_prob += event['probability']
            if roll <= current_prob:
                # Trigger this event
                self.apply_event(event)
                return event
        
        return None
    
    def apply_event(self, event):
        """Apply the effects of an event"""
        effects = event.get('effects', {})
        
        # Apply money effects
        if 'money' in effects:
            self.money += effects['money']
            self.money = max(0, self.money)  # Don't go below 0
        
        # Apply happiness effects
        if 'happiness' in effects:
            self.happiness += effects['happiness']
            self.happiness = max(0, min(100, self.happiness))
        
        # Apply income multiplier (temporary)
        if 'income_multiplier' in effects:
            # Store as a temporary event
            event_copy = event.copy()
            event_copy['duration'] = 12  # 12 months
            event_copy['remaining_duration'] = 12
            self.events.append(event_copy)
        
        # Add to history
        self.event_history.append({
            'name': event['name'],
            'description': event['description'],
            'type': event['type'],
            'year': self.current_year
        })
        
        logging.info(f"Event triggered: {event['name']} - {event['description']}")
    
    def process_events(self):
        """Process ongoing events and their effects"""
        # Process income multipliers
        for event in self.events[:]:  # Copy list to avoid modification during iteration
            if 'income_multiplier' in event.get('effects', {}):
                event['remaining_duration'] -= 1
                if event['remaining_duration'] <= 0:
                    self.events.remove(event)
                    logging.info(f"Event ended: {event['name']}")
    
    def get_active_events(self):
        """Get list of currently active events"""
        return [event for event in self.events if event.get('remaining_duration', 0) > 0]
    
    def check_achievements(self):
        """Check and unlock new achievements"""
        stats = self.get_statistics()
        
        # Define all possible achievements
        all_achievements = [
            # Population achievements
            {'id': 'first_citizens', 'name': 'First Citizens', 'description': 'Reach 100 population', 'condition': lambda: self.population >= 100, 'icon': '👥'},
            {'id': 'growing_city', 'name': 'Growing City', 'description': 'Reach 500 population', 'condition': lambda: self.population >= 500, 'icon': '🏙️'},
            {'id': 'metropoliss', 'name': 'Metropolis', 'description': 'Reach 1000 population', 'condition': lambda: self.population >= 1000, 'icon': '🌆'},
            
            # Building achievements
            {'id': 'first_building', 'name': 'First Building', 'description': 'Build your first structure', 'condition': lambda: sum(stats.values()) - stats['empty_cells'] >= 1, 'icon': '🏗️'},
            {'id': 'school_system', 'name': 'School System', 'description': 'Build 2 schools', 'condition': lambda: stats['schools'] >= 2, 'icon': '🎓'},
            {'id': 'healthcare', 'name': 'Healthcare', 'description': 'Build 2 hospitals', 'condition': lambda: stats['hospitals'] >= 2, 'icon': '🏥'},
            {'id': 'power_grid', 'name': 'Power Grid', 'description': 'Build 3 power plants', 'condition': lambda: stats['power_plants'] >= 3, 'icon': '⚡'},
            {'id': 'road_network', 'name': 'Road Network', 'description': 'Build 5 roads', 'condition': lambda: stats['roads'] >= 5, 'icon': '🛣️'},
            
            # Zone achievements
            {'id': 'residential_zone', 'name': 'Residential Zone', 'description': 'Build 3 residential zones', 'condition': lambda: stats['residential'] >= 3, 'icon': '🏠'},
            {'id': 'commercial_district', 'name': 'Commercial District', 'description': 'Build 3 commercial zones', 'condition': lambda: stats['commercial'] >= 3, 'icon': '🏪'},
            {'id': 'industrial_area', 'name': 'Industrial Area', 'description': 'Build 3 industrial zones', 'condition': lambda: stats['industrial'] >= 3, 'icon': '🏭'},
            {'id': 'green_city', 'name': 'Green City', 'description': 'Build 4 parks', 'condition': lambda: stats['parks'] >= 4, 'icon': '🌳'},
            
            # Happiness achievements
            {'id': 'happy_city', 'name': 'Happy City', 'description': 'Achieve 80% happiness', 'condition': lambda: self.happiness >= 80, 'icon': '😊'},
            {'id': 'paradise', 'name': 'Paradise', 'description': 'Achieve 95% happiness', 'condition': lambda: self.happiness >= 95, 'icon': '😇'},
            
            # Economic achievements
            {'id': 'wealthy_city', 'name': 'Wealthy City', 'description': 'Accumulate $50,000', 'condition': lambda: self.money >= 50000, 'icon': '💰'},
            {'id': 'economic_boom', 'name': 'Economic Boom', 'description': 'Have $100,000', 'condition': lambda: self.money >= 100000, 'icon': '💎'},
            
            # Time achievements
            {'id': 'decade', 'name': 'Decade', 'description': 'Reach year 10', 'condition': lambda: self.current_year >= 10, 'icon': '📅'},
            {'id': 'century', 'name': 'Century', 'description': 'Reach year 100', 'condition': lambda: self.current_year >= 100, 'icon': '🗓️'},
            
            # Special achievements
            {'id': 'full_grid', 'name': 'Full Grid', 'description': 'Fill the entire 5x5 grid', 'condition': lambda: stats['empty_cells'] == 0, 'icon': '🎯'},
            {'id': 'balanced_city', 'name': 'Balanced City', 'description': 'Have at least 2 of each zone type', 'condition': lambda: all(stats[zone] >= 2 for zone in ['residential', 'commercial', 'industrial', 'parks']), 'icon': '⚖️'},
        ]
        
        # Check each achievement
        for achievement in all_achievements:
            if achievement['id'] not in self.achievements and achievement['condition']():
                self.unlock_achievement(achievement)
    
    def unlock_achievement(self, achievement):
        """Unlock an achievement"""
        self.achievements.append(achievement['id'])
        self.achievement_history.append({
            'id': achievement['id'],
            'name': achievement['name'],
            'description': achievement['description'],
            'icon': achievement['icon'],
            'year': self.current_year
        })
        
        # Give bonus rewards for achievements
        if achievement['id'] in ['metropoliss', 'paradise', 'economic_boom']:
            self.money += 5000  # Bonus money for major achievements
            logging.info(f"Achievement unlocked: {achievement['name']} - Bonus $5000!")
        else:
            logging.info(f"Achievement unlocked: {achievement['name']}")
    
    def get_recent_achievements(self, count=5):
        """Get recent achievements"""
        return self.achievement_history[-count:] if self.achievement_history else []
    
    # Advanced Systems Methods
    
    def zone_2x2_block(self, row, col, zone_type):
        """Zone a 2x2 block of land"""
        if not self.is_valid_position(row, col) or not self.is_valid_position(row+1, col+1):
            return False
        
        # Check if all 4 cells are empty
        for r in range(row, row+2):
            for c in range(col, col+2):
                if not self.is_cell_empty(r, c):
                    return False
        
        # Check if player has enough money (4x cost)
        cost = self.BUILDING_COSTS.get(zone_type, 0) * 4
        if self.money < cost:
            return False
        
        # Zone all 4 cells
        self.money -= cost
        for r in range(row, row+2):
            for c in range(col, col+2):
                self.grid[r][c] = zone_type
                self.building_states[(r, c)] = self.ZONED_EMPTY
        
        logging.info(f"Zoned 2x2 block at ({row}, {col}) as {zone_type} for ${cost}")
        return True
    
    def build_road_tile(self, row, col):
        """Build a road tile and update connections"""
        if not self.is_valid_position(row, col) or not self.is_cell_empty(row, col):
            return False
        
        cost = self.BUILDING_COSTS.get(self.ROAD, 0)
        if self.money < cost:
            return False
        
        self.money -= cost
        self.grid[row][col] = self.ROAD
        self.road_network.add((row, col))
        
        # Update road connections
        self.update_road_connections()
        
        logging.info(f"Built road at ({row}, {col}) for ${cost}")
        return True
    
    def update_road_connections(self):
        """Update road tile appearances based on connections"""
        for row, col in self.road_network:
            if self.grid[row][col] == self.ROAD:
                # Check connections to adjacent roads
                connections = []
                if (row-1, col) in self.road_network: connections.append('up')
                if (row+1, col) in self.road_network: connections.append('down')
                if (row, col-1) in self.road_network: connections.append('left')
                if (row, col+1) in self.road_network: connections.append('right')
                
                # Determine road type based on connections
                if len(connections) == 0:
                    road_type = self.ROAD_NONE
                elif len(connections) == 1:
                    if 'up' in connections: road_type = self.ROAD_VERTICAL
                    elif 'down' in connections: road_type = self.ROAD_VERTICAL
                    elif 'left' in connections: road_type = self.ROAD_HORIZONTAL
                    elif 'right' in connections: road_type = self.ROAD_HORIZONTAL
                elif len(connections) == 2:
                    if 'up' in connections and 'down' in connections:
                        road_type = self.ROAD_VERTICAL
                    elif 'left' in connections and 'right' in connections:
                        road_type = self.ROAD_HORIZONTAL
                    elif 'up' in connections and 'left' in connections:
                        road_type = self.ROAD_CORNER_UL
                    elif 'up' in connections and 'right' in connections:
                        road_type = self.ROAD_CORNER_UR
                    elif 'down' in connections and 'left' in connections:
                        road_type = self.ROAD_CORNER_DL
                    elif 'down' in connections and 'right' in connections:
                        road_type = self.ROAD_CORNER_DR
                elif len(connections) == 3:
                    if 'up' not in connections: road_type = self.ROAD_T_UP
                    elif 'down' not in connections: road_type = self.ROAD_T_DOWN
                    elif 'left' not in connections: road_type = self.ROAD_T_LEFT
                    elif 'right' not in connections: road_type = self.ROAD_T_RIGHT
                else:  # 4 connections
                    road_type = self.ROAD_CROSS
                
                # Store the road type (we'll use this for display)
                self.grid[row][col] = road_type
    
    def build_power_line(self, row, col):
        """Build a power line tile"""
        if not self.is_valid_position(row, col) or not self.is_cell_empty(row, col):
            return False
        
        cost = 100  # Power lines are cheaper than roads
        if self.money < cost:
            return False
        
        self.money -= cost
        self.power_network.add((row, col))
        self.grid[row][col] = 'Power_Line'  # Special marker for power lines
        
        # Update power distribution
        self.update_power_distribution()
        
        logging.info(f"Built power line at ({row}, {col}) for ${cost}")
        return True
    
    def update_power_distribution(self):
        """Update which buildings have power based on power plant connections"""
        # Reset all powered status
        powered_buildings = set()
        
        # Find all power plants
        power_plants = []
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                if self.grid[row][col] == self.POWER_PLANT:
                    power_plants.append((row, col))
                    powered_buildings.add((row, col))
        
        # BFS to find all connected buildings
        for plant_row, plant_col in power_plants:
            queue = [(plant_row, plant_col)]
            visited = set()
            
            while queue:
                current_row, current_col = queue.pop(0)
                if (current_row, current_col) in visited:
                    continue
                visited.add((current_row, current_col))
                
                # Check adjacent cells for power lines or buildings
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_row, new_col = current_row + dr, current_col + dc
                    if (self.is_valid_position(new_row, new_col) and 
                        (new_row, new_col) not in visited and
                        ((new_row, new_col) in self.power_network or 
                         self.grid[new_row][new_col] in [self.RESIDENTIAL, self.COMMERCIAL, self.INDUSTRIAL])):
                        powered_buildings.add((new_row, new_col))
                        queue.append((new_row, new_col))
        
        # Update building states based on power
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                if self.grid[row][col] in [self.RESIDENTIAL, self.COMMERCIAL, self.INDUSTRIAL]:
                    if (row, col) in powered_buildings:
                        if self.building_states.get((row, col)) == self.ZONED_EMPTY:
                            self.building_states[(row, col)] = self.ZONED_DEVELOPING
                    else:
                        self.building_states[(row, col)] = self.ZONED_EMPTY
    
    def calculate_desirability(self, row, col):
        """Calculate desirability score for a zoned building"""
        if self.grid[row][col] not in [self.RESIDENTIAL, self.COMMERCIAL, self.INDUSTRIAL]:
            return 0
        
        score = 50  # Base desirability
        
        # Proximity to amenities
        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                distance = abs(row - r) + abs(col - c)  # Manhattan distance
                if distance == 0:
                    continue
                
                cell_type = self.grid[r][c]
                if cell_type == self.PARK:
                    score += max(0, 20 - distance * 5)  # Parks boost desirability
                elif cell_type == self.SCHOOL:
                    score += max(0, 15 - distance * 3)  # Schools boost desirability
                elif cell_type == self.HOSPITAL:
                    score += max(0, 10 - distance * 2)  # Hospitals boost desirability
                elif cell_type == self.POWER_PLANT:
                    score += max(0, 5 - distance)  # Power plants slightly boost desirability
                elif cell_type == self.INDUSTRIAL and self.grid[row][col] == self.RESIDENTIAL:
                    score -= max(0, 10 - distance * 2)  # Industrial near residential is bad
        
        # Road access bonus
        if (row, col) in self.road_network:
            score += 10
        
        # Power access bonus
        if (row, col) in self.power_network:
            score += 15
        
        # Traffic penalty
        traffic_level = self.traffic_levels.get((row, col), 0)
        score -= traffic_level * 2
        
        return max(0, min(100, score))
    
    def update_building_states(self):
        """Update building states based on operating conditions and desirability"""
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                if self.grid[row][col] in [self.RESIDENTIAL, self.COMMERCIAL, self.INDUSTRIAL]:
                    current_state = self.building_states.get((row, col), self.ZONED_EMPTY)
                    desirability = self.calculate_desirability(row, col)
                    self.desirability_scores[(row, col)] = desirability
                    
                    # Check if building has road and power access
                    has_road = (row, col) in self.road_network
                    has_power = (row, col) in self.power_network
                    
                    # Update state based on conditions
                    if has_road and has_power and desirability >= 60:
                        if current_state == self.ZONED_EMPTY:
                            self.building_states[(row, col)] = self.ZONED_DEVELOPING
                        elif current_state == self.ZONED_DEVELOPING:
                            self.building_states[(row, col)] = self.ZONED_OPERATING
                    elif desirability < 30:
                        self.building_states[(row, col)] = self.ZONED_ABANDONED
                    elif not has_road or not has_power:
                        self.building_states[(row, col)] = self.ZONED_EMPTY
    
    def calculate_traffic(self):
        """Calculate traffic levels based on commutes"""
        # Reset traffic levels
        self.traffic_levels = {}
        
        # Find all operating buildings
        operating_buildings = []
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                if (self.building_states.get((row, col)) == self.ZONED_OPERATING and
                    self.grid[row][col] in [self.RESIDENTIAL, self.COMMERCIAL, self.INDUSTRIAL]):
                    operating_buildings.append((row, col))
        
        # Calculate commutes and traffic
        for residential in operating_buildings:
            if self.grid[residential[0]][residential[1]] == self.RESIDENTIAL:
                # Find nearest commercial/industrial for work
                min_distance = float('inf')
                workplace = None
                
                for building in operating_buildings:
                    if self.grid[building[0]][building[1]] in [self.COMMERCIAL, self.INDUSTRIAL]:
                        distance = abs(residential[0] - building[0]) + abs(residential[1] - building[1])
                        if distance < min_distance:
                            min_distance = distance
                            workplace = building
                
                if workplace:
                    # Add traffic to road tiles along the path
                    self.add_traffic_to_path(residential, workplace)
    
    def add_traffic_to_path(self, start, end):
        """Add traffic to road tiles along a path"""
        # Simple pathfinding - move horizontally first, then vertically
        current = start
        while current != end:
            # Move towards target
            if current[1] < end[1]:  # Move right
                current = (current[0], current[1] + 1)
            elif current[1] > end[1]:  # Move left
                current = (current[0], current[1] - 1)
            elif current[0] < end[0]:  # Move down
                current = (current[0] + 1, current[1])
            elif current[0] > end[0]:  # Move up
                current = (current[0] - 1, current[1])
            
            # Add traffic to this cell if it's a road
            if current in self.road_network:
                self.traffic_levels[current] = self.traffic_levels.get(current, 0) + 1
    
    def calculate_daily_economy(self):
        """Calculate daily revenue and maintenance costs"""
        self.daily_revenue = 0
        self.daily_maintenance = 0
        
        # Revenue from operating buildings
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                if self.building_states.get((row, col)) == self.ZONED_OPERATING:
                    cell_type = self.grid[row][col]
                    if cell_type == self.RESIDENTIAL:
                        self.daily_revenue += 5  # Tax revenue
                    elif cell_type == self.COMMERCIAL:
                        self.daily_revenue += 15  # Commercial activity
                    elif cell_type == self.INDUSTRIAL:
                        self.daily_revenue += 20  # Industrial production
        
        # Maintenance costs
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                cell = self.grid[row][col]
                if cell:
                    daily_cost = self.MAINTENANCE_COSTS.get(cell, 0) / 365  # Daily cost
                    self.daily_maintenance += daily_cost
        
        # Apply daily economic changes
        net_daily = self.daily_revenue - self.daily_maintenance
        self.money += net_daily
        self.money = max(0, self.money)
    
    def trigger_disaster(self, disaster_type, row, col):
        """Trigger a disaster at a specific location"""
        if not self.is_valid_position(row, col):
            return False
        
        disaster = {
            'type': disaster_type,
            'row': row,
            'col': col,
            'severity': 1,
            'duration': 3,  # 3 days
            'remaining_duration': 3
        }
        
        self.disasters.append(disaster)
        
        # Apply immediate effects
        if disaster_type == 'fire':
            self.money -= 500
            self.happiness -= 5
        elif disaster_type == 'tornado':
            self.money -= 1000
            self.happiness -= 10
            # Destroy buildings in affected area
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    r, c = row + dr, col + dc
                    if self.is_valid_position(r, c) and self.grid[r][c]:
                        self.grid[r][c] = None
                        self.building_states.pop((r, c), None)
        
        logging.info(f"Disaster triggered: {disaster_type} at ({row}, {col})")
        return True
    
    def process_disasters(self):
        """Process ongoing disasters"""
        for disaster in self.disasters[:]:
            disaster['remaining_duration'] -= 1
            if disaster['remaining_duration'] <= 0:
                self.disasters.remove(disaster)
                logging.info(f"Disaster ended: {disaster['type']}")
            else:
                # Apply ongoing effects
                if disaster['type'] == 'fire':
                    self.money -= 100
                    self.happiness -= 2
                elif disaster['type'] == 'tornado':
                    self.money -= 200
                    self.happiness -= 3
