import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Route 700 Patronage", layout="wide")

st.title("🚌 Route 700 Patronage Dashboard - March 2026")

# Load data
df = pd.read_csv('data/Patronage_data.csv')
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
df['DayOfWeek'] = df['Date'].dt.dayofweek
df['DayName'] = df['Date'].dt.day_name()
df['DayType'] = df['DayOfWeek'].apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
df['IsTueThu'] = df['DayOfWeek'].isin([1, 2, 3])

# Key metrics
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Passengers", f"{df['Passengers'].sum():,}")
col2.metric("Avg Weekday (M-F)", f"{df[df['DayType'] == 'Weekday']['Passengers'].mean():.1f}")
col3.metric("Avg Weekend", f"{df[df['DayType'] == 'Weekend']['Passengers'].mean():.1f}")
col4.metric("Avg Tue-Thu", f"{df[df['IsTueThu']]['Passengers'].mean():.1f}")
col5.metric("Unique Stops", df['Boarding Stop'].nunique())

st.divider()

# Tabs
tab1, tab2, tab3 = st.tabs(["Daily Summary", "Top Stops", "Raw Data"])

with tab1:
    daily = df.groupby('Date')['Passengers'].sum().reset_index()
    fig = px.line(daily, x='Date', y='Passengers', title='Daily Total Passengers', markers=True)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    top_stops = df.groupby('Boarding Stop')['Passengers'].agg(['sum', 'mean']).reset_index()
    top_stops = top_stops.sort_values('sum', ascending=False).head(15)
    fig = px.bar(top_stops, y='Boarding Stop', x='sum', orientation='h', title='Top 15 Stops')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.dataframe(df[['Date', 'DayName', 'Boarding Stop', 'Alighting Stop', 'Passengers']], use_container_width=True)
