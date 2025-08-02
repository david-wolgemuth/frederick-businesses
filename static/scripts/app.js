import { MapModule } from './modules/map.js';
import { GridModule } from './modules/grid.js';
import { ChartsModule } from './modules/charts.js';
import { DataProcessor } from './modules/dataProcessor.js';

class BusinessDirectoryApp {
    constructor() {
        this.mapModule = new MapModule();
        this.gridModule = new GridModule(this.mapModule);
        this.chartsModule = new ChartsModule();
        this.dataProcessor = new DataProcessor();
    }

    async initialize() {
        // Initialize the map first
        this.mapModule.initialize();
        
        // Initialize the grid
        this.gridModule.initialize();
        
        // Load and process data
        await this.loadData();
    }

    async loadData() {
        try {
            // Load and process data
            const data = await this.dataProcessor.loadData();
            
            // Share category colors and names across modules
            this.mapModule.setCategoryColors(data.categoryColors);
            this.gridModule.setCategoryColors(data.categoryColors);
            this.gridModule.setAllCategoryNames(data.allCategoryNames);
            this.chartsModule.setCategoryColors(data.categoryColors);
            
            // Set grid data
            this.gridModule.setRowData(data.processedBusinesses);
            
            // Create charts
            this.chartsModule.createAllCharts(data.processedBusinesses);
            
            // Update statistics
            this.dataProcessor.updateStats();
            
            // Hide loading and show grid
            document.getElementById('loading').style.display = 'none';
            document.getElementById('grid-section').style.display = 'block';
            
            // Setup interactions
            this.setupInteractions();
            
            // Force map resize after data loads
            setTimeout(() => {
                this.mapModule.invalidateSize();
            }, 500);
            
        } catch (error) {
            console.error('Error loading data:', error);
            document.getElementById('loading').textContent = 'Error loading data. Please try again later.';
        }
    }

    setupInteractions() {
        // Setup quick filter
        this.gridModule.setupQuickFilter();
        
        // Setup map integration with grid
        this.gridModule.setupMapIntegration();
        
        // Initial map update to show only first page
        this.gridModule.updateMapWithCurrentPage();
    }
}

// Initialize the application when the DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    const app = new BusinessDirectoryApp();
    app.initialize().catch(console.error);
});