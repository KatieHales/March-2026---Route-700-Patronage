import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Route 700 Patronage Dashboard", layout="wide")

# Title
st.title("🚌 Route 700 Patronage Dashboard - March 2026")
st.markdown("Patronage Data for Route 700 - Boarding and Alighting Analysis")

# Load and prepare data
def load_data():
    try:
        # Get absolute path to CSV file
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'Patronage_data.csv')
        
        df = pd.read_csv(csv_path, usecols=[0, 1, 2, 3, 4])
        df.columns = ['Direction', 'Date', 'Boarding_Stop', 'Alighting_Stop', 'Passengers']
        
        # Clean data
        df = df.dropna(subset=['Date', 'Boarding_Stop', 'Passengers'])
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
        df['DayOfWeek'] = df['Date'].dt.dayofweek
        df['DayName'] = df['Date'].dt.day_name()
        df['Passengers'] = pd.to_numeric(df['Passengers'], errors='coerce')
        df = df.dropna(subset=['Passengers'])
        df['Passengers'] = df['Passengers'].astype(int)
        
        # Day type categorization
        df['DayType'] = df['DayOfWeek'].apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
        df['IsTueThu'] = df['DayOfWeek'].isin([1, 2, 3])
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data()

if df is None:
    st.stop()

# Key Metrics
st.header("📊 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Passengers", f"{df['Passengers'].sum():,}")

with col2:
    weekday_avg = df[df['DayType'] == 'Weekday']['Passengers'].mean()
    st.metric("Avg Weekday (M-F)", f"{weekday_avg:.1f}")

with col3:
    weekend_avg = df[df['DayType'] == 'Weekend']['Passengers'].mean()
    st.metric("Avg Weekend", f"{weekend_avg:.1f}")

with col4:
    tuethu_avg = df[df['IsTueThu']]['Passengers'].mean()
    st.metric("Avg Tue-Thu", f"{tuethu_avg:.1f}")

with col5:
    unique_stops = df['Boarding_Stop'].nunique()
    st.metric("Unique Stops", unique_stops)

st.divider()

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📈 Analysis", "🗺️ Stop Details", "📅 Daily Trends", "📋 Data Table"])

