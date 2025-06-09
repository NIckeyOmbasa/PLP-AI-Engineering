# AirAware — Urban Air Quality Monitoring Dashboard

Smarter cities through cleaner air.  
Aligned with SDG 11 — Sustainable Cities & Communities.

## Project Overview

AirAware is an open-source dashboard that visualizes real-time and historical air quality data for African cities. Our goal is to make air pollution data accessible to citizens, policymakers, and health professionals — helping to drive cleaner, healthier cities.

## Features

✅ Real-time AQI (Air Quality Index) display  
✅ Historical trend visualization for pollutants: PM2.5, PM10, CO, NO2, SO2, O3  
✅ 7-day and 30-day trend charts  
✅ AQI forecasting (next 24h, ML-based)  
✅ Public dashboard with shareable charts  
✅ "Bad air day" alerts for citizens  

## Tech Stack

### Core Libraries
- Pandas → Data collection & wrangling  
- NumPy → Data processing  
- Plotly.js → Interactive visualizations  
- Flask → Lightweight web server  
- Scikit-learn → AQI forecasting (time series models)  

### Data Source
- [OpenAQ API](https://docs.openaq.org) — Free real-time & historical air quality data

## Installation

### Prerequisites
- Python 3.9+  
- pip  

### Setup Instructions
```bash
# Clone repo
git clone https://github.com/NIckeyOmbasa/PLP-AI-Engineering/airaware.git
cd airaware

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux / macOS
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAQ API key

# Run Flask app
python app.py
```

## Project Structure
```
airaware/
├── app.py               # Flask server
├── config.py            # API keys, config variables
├── static/              # CSS, JS, images
├── templates/           # HTML templates (Jinja2)
├── notebooks/           # Jupyter notebooks for EDA & modeling
├── data/                # Local cached data (CSV/JSON)
├── utils.py             # Helper functions (API calls, data cleaning)
├── requirements.txt     # Python dependencies
└── README.md
```

## Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAQ for providing the air quality data
- All contributors who have helped shape this project

## Contact

For any queries or support, please reach out to:
- Email: [ombasanickey@gmail.com]
- GitHub: [github.com/NIckeyOmbasa]
