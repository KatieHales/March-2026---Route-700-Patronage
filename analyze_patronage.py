import pandas as pd
import numpy as np
from datetime import datetime
import folium
from folium import plugins
import webbrowser
import os

# Load the data
df = pd.read_csv('data/Patronage_data.csv', usecols=[0, 1, 2, 3, 4])
df.columns = ['Direction', 'Date', 'Boarding_Stop', 'Alighting_Stop', 'Passengers']

# Clean data - remove rows with NaN values in key columns
df = df.dropna(subset=['Date', 'Boarding_Stop', 'Passengers'])

# Convert date to datetime
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

# Extract day of week (0=Monday, 6=Sunday)
df['DayOfWeek'] = df['Date'].dt.dayofweek
df['DayName'] = df['Date'].dt.day_name()

# Convert passengers to numeric
df['Passengers'] = pd.to_numeric(df['Passengers'], errors='coerce')
df = df.dropna(subset=['Passengers'])
df['Passengers'] = df['Passengers'].astype(int)

# Categorize by day type
df['DayType'] = df['DayOfWeek'].apply(
    lambda x: 'Weekend' if x >= 5 else 'Weekday'
)

df['IsTueThu'] = df['DayOfWeek'].isin([1, 2, 3])  # Tuesday=1, Wednesday=2, Thursday=3

print("\n=== ROUTE 700 MARCH 2026 PATRONAGE ANALYSIS ===\n")
print(f"Data range: {df['Date'].min().date()} to {df['Date'].max().date()}")
print(f"Total records: {len(df)}")
print(f"Total passengers: {df['Passengers'].sum()}")

# Aggregate by boarding stop and day type
print("\n--- PATRONAGE BY DAY TYPE ---")

# Weekday vs Weekend
weekday_avg = df[df['DayType'] == 'Weekday'].groupby('Boarding_Stop')['Passengers'].mean()
weekend_avg = df[df['DayType'] == 'Weekend'].groupby('Boarding_Stop')['Passengers'].mean()

# Weekday (Mon-Fri) vs Tue-Thu specifically
monthu_avg = df[df['DayOfWeek'].isin([0, 1, 2, 3, 4])].groupby('Boarding_Stop')['Passengers'].mean()  # M-F
tuethu_avg = df[df['IsTueThu']].groupby('Boarding_Stop')['Passengers'].mean()

# Create summary table
summary = pd.DataFrame({
    'Boarding_Stop': weekday_avg.index,
    'Avg_Weekday_MF': weekday_avg.values,
    'Avg_Weekend': weekend_avg.values,
    'Avg_TueThu': tuethu_avg.values
}).fillna(0)

# Add total passengers per stop
total_by_stop = df.groupby('Boarding_Stop')['Passengers'].sum()
summary['Total_Passengers'] = summary['Boarding_Stop'].map(total_by_stop)

# Sort by total passengers descending
summary = summary.sort_values('Total_Passengers', ascending=False)

# Round to 2 decimal places
summary = summary.round(2)

print("\nTop 20 Boarding Stops by Total Passengers:")
print(summary.head(20).to_string(index=False))

# Save to CSV
summary.to_csv('data/patronage_summary.csv', index=False)
print(f"\n✓ Summary saved to 'data/patronage_summary.csv'")

# Overall statistics
print("\n--- OVERALL STATISTICS ---")
print(f"Average passengers per weekday journey: {df[df['DayType'] == 'Weekday']['Passengers'].mean():.2f}")
print(f"Average passengers per weekend journey: {df[df['DayType'] == 'Weekend']['Passengers'].mean():.2f}")
print(f"Average passengers per Tue-Thu journey: {df[df['IsTueThu']]['Passengers'].mean():.2f}")

print(f"\nWeekday total: {df[df['DayType'] == 'Weekday']['Passengers'].sum()}")
print(f"Weekend total: {df[df['DayType'] == 'Weekend']['Passengers'].sum()}")

print("\n--- ASSESSMENT ---")
num_stops = len(summary)
print(f"Total unique boarding stops: {num_stops}")

if num_stops > 50:
    print("⚠ With {} stops, a map may be cluttered.".format(num_stops))
    print("   → Recommend: Table view (CSV file created above)")
else:
    print(f"✓ With {num_stops} stops, a map should be manageable.")
    print("   → Both map and table can work well")

print("\n" + "="*50)