with tab1:
    st.subheader("Patronage by Day Type")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart: Day type comparison
        day_type_data = df.groupby('DayType')['Passengers'].agg(['sum', 'mean', 'count'])
        day_type_data = day_type_data.reset_index()
        
        fig = px.bar(
            day_type_data,
            x='DayType',
            y='sum',
            title='Total Passengers by Day Type',
            labels={'sum': 'Total Passengers', 'DayType': 'Day Type'},
            color='DayType',
            color_discrete_map={'Weekday': '#1f77b4', 'Weekend': '#ff7f0e'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average passengers comparison
        avg_data = pd.DataFrame({
            'Day Type': ['Weekday (M-F)', 'Tue-Thu Only', 'Weekend'],
            'Avg Passengers': [
                df[df['DayType'] == 'Weekday']['Passengers'].mean(),
                df[df['IsTueThu']]['Passengers'].mean(),
                df[df['DayType'] == 'Weekend']['Passengers'].mean()
            ]
        })
        
        fig = px.bar(
            avg_data,
            x='Day Type',
            y='Avg Passengers',
            title='Average Passengers per Journey',
            labels={'Avg Passengers': 'Avg Passengers'},
            color='Avg Passengers',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Patronage by Boarding Stop")
    
    # Aggregate by stop and day type
    stop_analysis = df.groupby('Boarding_Stop').agg({
        'Passengers': ['sum', 'mean', 'count']
    }).reset_index()
    stop_analysis.columns = ['Boarding_Stop', 'Total', 'Average', 'Journeys']
    stop_analysis = stop_analysis.sort_values('Total', ascending=False)
    
    # Filter top stops
    num_stops = len(stop_analysis)
    st.info(f"Total unique boarding stops: **{num_stops}**")
    
    # Top stops chart
    st.subheader("Top 15 Boarding Stops by Total Passengers")
    top_stops = stop_analysis.head(15)
    
    fig = px.bar(
        top_stops,
        x='Total',
        y='Boarding_Stop',
        orientation='h',
        title='Top 15 Boarding Stops',
        labels={'Total': 'Total Passengers', 'Boarding_Stop': ''},
        color='Average',
        color_continuous_scale='Blues'
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed stop statistics
    st.subheader("Stop Details with Day Type Breakdown")
    
    # Calculate average by stop and day type
    stop_daytype = df.groupby(['Boarding_Stop', 'DayType'])['Passengers'].mean().reset_index()
    stop_daytype_pivot = stop_daytype.pivot(index='Boarding_Stop', columns='DayType', values='Passengers').fillna(0)
    
    # Tue-Thu average
    stop_tuethu = df[df['IsTueThu']].groupby('Boarding_Stop')['Passengers'].mean()
    stop_tuethu_df = pd.DataFrame({'Boarding_Stop': stop_tuethu.index, 'TueThu': stop_tuethu.values})
    
    # Merge all data
    stop_summary = stop_analysis.copy()
    stop_summary = stop_summary.merge(stop_daytype_pivot, left_on='Boarding_Stop', right_index=True, how='left')
    stop_summary = stop_summary.merge(stop_tuethu_df, on='Boarding_Stop', how='left')
    
    # Rename columns for clarity
    if 'Weekday' in stop_summary.columns:
        stop_summary = stop_summary.rename(columns={
            'Weekday': 'Avg_Weekday_MF',
            'Weekend': 'Avg_Weekend',
            'TueThu': 'Avg_TueThu'
        })
    
    # Display top stops with all metrics
    display_cols = ['Boarding_Stop', 'Total', 'Average', 'Journeys']
    if 'Avg_Weekday_MF' in stop_summary.columns:
        display_cols.extend(['Avg_Weekday_MF', 'Avg_Weekend', 'Avg_TueThu'])
    
    st.dataframe(
        stop_summary[display_cols].head(20).round(2),
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.subheader("Daily Patronage Trends")
    
    # Daily totals
    daily_data = df.groupby(['Date', 'DayName']).agg({
        'Passengers': ['sum', 'mean'],
        'Direction': 'count'
    }).reset_index()
    daily_data.columns = ['Date', 'DayName', 'Total', 'Average', 'Journeys']
    daily_data = daily_data.sort_values('Date')
    
    fig = px.line(
        daily_data,
        x='Date',
        y='Total',
        title='Total Passengers by Date',
        labels={'Total': 'Total Passengers', 'Date': 'Date'},
        markers=True
    )
    fig.update_traces(line=dict(color='#1f77b4', width=2), marker=dict(size=6))
    st.plotly_chart(fig, use_container_width=True)
    
    # Day of week comparison
    dow_data = df.groupby('DayName')['Passengers'].agg(['sum', 'mean']).reset_index()
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_data['DayName'] = pd.Categorical(dow_data['DayName'], categories=dow_order, ordered=True)
    dow_data = dow_data.sort_values('DayName')
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            dow_data,
            x='DayName',
            y='sum',
            title='Total Passengers by Day of Week',
            labels={'sum': 'Total Passengers', 'DayName': 'Day'},
            color='sum',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            dow_data,
            x='DayName',
            y='mean',
            title='Average Passengers by Day of Week',
            labels={'mean': 'Avg Passengers', 'DayName': 'Day'},
            color='mean',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Raw Data")
    
    # Display full dataset
    display_df = df[['Date', 'DayName', 'Direction', 'Boarding_Stop', 'Alighting_Stop', 'Passengers']].copy()
    display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%Y')
    
    st.dataframe(
        display_df.sort_values('Date'),
        use_container_width=True,
        hide_index=True
    )

# Footer
st.divider()
st.markdown("""
### About This Dashboard
- **Data Period:** March 1-31, 2026
- **Route:** Gold Coast Transit Route 700
- **Metrics:**
  - Weekday (M-F): Average passengers per journey on weekdays
  - Weekend: Average passengers per journey on Saturdays and Sundays
  - Tue-Thu: Average passengers per journey on Tuesday, Wednesday, Thursday (typically higher patronage days)
""")
