export class DataProcessor {
    constructor() {
        this.businesses = [];
        this.businessCategories = [];
        this.addresses = [];
        this.allCategoryNames = [];
        this.processedBusinesses = [];
        this.categoryColors = {};
        this.colorPalette = ["#f94144","#f3722c","#f8961e","#f9c74f","#90be6d","#43aa8b","#577590"];
    }

    async loadData() {
        try {
            // Fetch the YAML file
            const response = await fetch('./db.yaml');
            const yamlText = await response.text();
            
            // Parse YAML
            const data = jsyaml.load(yamlText);
            
            // Process the data
            this.processData(data);
            
            return {
                processedBusinesses: this.processedBusinesses,
                allCategoryNames: this.allCategoryNames,
                categoryColors: this.categoryColors,
                businesses: this.businesses,
                businessCategories: this.businessCategories,
                addresses: this.addresses
            };
            
        } catch (error) {
            console.error('Error loading data:', error);
            throw error;
        }
    }

    assignColorsToCategories() {
        // Shuffle the color palette to randomize assignment
        const shuffledColors = [...this.colorPalette];
        for (let i = shuffledColors.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffledColors[i], shuffledColors[j]] = [shuffledColors[j], shuffledColors[i]];
        }
        
        // Assign colors to categories, cycling through palette
        this.allCategoryNames.forEach((category, index) => {
            this.categoryColors[category] = shuffledColors[index % shuffledColors.length];
        });
    }

    processData(data) {
        // Separate data by model type
        this.addresses = data.filter(item => item.model === 'app.address');
        this.businessCategories = data.filter(item => item.model === 'app.businesscategory');
        this.businesses = data.filter(item => item.model === 'app.business');
        
        // Create lookup maps for efficiency
        const addressMap = {};
        this.addresses.forEach(addr => {
            addressMap[addr.pk] = addr.fields;
        });
        
        const categoryMap = {};
        this.businessCategories.forEach(cat => {
            categoryMap[cat.pk] = cat.fields;
        });
        
        // Process businesses data for the grid
        this.processedBusinesses = this.businesses.map(business => {
            const fields = business.fields;
            
            // Get address information
            let fullAddress = '';
            if (fields.address && addressMap[fields.address]) {
                const addr = addressMap[fields.address];
                const parts = [addr.street_1, addr.city, addr.state, addr.zip].filter(Boolean);
                fullAddress = parts.join(', ');
            }
            
            // Get category names
            const categoryNames = [];
            if (fields.categories && fields.categories.length > 0) {
                fields.categories.forEach(catId => {
                    if (categoryMap[catId]) {
                        const catName = categoryMap[catId].name;
                        categoryNames.push(catName);
                        // Collect all unique category names
                        if (!this.allCategoryNames.includes(catName)) {
                            this.allCategoryNames.push(catName);
                        }
                    }
                });
            }
            
            return {
                ...fields,
                id: business.pk,
                fullAddress: fullAddress,
                categoryNames: categoryNames
            };
        });
        
        // Sort category names alphabetically
        this.allCategoryNames.sort();
        
        // Assign random colors to categories
        this.assignColorsToCategories();
    }

    updateStats() {
        // Update stats
        document.getElementById('business-count').textContent = this.businesses.length.toLocaleString();
        document.getElementById('category-count').textContent = this.businessCategories.length.toLocaleString();
        
        // Find the most recent update date
        const allDates = [...this.businesses, ...this.businessCategories, ...this.addresses]
            .map(item => new Date(item.fields.updated_at || item.fields.created_at))
            .filter(date => !isNaN(date));
        
        if (allDates.length > 0) {
            const lastUpdate = new Date(Math.max(...allDates));
            document.getElementById('last-updated').textContent = lastUpdate.toLocaleDateString();
        }
    }
}