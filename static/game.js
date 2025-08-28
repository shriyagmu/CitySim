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
    }

    getCellTypeName(symbol) {
        const typeMap = {
            '.': 'Empty',
            'R': 'Residential',
            'C': 'Commercial', 
            'I': 'Industrial',
            'P': 'Park',
            'S': 'School',
            'H': 'Hospital',
            'E': 'Power Plant',
            '#': 'Road'
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
});

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
