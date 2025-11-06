// City Simulation Game JavaScript

class CityGame {
    constructor() {
        this.selectedCell = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateGridColors();
    }

    bindEvents() {
        // Grid cell click events
        document.querySelectorAll('.grid-cell').forEach(cell => {
            cell.addEventListener('click', (e) => this.selectCell(e.target.closest('.grid-cell')));
        });

        // Zone buttons
        document.querySelectorAll('.zone-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.zoneCell(e.target.dataset.zone));
        });

        // Build buttons
        document.querySelectorAll('.build-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.buildStructure(e.target.dataset.building));
        });

        // 2x2 Zone buttons
        document.querySelectorAll('.zone-2x2-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.zone2x2Cell(e.target.dataset.zone));
        });

        // Infrastructure buttons
        document.querySelectorAll('.road-btn').forEach(btn => {
            btn.addEventListener('click', () => this.buildRoad());
        });

        document.querySelectorAll('.power-line-btn').forEach(btn => {
            btn.addEventListener('click', () => this.buildPowerLine());
        });

        // Disaster buttons
        document.querySelectorAll('.disaster-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.triggerDisaster(e.target.dataset.disaster));
        });

        // Clear button
        document.getElementById('clearCellBtn').addEventListener('click', () => this.clearCell());

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    selectCell(cell) {
        // Remove previous selection
        document.querySelectorAll('.grid-cell').forEach(c => c.classList.remove('selected'));
        
        // Select new cell
        cell.classList.add('selected');
        this.selectedCell = {
            row: parseInt(cell.dataset.row),
            col: parseInt(cell.dataset.col),
            element: cell
        };

        // Update cell info panel
        this.updateCellInfo();
        
        // Show cell info card
        document.getElementById('cellInfoCard').style.display = 'block';
    }

    updateCellInfo() {
        if (!this.selectedCell) return;

        const { row, col, element } = this.selectedCell;
        const cellContent = element.querySelector('.cell-content').textContent;
        const cellName = this.getCellTypeName(cellContent);
        
        const cellInfoDiv = document.getElementById('cellInfo');
        cellInfoDiv.innerHTML = `
            <div class="text-center">
                <h6>Cell (${row}, ${col})</h6>
                <p class="text-muted mb-0">Current: <strong>${cellName}</strong></p>
            </div>
        `;
        
        // Update button states based on affordability
        this.updateButtonStates();
    }
    
    updateButtonStates() {
        // Get current money from the page
        const moneyElement = document.querySelector('.h4.text-info');
        const currentMoney = moneyElement ? parseInt(moneyElement.textContent.replace('$', '').replace(',', '')) : 0;
        
        // Update zone buttons
        document.querySelectorAll('.zone-btn').forEach(btn => {
            const zone = btn.dataset.zone;
            const cost = this.getZoneCost(zone);
            const canAfford = currentMoney >= cost;
            
            btn.disabled = !canAfford;
            btn.classList.toggle('disabled', !canAfford);
            
            if (!canAfford) {
                btn.title = `Cost: $${cost} (Insufficient funds)`;
            }
        });
        
        // Update 2x2 zone buttons
        document.querySelectorAll('.zone-2x2-btn').forEach(btn => {
            const zone = btn.dataset.zone;
            const cost = this.getZoneCost(zone) * 4; // 2x2 costs 4x as much
            const canAfford = currentMoney >= cost;
            
            btn.disabled = !canAfford;
            btn.classList.toggle('disabled', !canAfford);
            
            if (!canAfford) {
                btn.title = `Cost: $${cost} (Insufficient funds)`;
            }
        });
        
        // Update build buttons
        document.querySelectorAll('.build-btn').forEach(btn => {
            const building = btn.dataset.building;
            const cost = this.getBuildingCost(building);
            const canAfford = currentMoney >= cost;
            
            btn.disabled = !canAfford;
            btn.classList.toggle('disabled', !canAfford);
            
            if (!canAfford) {
                btn.title = `Cost: $${cost} (Insufficient funds)`;
            }
        });

        // Update infrastructure buttons
        document.querySelectorAll('.road-btn').forEach(btn => {
            const canAfford = currentMoney >= 200;
            btn.disabled = !canAfford;
            btn.classList.toggle('disabled', !canAfford);
        });

        document.querySelectorAll('.power-line-btn').forEach(btn => {
            const canAfford = currentMoney >= 100;
            btn.disabled = !canAfford;
            btn.classList.toggle('disabled', !canAfford);
        });
    }
    
    getZoneCost(zone) {
        const costs = {
            'R': 500,
            'C': 800,
            'I': 1000,
            'P': 300
        };
        return costs[zone] || 0;
    }
    
    getBuildingCost(building) {
        const costs = {
            'School': 2000,
            'Hospital': 3000,
            'Power': 2500,
            'Road': 200,
            'Police': 4000,
            'Fire': 3500,
            'Mall': 6000,
            'Stadium': 8000,
            'University': 10000,
            'Airport': 15000
        };
        return costs[building] || 0;
    }

    getCellTypeName(symbol) {
        const typeMap = {
            '.': 'Empty',
            'R': 'Residential (Empty)',
            'r': 'Residential (Operating)',
            'Rd': 'Residential (Developing)',
            'Ra': 'Residential (Abandoned)',
            'C': 'Commercial (Empty)',
            'c': 'Commercial (Operating)',
            'Cd': 'Commercial (Developing)',
            'Ca': 'Commercial (Abandoned)',
            'I': 'Industrial (Empty)',
            'i': 'Industrial (Operating)',
            'Id': 'Industrial (Developing)',
            'Ia': 'Industrial (Abandoned)',
            'P': 'Park',
            'S': 'School',
            'H': 'Hospital',
            'E': 'Power Plant',
            '|': 'Power Line',
            '─': 'Road (Horizontal)',
            '│': 'Road (Vertical)',
            '┼': 'Road (Cross)',
            '┴': 'Road (T-Up)',
            '┬': 'Road (T-Down)',
            '┤': 'Road (T-Left)',
            '├': 'Road (T-Right)',
            '┘': 'Road (Corner UL)',
            '└': 'Road (Corner UR)',
            '┐': 'Road (Corner DL)',
            '┌': 'Road (Corner DR)',
            '#': 'Road (Isolated)',
            'L': 'Police Station',
            'F': 'Fire Station',
            'A': 'Airport',
            'T': 'Stadium',
            'M': 'Mall',
            'U': 'University'
        };
        return typeMap[symbol] || 'Unknown';
    }

    zoneCell(zoneType) {
        if (!this.selectedCell) {
            this.showMessage('Please select a cell first', 'warning');
            return;
        }

        // Set form values
        document.getElementById('zoneRow').value = this.selectedCell.row;
        document.getElementById('zoneCol').value = this.selectedCell.col;
        document.getElementById('zoneType').value = zoneType;
        
        // Submit form
        document.getElementById('zoneForm').submit();
    }

    buildStructure(buildingType) {
        if (!this.selectedCell) {
            this.showMessage('Please select a cell first', 'warning');
            return;
        }

        // Set form values
        document.getElementById('buildRow').value = this.selectedCell.row;
        document.getElementById('buildCol').value = this.selectedCell.col;
        document.getElementById('buildingType').value = buildingType;
        
        // Submit form
        document.getElementById('buildForm').submit();
    }

    clearCell() {
        if (!this.selectedCell) {
            this.showMessage('Please select a cell first', 'warning');
            return;
        }

        // Set form values
        document.getElementById('clearRow').value = this.selectedCell.row;
        document.getElementById('clearCol').value = this.selectedCell.col;
        
        // Submit form
        document.getElementById('clearForm').submit();
    }

    zone2x2Cell(zoneType) {
        if (!this.selectedCell) {
            this.showMessage('Please select a cell first', 'warning');
            return;
        }

        // Check if 2x2 block fits
        const { row, col } = this.selectedCell;
        if (row > 3 || col > 3) {
            this.showMessage('2x2 block must fit within grid (select top-left corner)', 'warning');
            return;
        }

        // Set form values
        document.getElementById('zone2x2Row').value = row;
        document.getElementById('zone2x2Col').value = col;
        document.getElementById('zone2x2Type').value = zoneType;
        
        // Submit form
        document.getElementById('zone2x2Form').submit();
    }

    buildRoad() {
        if (!this.selectedCell) {
            this.showMessage('Please select a cell first', 'warning');
            return;
        }

        // Set form values
        document.getElementById('roadRow').value = this.selectedCell.row;
        document.getElementById('roadCol').value = this.selectedCell.col;
        
        // Submit form
        document.getElementById('roadForm').submit();
    }

    buildPowerLine() {
        if (!this.selectedCell) {
            this.showMessage('Please select a cell first', 'warning');
            return;
        }

        // Set form values
        document.getElementById('powerLineRow').value = this.selectedCell.row;
        document.getElementById('powerLineCol').value = this.selectedCell.col;
        
        // Submit form
        document.getElementById('powerLineForm').submit();
    }

    triggerDisaster(disasterType) {
        if (!this.selectedCell) {
            this.showMessage('Please select a cell first', 'warning');
            return;
        }

        if (!confirm(`Trigger ${disasterType} disaster at (${this.selectedCell.row}, ${this.selectedCell.col})?`)) {
            return;
        }

        // Set form values
        document.getElementById('disasterRow').value = this.selectedCell.row;
        document.getElementById('disasterCol').value = this.selectedCell.col;
        document.getElementById('disasterType').value = disasterType;
        
        // Submit form
        document.getElementById('disasterForm').submit();
    }

    updateGridColors() {
        document.querySelectorAll('.grid-cell').forEach(cell => {
            const content = cell.querySelector('.cell-content').textContent;
            
            // Remove existing type classes
            cell.classList.remove('type-empty', 'type-residential', 'type-commercial', 
                              'type-industrial', 'type-park', 'type-building');

            // Add appropriate class based on content
            switch(content) {
                case '.':
                    cell.classList.add('type-empty');
                    break;
                case 'R':
                    cell.dataset.type = 'R';
                    break;
                case 'C':
                    cell.dataset.type = 'C';
                    break;
                case 'I':
                    cell.dataset.type = 'I';
                    break;
                case 'P':
                    cell.dataset.type = 'P';
                    break;
                case 'S':
                    cell.dataset.type = 'School';
                    break;
                case 'H':
                    cell.dataset.type = 'Hospital';
                    break;
                case 'E':
                    cell.dataset.type = 'Power';
                    break;
                case '#':
                    cell.dataset.type = 'Road';
                    break;
            }
        });
    }

    handleKeyboard(event) {
        if (!this.selectedCell) return;

        // Movement keys
        const { row, col } = this.selectedCell;
        let newRow = row;
        let newCol = col;

        switch(event.key) {
            case 'ArrowUp':
                newRow = Math.max(0, row - 1);
                break;
            case 'ArrowDown':
                newRow = Math.min(4, row + 1);
                break;
            case 'ArrowLeft':
                newCol = Math.max(0, col - 1);
                break;
            case 'ArrowRight':
                newCol = Math.min(4, col + 1);
                break;
            case 'Delete':
            case 'Backspace':
                this.clearCell();
                return;
            // Zone hotkeys
            case 'r':
            case 'R':
                this.zoneCell('R');
                return;
            case 'c':
            case 'C':
                this.zoneCell('C');
                return;
            case 'i':
            case 'I':
                this.zoneCell('I');
                return;
            case 'p':
            case 'P':
                this.zoneCell('P');
                return;
            // Building hotkeys
            case 's':
            case 'S':
                this.buildStructure('School');
                return;
            case 'h':
            case 'H':
                this.buildStructure('Hospital');
                return;
            case 'e':
            case 'E':
                this.buildStructure('Power');
                return;
            case '#':
                this.buildStructure('Road');
                return;
            default:
                return; // Don't prevent default for other keys
        }

        // If we're moving, prevent default and select new cell
        if (newRow !== row || newCol !== col) {
            event.preventDefault();
            const newCell = document.querySelector(`[data-row="${newRow}"][data-col="${newCol}"]`);
            if (newCell) {
                this.selectCell(newCell);
            }
        }
    }

    showMessage(message, type = 'info') {
        // Create a temporary alert (since we're not using AJAX, this is mainly for client-side validation)
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        const firstRow = container.querySelector('.row');
        container.insertBefore(alertDiv, firstRow);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }
}

