export class ChartsModule {
    constructor() {
        this.categoryColors = {};
        this.colorPalette = ["#f94144","#f3722c","#f8961e","#f9c74f","#90be6d","#43aa8b","#577590"];
    }

    setCategoryColors(colors) {
        this.categoryColors = colors;
    }

    createAllCharts(businesses) {
        this.createCategoryChart(businesses);
        this.createEmployeeChart(businesses);
        this.createAddressChart(businesses);
    }

    createCategoryChart(businesses) {
        // Count businesses by category
        const categoryCount = {};
        businesses.forEach(business => {
            if (business.categoryNames && business.categoryNames.length > 0) {
                business.categoryNames.forEach(category => {
                    categoryCount[category] = (categoryCount[category] || 0) + 1;
                });
            }
        });
        
        // Get top 10 categories
        const topCategories = Object.entries(categoryCount)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);
        
        // Set dimensions
        const margin = {top: 10, right: 10, bottom: 80, left: 40};
        const width = 300 - margin.left - margin.right;
        const height = 200 - margin.bottom - margin.top;
        
        // Create SVG
        const svg = d3.select('#category-chart')
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
        
        // Create scales
        const xScale = d3.scaleBand()
            .domain(topCategories.map(d => d[0]))
            .range([0, width])
            .padding(0.1);
        
        const yScale = d3.scaleLinear()
            .domain([0, d3.max(topCategories, d => d[1])])
            .range([height, 0]);
        
        // Create bars
        svg.selectAll('.bar')
            .data(topCategories)
            .enter().append('rect')
            .attr('class', 'bar')
            .attr('x', d => xScale(d[0]))
            .attr('width', xScale.bandwidth())
            .attr('y', d => yScale(d[1]))
            .attr('height', d => height - yScale(d[1]))
            .style('fill', d => this.categoryColors[d[0]] || this.colorPalette[0]);
        
        // Add x-axis
        svg.append('g')
            .attr('class', 'axis')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(xScale))
            .selectAll('text')
            .style('text-anchor', 'end')
            .attr('dx', '-.8em')
            .attr('dy', '.15em')
            .attr('transform', 'rotate(-45)');
        
        // Add y-axis
        svg.append('g')
            .attr('class', 'axis')
            .call(d3.axisLeft(yScale));
    }
    
    createEmployeeChart(businesses) {
        // Group businesses by employee count ranges
        const employeeRanges = {
            '1-10': 0,
            '11-50': 0,
            '51-100': 0,
            '101-500': 0,
            '500+': 0,
            'Unknown': 0
        };
        
        businesses.forEach(business => {
            const count = business.number_of_employees;
            if (!count) {
                employeeRanges['Unknown']++;
            } else if (count <= 10) {
                employeeRanges['1-10']++;
            } else if (count <= 50) {
                employeeRanges['11-50']++;
            } else if (count <= 100) {
                employeeRanges['51-100']++;
            } else if (count <= 500) {
                employeeRanges['101-500']++;
            } else {
                employeeRanges['500+']++;
            }
        });
        
        const data = Object.entries(employeeRanges).filter(d => d[1] > 0);
        
        // Set dimensions
        const width = 300;
        const height = 200;
        const radius = Math.min(width, height) / 2 - 10;
        
        // Create SVG
        const svg = d3.select('#employee-chart')
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .append('g')
            .attr('transform', `translate(${width/2},${height/2})`);
        
        // Create color scale
        const color = d3.scaleOrdinal()
            .domain(data.map(d => d[0]))
            .range(this.colorPalette);
        
        // Create pie generator
        const pie = d3.pie().value(d => d[1]);
        const arc = d3.arc().innerRadius(0).outerRadius(radius);
        
        // Create pie slices
        svg.selectAll('.arc')
            .data(pie(data))
            .enter().append('g')
            .attr('class', 'arc')
            .append('path')
            .attr('d', arc)
            .style('fill', d => color(d.data[0]));
        
        // Add labels
        svg.selectAll('.arc')
            .append('text')
            .attr('transform', d => `translate(${arc.centroid(d)})`)
            .attr('dy', '.35em')
            .style('text-anchor', 'middle')
            .style('font-size', '11px')
            .text(d => d.data[1] > 5 ? d.data[0] : '');
    }
    
    createAddressChart(businesses) {
        // Count businesses by city
        const cityCount = {};
        businesses.forEach(business => {
            if (business.fullAddress) {
                // Extract city from address (simple approach)
                const parts = business.fullAddress.split(', ');
                if (parts.length >= 2) {
                    const city = parts[1] || 'Unknown';
                    cityCount[city] = (cityCount[city] || 0) + 1;
                }
            }
        });
        
        // Get top cities
        const topCities = Object.entries(cityCount)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 8);
        
        // Set dimensions
        const margin = {top: 10, right: 10, bottom: 60, left: 40};
        const width = 300 - margin.left - margin.right;
        const height = 150 - margin.bottom - margin.top;
        
        // Create SVG
        const svg = d3.select('#address-chart')
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
        
        // Create scales
        const xScale = d3.scaleBand()
            .domain(topCities.map(d => d[0]))
            .range([0, width])
            .padding(0.1);
        
        const yScale = d3.scaleLinear()
            .domain([0, d3.max(topCities, d => d[1])])
            .range([height, 0]);
        
        // Create bars
        svg.selectAll('.bar')
            .data(topCities)
            .enter().append('rect')
            .attr('class', 'bar')
            .attr('x', d => xScale(d[0]))
            .attr('width', xScale.bandwidth())
            .attr('y', d => yScale(d[1]))
            .attr('height', d => height - yScale(d[1]))
            .style('fill', (d, i) => this.colorPalette[i % this.colorPalette.length]);
        
        // Add x-axis
        svg.append('g')
            .attr('class', 'axis')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(xScale))
            .selectAll('text')
            .style('text-anchor', 'end')
            .attr('dx', '-.8em')
            .attr('dy', '.15em')
            .attr('transform', 'rotate(-45)');
        
        // Add y-axis
        svg.append('g')
            .attr('class', 'axis')
            .call(d3.axisLeft(yScale));
    }
}