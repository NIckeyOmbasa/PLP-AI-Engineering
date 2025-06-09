"""
AirAware Configuration Settings
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # OpenAQ API settings
    OPENAQ_API_URL = 'https://api.openaq.org/v2'
    OPENAQ_API_KEY = os.getenv('OPENAQ_API_KEY', '')
    
    # Weather API settings (for enhanced forecasting)
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
    WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5'
    
    # Data refresh intervals (in seconds)
    CURRENT_DATA_REFRESH = 300  # 5 minutes
    HISTORICAL_DATA_REFRESH = 3600  # 1 hour
    FORECAST_REFRESH = 1800  # 30 minutes
    
    # Cache settings
    CACHE_TIMEOUT = 300  # 5 minutes
    CACHE_DIR = 'data/cache'
    
    # Air Quality Index thresholds (US EPA standard)
    AQI_BREAKPOINTS = {
        'pm25': [
            (0, 12.0, 0, 50),
            (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300),
            (250.5, 350.4, 301, 400),
            (350.5, 500.4, 401, 500)
        ],
        'pm10': [
            (0, 54, 0, 50),
            (55, 154, 51, 100),
            (155, 254, 101, 150),
            (255, 354, 151, 200),
            (355, 424, 201, 300),
            (425, 504, 301, 400),
            (505, 604, 401, 500)
        ],
        'o3': [
            (0, 54, 0, 50),
            (55, 70, 51, 100),
            (71, 85, 101, 150),
            (86, 105, 151, 200),
            (106, 200, 201, 300)
        ],
        'no2': [
            (0, 53, 0, 50),
            (54, 100, 51, 100),
            (101, 360, 101, 150),
            (361, 649, 151, 200),
            (650, 1249, 201, 300),
            (1250, 1649, 301, 400),
            (1650, 2049, 401, 500)
        ],
        'so2': [
            (0, 35, 0, 50),
            (36, 75, 51, 100),
            (76, 185, 101, 150),
            (186, 304, 151, 200),
            (305, 604, 201, 300),
            (605, 804, 301, 400),
            (805, 1004, 401, 500)
        ],
        'co': [
            (0, 4.4, 0, 50),
            (4.5, 9.4, 51, 100),
            (9.5, 12.4, 101, 150),
            (12.5, 15.4, 151, 200),
            (15.5, 30.4, 201, 300),
            (30.5, 40.4, 301, 400),
            (40.5, 50.4, 401, 500)
        ]
    }
    
    # AQI status messages
    AQI_STATUS = {
        (0, 50): {
            'level': 'Good',
            'color': '#00e400',
            'description': 'Air quality is satisfactory, and air pollution poses little or no risk.'
        },
        (51, 100): {
            'level': 'Moderate',
            'color': '#ffff00',
            'description': 'Air quality is acceptable for most people. However, sensitive groups may experience minor symptoms.'
        },
        (101, 150): {
            'level': 'Unhealthy for Sensitive Groups',
            'color': '#ff7e00',
            'description': 'Members of sensitive groups may experience health effects. The general public is not likely to be affected.'
        },
        (151, 200): {
            'level': 'Unhealthy',
            'color': '#ff0000',
            'description': 'Everyone may begin to experience health effects; members of sensitive groups may experience more serious effects.'
        },
        (201, 300): {
            'level': 'Very Unhealthy',
            'color': '#8f3f97',
            'description': 'Health warnings of emergency conditions. The entire population is more likely to be affected.'
        },
        (301, 500): {
            'level': 'Hazardous',
            'color': '#7e0023',
            'description': 'Health alert: everyone may experience more serious health effects.'
        }
    }
    
    # Alert thresholds
    ALERT_THRESHOLDS = {
        'warning': 100,    # Moderate to Unhealthy for SG
        'danger': 150,     # Unhealthy for SG to Unhealthy
        'emergency': 200   # Unhealthy to Very Unhealthy
    }
    
    # Supported pollutants
    POLLUTANTS = {
        'pm25': {'name': 'PM2.5', 'unit': 'μg/m³', 'description': 'Fine Particulate Matter'},
        'pm10': {'name': 'PM10', 'unit': 'μg/m³', 'description': 'Coarse Particulate Matter'},
        'o3': {'name': 'O₃', 'unit': 'μg/m³', 'description': 'Ozone'},
        'no2': {'name': 'NO₂', 'unit': 'μg/m³', 'description': 'Nitrogen Dioxide'},
        'so2': {'name': 'SO₂', 'unit': 'μg/m³', 'description': 'Sulfur Dioxide'},
        'co': {'name': 'CO', 'unit': 'mg/m³', 'description': 'Carbon Monoxide'}
    }
    
    # Rate limiting settings
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 1000
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/airaware.log'
    
    # Database settings (if using database for caching)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email settings for alerts (optional)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # SMS settings for alerts (optional)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # Application Settings
    DEFAULT_CITY = 'Nairobi'
    SUPPORTED_CITIES = [
        'Nairobi',
        'Lagos',
        'Cairo',
        'Johannesburg',
        'Addis Ababa'
    ]
    
    # Data Settings
    CACHE_DURATION = 3600  # Cache duration in seconds (1 hour)
    MAX_HISTORICAL_DAYS = 30
    FORECAST_HOURS = 24
    
    # Alert Thresholds
    AQI_THRESHOLDS = {
        'GOOD': 50,
        'MODERATE': 100,
        'UNHEALTHY_SENSITIVE': 150,
        'UNHEALTHY': 200,
        'VERY_UNHEALTHY': 300,
        'HAZARDOUS': 500
    }
    
    # Chart Settings
    CHART_COLORS = {
        'PM2.5': '#1f77b4',
        'PM10': '#ff7f0e',
        'O3': '#2ca02c',
        'NO2': '#d62728',
        'SO2': '#9467bd',
        'CO': '#8c564b'
    }
    
    # UI Settings
    THEME = {
        'primary': '#2c3e50',
        'secondary': '#34495e',
        'accent': '#3498db',
        'background': '#f5f6fa',
        'text': '#2c3e50',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#c0392b'
    }
    
    # Cache Settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    @staticmethod
    def get_aqi_status(aqi_value):
        """Get AQI status information based on value"""
        for (min_val, max_val), status in Config.AQI_STATUS.items():
            if min_val <= aqi_value <= max_val:
                return status
        
        # Default to hazardous if above all ranges
        return Config.AQI_STATUS[(301, 500)]
    
    @staticmethod
    def calculate_aqi(pollutant, concentration):
        """Calculate AQI for a specific pollutant concentration"""
        if pollutant not in Config.AQI_BREAKPOINTS:
            return None
        
        breakpoints = Config.AQI_BREAKPOINTS[pollutant]
        
        for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
            if bp_low <= concentration <= bp_high:
                # Linear interpolation formula
                aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (concentration - bp_low) + aqi_low
                return round(aqi)
        
        # If concentration is above all breakpoints, return maximum AQI
        return 500

    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    CACHE_TIMEOUT = 60  # Shorter cache for development

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    CACHE_TIMEOUT = 600  # Longer cache for production

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    CACHE_TIMEOUT = 1  # Minimal cache for testing

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}