// Initialize game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CityGame();
    loadSaveList(); // Load available saves
});

// Save/Load functions
function saveCity() {
    const saveName = document.getElementById('saveName').value.trim();
    if (!saveName) {
        alert('Please enter a city name');
        return;
    }
    
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/save_city';
    
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'save_name';
    input.value = saveName;
    
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
}

function loadCity() {
    const saveName = document.getElementById('loadSelect').value;
    if (!saveName) {
        alert('Please select a save file');
        return;
    }
    
    if (confirm(`Load city "${saveName}"? This will replace your current city.`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/load_city';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'save_name';
        input.value = saveName;
        
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    }
}

function loadSaveList() {
    fetch('/list_saves')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('loadSelect');
            select.innerHTML = '<option value="">Select save file...</option>';
            
            data.saves.forEach(save => {
                const option = document.createElement('option');
                option.value = save.name;
                option.textContent = `${save.name} (Year ${save.year}, Pop: ${save.population}, $${Math.round(save.money)})`;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading save list:', error);
        });
}

// Add some helpful tooltips and enhanced UX
document.addEventListener('DOMContentLoaded', () => {
    // Enhanced tooltips for better UX
    const tooltips = {
        'R': 'Residential zones house your population. Each zone can hold up to 100 people.',
        'C': 'Commercial zones provide jobs (50 per zone) and services for your citizens.',
        'I': 'Industrial zones provide jobs (75 per zone) but reduce happiness slightly.',
        'P': 'Parks significantly boost citizen happiness and provide recreation.',
        'S': 'Schools boost happiness and provide education services.',
        'H': 'Hospitals boost happiness and provide healthcare services.',
        'E': 'Power plants provide essential electricity and boost happiness.',
        '#': 'Roads improve city infrastructure and connectivity.'
    };

    // Update tooltips with more detailed information
    document.querySelectorAll('.grid-cell').forEach(cell => {
        const content = cell.querySelector('.cell-content').textContent;
        const baseTitle = cell.title;
        
        if (tooltips[content]) {
            cell.title = `${baseTitle}\n\n${tooltips[content]}`;
        }
    });
});
