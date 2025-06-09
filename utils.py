"""
AirAware Utility Functions
Data fetching, processing, and analysis functions
"""

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AirQualityDataFetcher:
    """Class to handle air quality data fetching and processing"""
    
    def __init__(self):
        self.config = Config()
        self.base_url = self.config.OPENAQ_API_URL
        self.session = requests.Session()
        
        # Set up headers
        headers = {
            'User-Agent': 'AirAware/1.0 (https://github.com/airaware/dashboard)'
        }
        
        if self.config.OPENAQ_API_KEY:
            headers['X-API-Key'] = self.config.OPENAQ_API_KEY
        
        self.session.headers.update(headers)
    
    def fetch_current_measurements(self, lat: float, lon: float, radius: int = 10000) -> Dict:
        """Fetch current air quality measurements near coordinates"""
        try:
            url = f"{self.base_url}/measurements"
            params = {
                'coordinates': f"{lat},{lon}",
                'radius': radius,
                'order_by': 'datetime',
                'sort': 'desc',
                'limit': 100,
                'date_from': (datetime.now() - timedelta(hours=6)).isoformat(),
                'date_to': datetime.now().isoformat()
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return self._process_current_data(data['results'])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching current measurements: {e}")
            return self._get_mock_data(lat, lon)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return self._get_mock_data(lat, lon)
    
    def fetch_historical_data(self, lat: float, lon: float, days: int = 7) -> Dict:
        """Fetch historical air quality data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            url = f"{self.base_url}/measurements"
            params = {
                'coordinates': f"{lat},{lon}",
                'radius': 10000,
                'date_from': start_date.isoformat(),
                'date_to': end_date.isoformat(),
                'order_by': 'datetime',
                'sort': 'desc',
                'limit': 1000
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return self._process_historical_data(data['results'], days)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching historical data: {e}")
            return self._generate_mock_historical_data(days)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return self._generate_mock_historical_data(days)
    
    def _process_current_data(self, measurements: List[Dict]) -> Dict:
        """Process raw measurement data into structured format"""
        if not measurements:
            return self._get_mock_data(0, 0)
        
        # Group measurements by parameter
        pollutants = {}
        for measurement in measurements:
            parameter = measurement['parameter']
            value = measurement['value']
            unit = measurement['unit']
            
            if parameter not in pollutants:
                pollutants[parameter] = []
            
            pollutants[parameter].append({
                'value': value,
                'unit': unit,
                'datetime': measurement['date']['utc']
            })
        
        # Calculate averages and AQI
        processed_data = {}
        aqi_values = []
        
        for param, values in pollutants.items():
            if values:
                avg_value = np.mean([v['value'] for v in values])
                processed_data[param] = {
                    'value': round(avg_value, 2),
                    'unit': values[0]['unit'],
                    'count': len(values)
                }
                
                # Calculate AQI for this pollutant
                aqi = self.config.calculate_aqi(param, avg_value)
                if aqi:
                    aqi_values.append(aqi)
        
        # Overall AQI is the maximum of all pollutant AQIs
        overall_aqi = max(aqi_values) if aqi_values else 50
        aqi_status = self.config.get_aqi_status(overall_aqi)
        
        return {
            'aqi': overall_aqi,
            'status': aqi_status,
            'pollutants': processed_data,
            'last_updated': datetime.now().isoformat(),
            'data_source': 'OpenAQ'
        }
    
    def _process_historical_data(self, measurements: List[Dict], days: int) -> Dict:
        """Process historical measurements into time series"""
        if not measurements:
            return self._generate_mock_historical_data(days)
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(measurements)
        df['datetime'] = pd.to_datetime(df['date'].apply(lambda x: x['utc']))
        df = df.sort_values('datetime')
        
        # Group by date and parameter
        daily_data = df.groupby([df['datetime'].dt.date, 'parameter'])['value'].mean().reset_index()
        daily_data.columns = ['date', 'parameter', 'value']
        
        # Pivot to get parameters as columns
        pivot_data = daily_data.pivot(index='date', columns='parameter', values='value')
        pivot_data = pivot_data.fillna(method='ffill').fillna(method='bfill')
        
        # Calculate daily AQI
        daily_aqi = []
        for date, row in pivot_data.iterrows():
            aqi_values = []
            for param, value in row.items():
                if not pd.isna(value):
                    aqi = self.config.calculate_aqi(param, value)
                    if aqi:
                        aqi_values.append(aqi)
            
            daily_aqi.append({
                'date': date.strftime('%Y-%m-%d'),
                'aqi': max(aqi_values) if aqi_values else 50
            })
        
        return {
            'daily_aqi': daily_aqi,
            'pollutant_trends': pivot_data.to_dict('records'),
            'period': f"{days} days",
            'data_source': 'OpenAQ'
        }
    
    def _get_mock_data(self, lat: float, lon: float) -> Dict:
        """Generate mock data when API is unavailable"""
        # Simulate realistic values based on typical African city pollution levels
        base_pm25 = np.random.normal(45, 15)  # Higher PM2.5 typical for African cities
        base_pm10 = base_pm25 * 1.5 + np.random.normal(0, 10)
        
        pollutants = {
            'pm25': {'value': max(0, round(base_pm25, 1)), 'unit': 'µg/m³', 'count': 5},
            'pm10': {'value': max(0, round(base_pm10, 1)), 'unit': 'µg/m³', 'count': 5},
            'no2': {'value': max(0, round(np.random.normal(35, 10), 1)), 'unit': 'µg/m³', 'count': 3},
            'so2': {'value': max(0, round(np.random.normal(20, 8), 1)), 'unit': 'µg/m³', 'count': 3},
            'co': {'value': max(0, round(np.random.normal(2.5, 0.8), 1)), 'unit': 'mg/m³', 'count': 2},
            'o3': {'value': max(0, round(np.random.normal(55, 15), 1)), 'unit': 'µg/m³', 'count': 4}
        }
        
        # Calculate AQI
        aqi_values = []
        for param, data in pollutants.items():
            aqi = self.config.calculate_aqi(param, data['value'])
            if aqi:
                aqi_values.append(aqi)
        
        overall_aqi = max(aqi_values) if aqi_values else 75
        aqi_status = self.config.get_aqi_status(overall_aqi)
        
        return {
            'aqi': overall_aqi,
            'status': aqi_status,
            'pollutants': pollutants,
            'last_updated': datetime.now().isoformat(),
            'data_source': 'Simulated (API unavailable)'
        }
    
    def _generate_mock_historical_data(self, days: int) -> Dict:
        """Generate mock historical data"""
        dates = []
        aqi_values = []
        
        base_aqi = np.random.normal(85, 20)  # Typical moderate AQI
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            dates.append(date.strftime('%Y-%m-%d'))
            
            # Add some trend and randomness
            trend = np.sin(i * 0.1) * 10  # Slight sinusoidal trend
            noise = np.random.normal(0, 15)
            daily_aqi = max(0, min(300, base_aqi + trend + noise))
            aqi_values.append(round(daily_aqi))
        
        daily_aqi = [{'date': d, 'aqi': a} for d, a in zip(dates, aqi_values)]
        
        return {
            'daily_aqi': daily_aqi,
            'period': f"{days} days",
            'data_source': 'Simulated (API unavailable)'
        }

class AirQualityForecaster:
    """Class to generate air quality forecasts"""
    
    def __init__(self):
        self.config = Config()
    
    def generate_forecast(self, historical_data: List[Dict], hours: int = 24) -> List[Dict]:
        """Generate air quality forecast using machine learning"""
        try:
            if len(historical_data) < 3:
                return self._generate_simple_forecast(hours)
            
            # Prepare data for ML model
            dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in historical_data]
            aqi_values = [d['aqi'] for d in historical_data]
            
            # Convert dates to numerical features
            X = np.array([(d - dates[0]).days for d in dates]).reshape(-1, 1)
            y = np.array(aqi_values)
            
            # Use polynomial features for better trend capture
            poly_features = PolynomialFeatures(degree=2)
            X_poly = poly_features.fit_transform(X)
            
            # Train model
            model = LinearRegression()
            model.fit(X_poly, y)
            
            # Generate forecast
            forecast = []
            last_date = dates[-1]
            
            for hour in range(1, hours + 1):
                forecast_date = last_date + timedelta(hours=hour)
                forecast_aqi = model.predict([[forecast_date.strftime('%Y-%m-%d')]])
                forecast.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'aqi': round(forecast_aqi[0][0], 2)
                })
            
            return forecast
        except Exception as e:
            logger.error(f"Error in forecast generation: {e}")
            return []

class AirQualityData:
    def __init__(self, api_key: str):
        """Initialize AirQualityData with OpenAQ API key."""
        self.api_key = api_key
        self.base_url = "https://api.openaq.org/v2"
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def get_latest_measurements(self, city: str) -> pd.DataFrame:
        """Fetch latest air quality measurements for a specific city."""
        endpoint = f"{self.base_url}/latest"
        params = {
            "city": city,
            "limit": 100
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process and clean the data
            measurements = []
            for result in data.get("results", []):
                for measurement in result.get("measurements", []):
                    measurements.append({
                        "parameter": measurement.get("parameter"),
                        "value": measurement.get("value"),
                        "unit": measurement.get("unit"),
                        "timestamp": measurement.get("lastUpdated")
                    })
            
            return pd.DataFrame(measurements)
        except Exception as e:
            print(f"Error fetching latest measurements: {str(e)}")
            return pd.DataFrame()

    def get_historical_data(self, city: str, days: int = 30) -> pd.DataFrame:
        """Fetch historical air quality data for a specific city."""
        endpoint = f"{self.base_url}/measurements"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "city": city,
            "date_from": start_date.strftime("%Y-%m-%d"),
            "date_to": end_date.strftime("%Y-%m-%d"),
            "limit": 1000
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process and clean the data
            measurements = []
            for result in data.get("results", []):
                measurements.append({
                    "parameter": result.get("parameter"),
                    "value": result.get("value"),
                    "unit": result.get("unit"),
                    "timestamp": result.get("date", {}).get("utc")
                })
            
            df = pd.DataFrame(measurements)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            return df
        except Exception as e:
            print(f"Error fetching historical data: {str(e)}")
            return pd.DataFrame()

    def calculate_aqi(self, measurements: pd.DataFrame) -> float:
        """Calculate Air Quality Index from measurements."""
        # AQI calculation based on EPA standards
        aqi_breakpoints = {
            "PM2.5": [(0, 12, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150),
                      (55.5, 150.4, 151, 200), (150.5, 250.4, 201, 300), (250.5, 500.4, 301, 500)],
            "PM10": [(0, 54, 0, 50), (55, 154, 51, 100), (155, 254, 101, 150),
                     (255, 354, 151, 200), (355, 424, 201, 300), (425, 604, 301, 500)],
            "O3": [(0, 54, 0, 50), (55, 70, 51, 100), (71, 85, 101, 150),
                   (86, 105, 151, 200), (106, 200, 201, 300), (201, 500, 301, 500)]
        }
        
        aqi_values = []
        for param in ["PM2.5", "PM10", "O3"]:
            param_data = measurements[measurements["parameter"] == param]
            if not param_data.empty:
                value = param_data["value"].mean()
                for low, high, aqi_low, aqi_high in aqi_breakpoints[param]:
                    if low <= value <= high:
                        aqi = ((aqi_high - aqi_low) / (high - low)) * (value - low) + aqi_low
                        aqi_values.append(aqi)
                        break
        
        return max(aqi_values) if aqi_values else 0

    def create_trend_chart(self, data: pd.DataFrame, parameter: str) -> go.Figure:
        """Create an interactive trend chart using Plotly."""
        fig = go.Figure()
        
        # Filter data for the specified parameter
        param_data = data[data["parameter"] == parameter]
        
        # Create line plot
        fig.add_trace(go.Scatter(
            x=param_data["timestamp"],
            y=param_data["value"],
            mode="lines+markers",
            name=parameter,
            line=dict(width=2)
        ))
        
        # Update layout
        fig.update_layout(
            title=f"{parameter} Trend Over Time",
            xaxis_title="Date",
            yaxis_title="Value",
            template="plotly_white",
            hovermode="x unified"
        )
        
        return fig

    def predict_aqi(self, historical_data: pd.DataFrame, forecast_hours: int = 24) -> pd.DataFrame:
        """Predict future AQI values using machine learning."""
        try:
            # Prepare features
            df = historical_data.copy()
            df["hour"] = df["timestamp"].dt.hour
            df["day"] = df["timestamp"].dt.day
            df["month"] = df["timestamp"].dt.month
            
            # Create lag features
            for lag in [1, 2, 3, 6, 12, 24]:
                df[f"lag_{lag}"] = df["value"].shift(lag)
            
            # Drop NaN values
            df = df.dropna()
            
            # Prepare training data
            X = df[["hour", "day", "month"] + [f"lag_{i}" for i in [1, 2, 3, 6, 12, 24]]]
            y = df["value"]
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Prepare future data
            last_timestamp = df["timestamp"].max()
            future_timestamps = pd.date_range(
                start=last_timestamp + timedelta(hours=1),
                periods=forecast_hours,
                freq="H"
            )
            
            future_data = pd.DataFrame({
                "timestamp": future_timestamps,
                "hour": future_timestamps.hour,
                "day": future_timestamps.day,
                "month": future_timestamps.month
            })
            
            # Add lag features for future predictions
            for lag in [1, 2, 3, 6, 12, 24]:
                future_data[f"lag_{lag}"] = df["value"].iloc[-lag:].values
            
            # Make predictions
            predictions = model.predict(future_data[["hour", "day", "month"] + [f"lag_{i}" for i in [1, 2, 3, 6, 12, 24]]])
            
            # Create prediction DataFrame
            forecast_df = pd.DataFrame({
                "timestamp": future_timestamps,
                "value": predictions,
                "parameter": "forecast"
            })
            
            return forecast_df
        except Exception as e:
            print(f"Error in AQI prediction: {str(e)}")
            return pd.DataFrame()

    def generate_alert(self, aqi: float) -> Dict[str, str]:
        """Generate air quality alert based on AQI value."""
        if aqi <= 50:
            return {
                "level": "Good",
                "message": "Air quality is satisfactory, and air pollution poses little or no risk.",
                "color": "green"
            }
        elif aqi <= 100:
            return {
                "level": "Moderate",
                "message": "Air quality is acceptable. However, there may be a risk for some people.",
                "color": "yellow"
            }
        elif aqi <= 150:
            return {
                "level": "Unhealthy for Sensitive Groups",
                "message": "Members of sensitive groups may experience health effects.",
                "color": "orange"
            }
        elif aqi <= 200:
            return {
                "level": "Unhealthy",
                "message": "Everyone may begin to experience health effects.",
                "color": "red"
            }
        elif aqi <= 300:
            return {
                "level": "Very Unhealthy",
                "message": "Health warnings of emergency conditions.",
                "color": "purple"
            }
        else:
            return {
                "level": "Hazardous",
                "message": "Health alert: everyone may experience more serious health effects.",
                "color": "maroon"
            }