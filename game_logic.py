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
    
    # Grid size
    GRID_SIZE = 5
    
    def __init__(self):
        """Initialize a new city simulation"""
        self.grid = [[None for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.current_year = 1
        self.population = 0
        self.happiness = 50  # Start at neutral happiness
        
    def to_dict(self):
        """Convert city state to dictionary for session storage"""
        return {
            'grid': self.grid,
            'current_year': self.current_year,
            'population': self.population,
            'happiness': self.happiness
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create city from dictionary data"""
        city = cls()
        city.grid = data.get('grid', [[None for _ in range(cls.GRID_SIZE)] for _ in range(cls.GRID_SIZE)])
        city.current_year = data.get('current_year', 1)
        city.population = data.get('population', 0)
        city.happiness = data.get('happiness', 50)
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
        
        self.grid[row][col] = zone_type
        logging.info(f"Zoned cell ({row}, {col}) as {zone_type}")
        return True
    
    def build_structure(self, row, col, building_type):
        """Build a structure"""
        if not self.is_valid_position(row, col):
            logging.warning(f"Invalid position: ({row}, {col})")
            return False
            
        if not self.is_cell_empty(row, col):
            logging.warning(f"Cell ({row}, {col}) is already occupied")
            return False
        
        valid_buildings = [self.SCHOOL, self.HOSPITAL, self.POWER_PLANT, self.ROAD]
        if building_type not in valid_buildings:
            logging.warning(f"Invalid building type: {building_type}")
            return False
        
        self.grid[row][col] = building_type
        logging.info(f"Built {building_type} at cell ({row}, {col})")
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
    
    def advance_year(self):
        """Advance the city by one year and recalculate stats"""
        self.current_year += 1
        self.population = self.calculate_population()
        self.happiness = self.calculate_happiness()
        logging.info(f"Advanced to year {self.current_year}, Population: {self.population}, Happiness: {self.happiness}")
    
    def get_cell_display(self, row, col):
        """Get display string for a cell"""
        if not self.is_valid_position(row, col):
            return '?'
        
        cell = self.grid[row][col]
        if cell is None:
            return '.'
        elif cell in [self.RESIDENTIAL, self.COMMERCIAL, self.INDUSTRIAL, self.PARK]:
            return cell
        elif cell == self.SCHOOL:
            return 'S'
        elif cell == self.HOSPITAL:
            return 'H'
        elif cell == self.POWER_PLANT:
            return 'E'  # E for Energy/Electricity
        elif cell == self.ROAD:
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
        elif cell in [self.SCHOOL, self.HOSPITAL, self.POWER_PLANT, self.ROAD]:
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
            'empty_cells': sum(row.count(None) for row in self.grid)
        }
