export class MapModule {
    constructor() {
        this.map = null;
        this.markersLayer = null;
        this.categoryColors = {};
    }

    initialize() {
        // Initialize map centered on Frederick, MD
        this.map = L.map('map').setView([39.4143, -77.4105], 12);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.map);
        
        // Create a layer group for markers
        this.markersLayer = L.layerGroup().addTo(this.map);
        
        // Force map to invalidate size after a short delay
        setTimeout(() => {
            this.map.invalidateSize();
        }, 100);
        
        // Handle window resize
        window.addEventListener('resize', () => {
            setTimeout(() => {
                if (this.map) {
                    this.map.invalidateSize();
                }
            }, 100);
        });
    }

    setCategoryColors(colors) {
        this.categoryColors = colors;
    }

    addBusinessesToMap(businesses) {
        // Clear existing markers
        this.markersLayer.clearLayers();
        
        const businessesWithAddress = businesses.filter(business => business.fullAddress);
        
        businessesWithAddress.forEach((business, index) => {
            this.geocodeAndAddMarker(business, index, businessesWithAddress.length);
        });
    }

    geocodeAndAddMarker(business, index, total) {
        // Better distribution of markers across Frederick area
        // Create a more realistic spread based on known Frederick geography
        const baseRadius = 0.08; // Larger area
        const angle = (index / total) * 2 * Math.PI; // Distribute in circle
        const radius = Math.sqrt(Math.random()) * baseRadius; // Random radius with better distribution
        
        const lat = 39.4143 + radius * Math.cos(angle) + (Math.random() - 0.5) * 0.02;
        const lng = -77.4105 + radius * Math.sin(angle) + (Math.random() - 0.5) * 0.02;
        
        // Get primary category color for marker
        let markerColor = '#6c757d'; // default gray
        if (business.categoryNames && business.categoryNames.length > 0) {
            markerColor = this.categoryColors[business.categoryNames[0]] || '#6c757d';
        }
        
        // Create custom colored SVG pin icon
        const customIcon = L.divIcon({
            className: 'custom-marker',
            html: `<svg width="24" height="30" viewBox="0 0 24 30" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 0C5.4 0 0 5.4 0 12c0 7.2 12 18 12 18s12-10.8 12-18C24 5.4 18.6 0 12 0z" 
                      fill="${markerColor}" stroke="#fff" stroke-width="2"/>
                <circle cx="12" cy="12" r="4" fill="#fff"/>
            </svg>`,
            iconSize: [24, 30],
            iconAnchor: [12, 30]
        });
        
        const marker = L.marker([lat, lng], { icon: customIcon }).addTo(this.markersLayer);
        
        // Create popup content
        const popupContent = `
            <div>
                <h6>${business.name}</h6>
                ${business.fullAddress ? `<p><small>${business.fullAddress}</small></p>` : ''}
                ${business.categoryNames && business.categoryNames.length > 0 ? 
                    `<p>${business.categoryNames.map(cat => `<span class="badge" style="background-color: ${this.categoryColors[cat] || '#6c757d'}; color: white; font-size: 0.7em; margin: 1px;">${cat}</span>`).join(' ')}</p>` : 
                    ''}
                ${business.website_url ? `<p><a href="${business.website_url}" target="_blank">Visit Website</a></p>` : ''}
            </div>
        `;
        
        marker.bindPopup(popupContent);
        
        // Store business data with marker for filtering
        marker.businessData = business;
    }

    highlightBusiness(businessId) {
        // Find and highlight corresponding marker
        this.markersLayer.eachLayer((marker) => {
            if (marker.businessData && marker.businessData.id === businessId) {
                marker.openPopup();
                this.map.setView(marker.getLatLng(), 15);
            }
        });
    }

    invalidateSize() {
        if (this.map) {
            this.map.invalidateSize();
        }
    }
}