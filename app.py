"""
AirAware - Urban Air Quality Monitoring Dashboard
Flask Application Server
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
import json
from datetime import datetime, timedelta
import os
from utils import fetch_air_quality_data, process_historical_data, generate_forecast, AirQualityData
from config import Config
from flask_caching import Cache

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize cache
cache = Cache(app)

# Initialize AirQualityData
air_quality = AirQualityData(app.config['OPENAQ_API_KEY'])

# African cities with their coordinates
CITIES = {
    'nairobi': {
        'name': 'Nairobi, Kenya',
        'lat': -1.2921,
        'lon': 36.8219,
        'country': 'KE'
    },
    'mombasa': {
        'name': 'Mombasa, Kenya',
        'lat': -4.0435,
        'lon': 39.6682,
        'country': 'KE'
    },
    'kisumu': {
        'name': 'Kisumu, Kenya',
        'lat': -0.0917,
        'lon': 34.7680,
        'country': 'KE'
    },
    'nakuru': {
        'name': 'Nakuru, Kenya',
        'lat': -0.3031,
        'lon': 36.0800,
        'country': 'KE'
    },
    'eldoret': {
        'name': 'Eldoret, Kenya',
        'lat': 0.5143,
        'lon': 35.2698,
        'country': 'KE'
    },
    'lagos': {
        'name': 'Lagos, Nigeria',
        'lat': 6.5244,
        'lon': 3.3792,
        'country': 'NG'
    },
    'cairo': {
        'name': 'Cairo, Egypt',
        'lat': 30.0444,
        'lon': 31.2357,
        'country': 'EG'
    },
    'capetown': {
        'name': 'Cape Town, South Africa',
        'lat': -33.9249,
        'lon': 18.4241,
        'country': 'ZA'
    },
    'addis': {
        'name': 'Addis Ababa, Ethiopia',
        'lat': 9.1450,
        'lon': 40.4897,
        'country': 'ET'
    },
    'johannesburg': {
        'name': 'Johannesburg, South Africa',
        'lat': -26.2041,
        'lon': 28.0473,
        'country': 'ZA'
    },
    'casablanca': {
        'name': 'Casablanca, Morocco',
        'lat': 33.5722,
        'lon': -7.5898,
        'country': 'MA'
    },
    'accra': {
        'name': 'Accra, Ghana',
        'lat': 5.6037,
        'lon': -0.1870,
        'country': 'GH'
    }
}

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html', 
                         cities=Config.SUPPORTED_CITIES,
                         default_city=Config.DEFAULT_CITY)

@app.route('/api/latest/<city>')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_latest_data(city):
    """Get latest air quality data for a city."""
    try:
        data = air_quality.get_latest_measurements(city)
        if data.empty:
            return jsonify({'error': 'No data available'}), 404
        
        aqi = air_quality.calculate_aqi(data)
        alert = air_quality.generate_alert(aqi)
        
        return jsonify({
            'aqi': aqi,
            'alert': alert,
            'measurements': data.to_dict('records')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/historical/<city>')
@cache.cached(timeout=3600)  # Cache for 1 hour
def get_historical_data(city):
    """Get historical air quality data for a city."""
    try:
        days = request.args.get('days', default=30, type=int)
        data = air_quality.get_historical_data(city, days)
        if data.empty:
            return jsonify({'error': 'No data available'}), 404
        
        return jsonify({
            'data': data.to_dict('records')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/forecast/<city>')
@cache.cached(timeout=1800)  # Cache for 30 minutes
def get_forecast(city):
    """Get air quality forecast for a city."""
    try:
        historical_data = air_quality.get_historical_data(city, Config.MAX_HISTORICAL_DAYS)
        if historical_data.empty:
            return jsonify({'error': 'No data available for forecasting'}), 404
        
        forecast = air_quality.predict_aqi(historical_data, Config.FORECAST_HOURS)
        return jsonify({
            'forecast': forecast.to_dict('records')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart/<city>')
@cache.cached(timeout=1800)  # Cache for 30 minutes
def get_chart_data(city):
    """Get chart data for a specific parameter in a city."""
    try:
        parameter = request.args.get('parameter', default='PM2.5')
        days = request.args.get('days', default=7, type=int)
        
        data = air_quality.get_historical_data(city, days)
        if data.empty:
            return jsonify({'error': 'No data available'}), 404
        
        chart = air_quality.create_trend_chart(data, parameter)
        return jsonify({
            'chart': json.loads(chart.to_json())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cities')
def get_all_cities():
    """Get list of all available cities"""
    return jsonify(CITIES)

@app.route('/api/alerts/<city>')
def get_alerts(city):
    """Get air quality alerts for a city"""
    try:
        if city not in CITIES:
            return jsonify({'error': 'City not found'}), 404
        
        city_info = CITIES[city]
        current_data = fetch_air_quality_data(
            city_info['lat'],
            city_info['lon'],
            city_info['name']
        )
        
        alerts = []
        aqi = current_data.get('aqi', 0)
        
        if aqi > 150:
            alerts.append({
                'level': 'warning',
                'title': 'High Air Pollution Alert',
                'message': f'Air quality in {city_info["name"]} is unhealthy. Consider limiting outdoor activities.',
                'timestamp': datetime.now().isoformat()
            })
        
        if aqi > 200:
            alerts.append({
                'level': 'danger',
                'title': 'Very Unhealthy Air Quality',
                'message': f'Air quality in {city_info["name"]} is very unhealthy. Avoid outdoor activities.',
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({'alerts': alerts})
    
    except Exception as e:
        app.logger.error(f"Error fetching alerts for {city}: {str(e)}")
        return jsonify({'error': 'Failed to fetch alerts'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )