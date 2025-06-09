// Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    let currentCity = document.getElementById('city-selector').value;
    let charts = {};
    
    // Initialize dashboard
    initializeDashboard();
    
    // Event listeners
    document.getElementById('city-selector').addEventListener('change', function(e) {
        currentCity = e.target.value;
        updateDashboard();
    });
    
    // Initialize dashboard components
    function initializeDashboard() {
        updateAQIDisplay();
        initializeCharts();
        updateAlerts();
    }
    
    // Update AQI display
    async function updateAQIDisplay() {
        try {
            const response = await fetch(`/api/latest/${currentCity}`);
            const data = await response.json();
            
            if (data.error) {
                showError('AQI Display', data.error);
                return;
            }
            
            const aqiDisplay = document.getElementById('aqi-display');
            aqiDisplay.innerHTML = `
                <div class="aqi-value" style="color: ${data.alert.color}">
                    ${Math.round(data.aqi)}
                </div>
                <div class="aqi-label">
                    ${data.alert.level}
                </div>
            `;
        } catch (error) {
            showError('AQI Display', 'Failed to fetch AQI data');
        }
    }
    
    // Initialize charts
    function initializeCharts() {
        const parameters = ['PM2.5', 'PM10', 'O3', 'NO2', 'SO2', 'CO'];
        
        parameters.forEach(param => {
            const chartId = `${param.toLowerCase()}-chart`;
            const chartContainer = document.getElementById(chartId);
            
            if (chartContainer) {
                const ctx = chartContainer.getContext('2d');
                charts[param] = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: param,
                            data: [],
                            borderColor: getParameterColor(param),
                            backgroundColor: getParameterColor(param) + '20',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                mode: 'index',
                                intersect: false
                            }
                        },
                        scales: {
                            x: {
                                type: 'time',
                                time: {
                                    unit: 'day',
                                    displayFormats: {
                                        day: 'MMM d'
                                    }
                                },
                                grid: {
                                    display: false
                                }
                            },
                            y: {
                                beginAtZero: true,
                                grid: {
                                    color: '#f0f0f0'
                                }
                            }
                        }
                    }
                });
            }
        });
        
        updateCharts();
    }
    
    // Update charts with new data
    async function updateCharts() {
        try {
            const response = await fetch(`/api/historical/${currentCity}`);
            const data = await response.json();
            
            if (data.error) {
                showError('Charts', data.error);
                return;
            }
            
            // Process data for each parameter
            const parameters = ['PM2.5', 'PM10', 'O3', 'NO2', 'SO2', 'CO'];
            
            parameters.forEach(param => {
                if (charts[param]) {
                    const paramData = data.data.filter(d => d.parameter === param);
                    
                    charts[param].data.labels = paramData.map(d => new Date(d.timestamp));
                    charts[param].data.datasets[0].data = paramData.map(d => d.value);
                    charts[param].update();
                }
            });
        } catch (error) {
            showError('Charts', 'Failed to update charts');
        }
    }
    
    // Update alerts
    async function updateAlerts() {
        try {
            const response = await fetch(`/api/latest/${currentCity}`);
            const data = await response.json();
            
            if (data.error) {
                showError('Alerts', data.error);
                return;
            }
            
            const alertsContainer = document.getElementById('alerts-container');
            alertsContainer.innerHTML = `
                <div class="alert alert-${data.alert.level.toLowerCase()}">
                    <h3>${data.alert.level}</h3>
                    <p>${data.alert.message}</p>
                </div>
            `;
        } catch (error) {
            showError('Alerts', 'Failed to update alerts');
        }
    }
    
    // Update entire dashboard
    function updateDashboard() {
        updateAQIDisplay();
        updateCharts();
        updateAlerts();
    }
    
    // Helper function to get parameter color
    function getParameterColor(parameter) {
        const colors = {
            'PM2.5': '#1f77b4',
            'PM10': '#ff7f0e',
            'O3': '#2ca02c',
            'NO2': '#d62728',
            'SO2': '#9467bd',
            'CO': '#8c564b'
        };
        return colors[parameter] || '#000000';
    }
    
    // Show error message
    function showError(component, message) {
        console.error(`${component} Error:`, message);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-error';
        errorDiv.innerHTML = `
            <h3>Error</h3>
            <p>${message}</p>
        `;
        document.querySelector('.container').prepend(errorDiv);
        
        // Remove error message after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
    
    // Auto-refresh dashboard every 5 minutes
    setInterval(updateDashboard, 300000);
}); 