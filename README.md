# March-2026---Route-700-Patronage
Patronage Data for Route 700

## Overview
This repository contains comprehensive boarding and alighting data for Gold Coast Transit Route 700 during March 2026, one of the highest patronage months. The data includes passenger movements across all stops on the route with analysis by day type (weekday, weekend, and mid-week patterns).

## 📊 Interactive Dashboard
View the full analysis on an interactive dashboard:

```bash
streamlit run dashboard.py
```

The dashboard includes:
- **Key Metrics**: Total passengers, averages by day type, unique stops
- **📈 Analysis Tab**: Patronage trends by day type
- **🗺️ Stop Details Tab**: Top boarding stops and detailed patronage breakdown
- **📅 Daily Trends Tab**: Passenger patterns by day of week and date
- **📋 Data Table Tab**: Full raw data view

## 📁 Data Files
- `data/Patronage_data.csv` - Raw patronage data with columns:
  - Direction (North/South)
  - Date (DD/MM/YYYY)
  - Boarding Stop
  - Alighting Stop
  - Passengers

## 📈 Key Insights
The dashboard provides patronage analysis across three day types:
- **Weekday (M-F)**: Average passengers per journey across all weekdays
- **Weekend**: Average passengers per journey on Saturday and Sunday
- **Tue-Thu**: Average passengers per journey specifically on Tuesday-Thursday (typically highest patronage mid-week)

This segmentation helps account for work-from-home patterns and identifies peak travel days.

## Installation
Requires Python 3.8+ with the following packages:
```bash
pip install streamlit pandas numpy plotly
```

## Usage
1. Ensure CSV data is in `data/Patronage_data.csv`
2. Run: `streamlit run dashboard.py`
3. Open browser to `http://localhost:8501` 
