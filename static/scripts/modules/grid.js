export class GridModule {
    constructor(mapModule) {
        this.gridApi = null;
        this.mapModule = mapModule;
        this.categoryColors = {};
        this.allCategoryNames = [];
    }

    setCategoryColors(colors) {
        this.categoryColors = colors;
    }

    setAllCategoryNames(names) {
        this.allCategoryNames = names;
    }

    getColumnDefinitions() {
        return [
            {
                field: "name",
                headerName: "Business Name",
                filter: true,
                sortable: true,
                flex: 3,
                cellRenderer: (params) => this.businessNameRenderer(params)
            },
            {
                field: "categoryNames",
                headerName: "Categories",
                filter: 'agSetColumnFilter',
                filterParams: {
                    excelMode: 'mac',
                    values: () => this.allCategoryNames
                },
                flex: 2,
                valueFormatter: (params) => this.categoryValueFormatter(params),
                cellRenderer: (params) => this.categoryRenderer(params)
            },
            {
                field: "fullAddress",
                headerName: "Address",
                filter: true,
                flex: 2,
                hide: true
            },
            {
                field: "number_of_employees",
                headerName: "Employees",
                filter: 'agNumberColumnFilter',
                sortable: true,
                width: 130,
                cellRenderer: (params) => this.employeeRenderer(params)
            },
            {
                field: "phone_numbers",
                headerName: "Phone",
                filter: true,
                width: 150,
                hide: true,
                valueFormatter: (params) => this.phoneValueFormatter(params),
                cellRenderer: (params) => this.phoneRenderer(params)
            }
        ];
    }


    businessNameRenderer(params) {
        if (params.data.website_url) {
            return `<a href="${params.data.website_url}" target="_blank" class="cell-link">${params.value}</a>`;
        }
        return params.value;
    }

    categoryValueFormatter(params) {
        if (params.value && Array.isArray(params.value) && params.value.length > 0) {
            return params.value.join(', ');
        }
        return '';
    }

    categoryRenderer(params) {
        if (params.value && Array.isArray(params.value) && params.value.length > 0) {
            return params.value.map(cat =>
                `<span class="badge category-tag" style="background-color: ${this.categoryColors[cat] || '#6c757d'}; color: white;">${cat}</span>`
            ).join(' ');
        }
        return '';
    }

    employeeRenderer(params) {
        if (params.value) {
            return params.value.toLocaleString();
        }
        return '';
    }

    phoneValueFormatter(params) {
        if (params.value && Array.isArray(params.value) && params.value.length > 0) {
            return params.value[0];
        }
        return '';
    }

    phoneRenderer(params) {
        if (params.value && Array.isArray(params.value) && params.value.length > 0) {
            return params.value[0];
        }
        return '';
    }

    initialize() {
        // Grid options
        const gridOptions = {
            columnDefs: this.getColumnDefinitions(),
            defaultColDef: {
                resizable: true,
                sortable: true,
                filter: true
            },
            pagination: true,
            paginationPageSize: 50,
            paginationPageSizeSelector: [25, 50, 100, 200],
            rowSelection: 'single',
            animateRows: true,
            sortingOrder: ['desc', 'asc'],
            suppressColumnVirtualisation: true
        };

        // Initialize the grid
        const gridDiv = document.querySelector('#myGrid');
        this.gridApi = agGrid.createGrid(gridDiv, gridOptions);
    }

    setRowData(data) {
        this.gridApi.setGridOption('rowData', data);
        
        // Apply initial sort by employee count (descending)
        this.gridApi.applyColumnState({
            state: [{ colId: 'number_of_employees', sort: 'desc' }]
        });
    }

    setupQuickFilter() {
        const quickFilterInput = document.getElementById('quickFilter');

        quickFilterInput.addEventListener('input', (e) => {
            this.gridApi.setGridOption('quickFilterText', e.target.value);
        });

        // Clear search with Escape key
        quickFilterInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                e.target.value = '';
                this.gridApi.setGridOption('quickFilterText', '');
            }
        });
    }

    setupMapIntegration() {
        // Add row selection listener to highlight corresponding map marker
        this.gridApi.addEventListener('rowClicked', (event) => {
            const business = event.data;
            this.mapModule.highlightBusiness(business.id);
        });

        // Listen for pagination changes
        this.gridApi.addEventListener('paginationChanged', () => {
            this.updateMapWithCurrentPage();
        });

        // Listen for filter changes
        this.gridApi.addEventListener('filterChanged', () => {
            this.updateMapWithCurrentPage();
        });

        // Listen for sort changes
        this.gridApi.addEventListener('sortChanged', () => {
            this.updateMapWithCurrentPage();
        });
    }

    updateMapWithCurrentPage() {
        if (!this.gridApi) return;

        // Get the currently displayed rows from the grid
        const displayedRows = [];
        this.gridApi.forEachNodeAfterFilterAndSort((node, index) => {
            // Only get nodes that are currently visible on the current page
            const currentPage = this.gridApi.paginationGetCurrentPage();
            const pageSize = this.gridApi.paginationGetPageSize();
            const startIndex = currentPage * pageSize;
            const endIndex = startIndex + pageSize;

            if (index >= startIndex && index < endIndex) {
                displayedRows.push(node.data);
            }
        });

        this.mapModule.addBusinessesToMap(displayedRows);
    }
}